import asyncio
import json
import tracemalloc
from datetime import datetime
import logging
import websockets
from urllib.parse import urlparse
from imutils.video import VideoStream
import cv2
import os

from models import Database
from path import abs_path
from train import FaceTrainer
from utils import host_address
from face_recognition import FaceRecognition
from socket_manager import WebSocketManager
from alert_manager import AlertManager

tracemalloc.start()
logging.basicConfig(level=logging.DEBUG)


class MainStream:
    def __init__(self, root_dir, camera_urls):
        self.root_dir = root_dir
        self.database = Database()
        self.websocket_manager = WebSocketManager()
        self.urls = camera_urls
        self.trainer = FaceTrainer(root_dir)
        self.index = self.trainer.index
        self.known_face_names = self.trainer.known_face_names
        self.face_model = self.trainer.face_model
        self.alert_manager = AlertManager(self.websocket_manager)
        self.face_recognition = FaceRecognition(self)
        self.processing_queue = asyncio.Queue()  # Queue for processing frames

    async def capture_and_send_frames(self, url):
        """Captures frames and sends them to the processing queue."""
        cap = VideoStream(url).start()
        while True:
            frame = cap.read()
            if frame is not None:
                await self.processing_queue.put((frame, url))
            await asyncio.sleep(0.1)

    async def process_frames(self):
        """Processes frames from all cameras."""
        last_screenshot_time = datetime.now()
        screenshot_interval = 5
        while True:
            frame, url = await self.processing_queue.get()
            self.face_recognition.current_frame = frame
            current_time = datetime.now()
            faces = self.face_model.get(frame)
            tasks = [self.face_recognition.process_face(face) for face in faces]
            results = await asyncio.gather(*tasks)
            for name in results:
                if name is not None:
                    await self.alert_manager.handle_alert(
                        frame=frame, detected_face=name, url=url
                    )
            if (
                current_time - last_screenshot_time
            ).total_seconds() >= screenshot_interval:
                self.save_screenshot(frame, url, current_time)
                last_screenshot_time = current_time

    async def reload_face_encodings_periodically(self):
        while True:
            self.index, self.known_face_names = self.trainer.load_face_encodings(
                self.root_dir
            )
            (
                self.face_recognition.index,
                self.face_recognition.known_face_names,
            ) = self.trainer.load_face_encodings(self.root_dir)
            await asyncio.sleep(60)

    async def start_camera_streams(self):
        """Start frame capture tasks for all cameras and the central processing task."""
        tasks = [
            asyncio.create_task(self.capture_and_send_frames(url)) for url in self.urls
        ]
        tasks.append(asyncio.create_task(self.process_frames()))
        await asyncio.gather(*tasks)

    async def reconnect_cameras_periodically(self, interval=60):
        """Reconnects to all cameras one by one at specified intervals."""
        while True:
            for url in database.get_camera_urls():
                asyncio.create_task(self.capture_and_send_frames(url))
            await asyncio.sleep(interval)

    def save_screenshot(self, frame, url, timestamp):
        """Saves a screenshot with a specific naming format, including only the IP address from the URL."""
        parsed_url = urlparse(url)
        ip_address = parsed_url.hostname  # Extracts the hostname/IP address

        formatted_time = timestamp.strftime("%Y-%m-%d|%H-%M-%S")
        filename = f"{formatted_time}|{ip_address}.jpg"
        directory = os.path.join("../media/screenshots/suspends")
        os.makedirs(directory, exist_ok=True)  # Ensure directory exists
        filepath = os.path.join(directory, filename)
        cv2.imwrite(filepath, frame)


async def websocket_server(websocket, path):
    manager = stream.websocket_manager
    try:
        message = await websocket.recv()
        data = json.loads(message)
        token = data.get("token", None)
        if token is not None:
            if database.is_authenticated(token):
                await manager.register(websocket, data)
            else:
                await websocket.send(json.dumps({"msg": "Invalid token provided!"}))
                await manager.unregister(websocket)
        else:
            await websocket.send(json.dumps({"msg": "Token is not provided!"}))
            await manager.unregister(websocket)
        while True:
            await asyncio.sleep(1000)
    except websockets.exceptions.ConnectionClosedError as e:  # type: ignore
        await manager.unregister(websocket)
    except json.JSONDecodeError as e:
        await manager.unregister(websocket)
    finally:
        await manager.unregister(websocket)


def list_image_paths(directory):
    relative_paths = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f))
    ]
    absolute_paths = [
        path.replace("../", host_address + "/", 1) for path in relative_paths
    ]
    return absolute_paths


async def send_image_paths(websocket, path):
    sent_image_paths = set()
    connection_time = datetime.now()
    screenshots_dir = "../media/screenshots/suspends/"

    while True:
        current_image_files = set(
            f
            for f in os.listdir(screenshots_dir)
            if os.path.isfile(os.path.join(screenshots_dir, f))
        )
        current_image_paths = {
            os.path.join(screenshots_dir, f) for f in current_image_files
        }
        new_paths = current_image_paths - sent_image_paths
        for file_path in new_paths:
            creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
            if creation_time > connection_time:
                image_name = os.path.basename(file_path)
                camera_url = image_name.split("|")[-1].rstrip(".jpg")
                camera_object = database.get_by_similar(camera_url)
                image_url = file_path.replace("../", host_address + "/", 1)
                camera_object["image"] = (
                    host_address + "/media/" + camera_object.get("image")
                )
                message = {"image_path": image_url, "camera_object": camera_object}
                await websocket.send(json.dumps(message))
                sent_image_paths.add(file_path)
        await asyncio.sleep(5)


async def image_path_server(websocket, path):
    consumer_task = asyncio.ensure_future(send_image_paths(websocket, path))
    done, pending = await asyncio.wait(
        [consumer_task], return_when=asyncio.FIRST_COMPLETED
    )
    for task in pending:
        task.cancel()


async def main():
    ws_server = await websockets.serve(websocket_server, "0.0.0.0", 5000)
    img_server = await websockets.serve(image_path_server, "0.0.0.0", 5678)
    camera_streams_task = asyncio.create_task(stream.start_camera_streams())
    reload_encodings_task = asyncio.create_task(
        stream.reload_face_encodings_periodically()
    )
    camera_reconnection = asyncio.create_task(stream.reconnect_cameras_periodically())
    await asyncio.gather(
        ws_server.wait_closed(),
        img_server.wait_closed(),
        camera_streams_task,
        reload_encodings_task,
        camera_reconnection,
    )


if __name__ == "__main__":
    database = Database()
    urls = database.get_camera_urls()
    stream = MainStream(abs_path() + "media/criminals", urls)
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
