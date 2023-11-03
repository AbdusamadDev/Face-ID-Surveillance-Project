import asyncio
import json
import logging
import time
import tracemalloc
from datetime import datetime

import websockets
from geopy.distance import geodesic
from imutils.video import VideoStream

from models import Database
from path import absolute_path
from train import FaceTrainer
from utils import save_screenshot, host_address

tracemalloc.start()

logging.basicConfig(level=logging.INFO)


class WebSocketManager:
    def __init__(self):
        self.web_clients = set()
        self.apk_clients = set()
        self.locations = {}

    async def register(self, websocket, data):
        if data["state"] == "apk":
            self.apk_clients.add(websocket)
            self.locations[websocket] = (data["latitude"], data["longitude"])
        else:
            self.web_clients.add(websocket)
        logging.info(
            f"Registered a {data['state']} client. Total web: {len(self.web_clients)}, apk: {len(self.apk_clients)}"
        )

    async def unregister(self, websocket):
        if websocket in self.apk_clients:
            self.apk_clients.remove(websocket)
            del self.locations[websocket]
        elif websocket in self.web_clients:
            self.web_clients.remove(websocket)
        logging.info(
            f"Unregistered a client. Remaining web: {len(self.web_clients)}, apk: {len(self.apk_clients)}"
        )

    async def send_to_all(self, message):
        for web_client in self.web_clients:
            if web_client.open:
                await web_client.send(message)

    async def send_to_nearest_client(self, message):
        nearest_client, _ = self.find_nearest_client()
        if nearest_client and nearest_client.open:
            await nearest_client.send(
                json.dumps({"event": "nearest_client", "context": message})
            )

    async def print_client_locations(self):
        nearest_client, nearest_distance = self.find_nearest_client()
        if nearest_client is not None:
            msg = f"Nearest client is at {nearest_client.remote_address} with distance {nearest_distance} km"
            print(msg)
            await self.send_to_nearest_client(
                json.dumps({"event": "nearest_client", "message": msg})
            )

    def find_nearest_client(self):
        camera_location = (41.0649, 71.4782)
        nearest_distance = float("inf")
        nearest_client = None
        for ws, location in self.locations.items():
            if not isinstance(location, tuple) or len(location) != 2:
                logging.error(type(location))
                logging.error(f"Invalid location data: {location}")
                continue

            try:
                lat, long = float(location[0]), float(location[1])
            except ValueError:
                logging.error(f"Invalid coordinates: {location}")
                continue

            location = (lat, long)
            distance = geodesic(camera_location, location).kilometers

            if distance < nearest_distance:
                nearest_distance = distance
                nearest_client = ws

        return nearest_client, nearest_distance


class FaceRecognition:
    def __init__(self, main_stream):
        self.index = main_stream.index
        self.known_face_names = main_stream.known_face_names
        self.face_model = main_stream.face_model

    def process_frame(self, frame):
        faces = self.face_model.get(frame)
        detected_faces = set()
        for face in faces:
            result = self.process_face(face)
            if result:
                detected_faces.add(result)
        return detected_faces

    async def process_face(self, face):
        embedding = face.embedding
        similarity, index = self.index.search(embedding.reshape(1, -1), 1)
        if similarity[0, 0] < 500:
            return self.known_face_names[index[0, 0]]
        return None


class AlertManager:
    def __init__(self, websocket_manager):
        self.websocket_manager = websocket_manager
        self.last_alert_time = {}
        self.face_last_seen = {}
        self.database = Database()

    async def handle_alert(self, detected_face, frame, url):
        now = datetime.now()
        last_alert_time = self.last_alert_time.get(detected_face, datetime.min)
        time_since_last_alert = (now - last_alert_time).total_seconds()

        time_since_last_seen = (
                now - self.face_last_seen.get(detected_face, datetime.min)
        ).total_seconds()

        if time_since_last_seen > 5 and time_since_last_alert > 3:
            await self.send_alert(detected_face, url)
            year, month, day = datetime.now().timetuple()[:3]
            path = (
                f"../media/screenshots/criminals/{detected_face}/{year}/{month}/{day}"
            )
            save_screenshot(frame, path=path)
            self.last_alert_time[detected_face] = now

        self.face_last_seen[detected_face] = now

    async def send_alert(self, detected_face, url):
        details = self.database.get_details(detected_face)
        camera = self.database.get_camera(url)
        camera_details = camera or None
        camera_context = {
            "id": camera_details[0],
            "name": camera_details[1],
            "url": camera_details[2],
            "longitude": camera_details[3],
            "latitude": camera_details[4],
            "image": host_address + "/" + camera_details[-1]
        }
        context = {
            "id": details[0],
            "first_name": details[1],
            "last_name": details[2],
            "middle_name": details[-1],
            "age": details[3],
            "description": details[4],
            "date_joined": str(details[5]),
            "url": url,
            "camera": camera_context,
        }

        print("Context: ", context)
        await self.websocket_manager.send_to_all(
            json.dumps(context)
        )
        await self.websocket_manager.send_to_nearest_client(
            json.dumps({"event": "nearest_client", "context": context})
        )

        # camera_location = (41.0000, 71.6682)
        # await self.websocket_manager.print_client_locations()


class MainStream:
    def __init__(self, root_dir, camera_urls):
        self.websocket_manager = WebSocketManager()
        self.urls = camera_urls
        self.trainer = FaceTrainer(root_dir)
        self.index = self.trainer.index
        self.known_face_names = self.trainer.known_face_names
        self.face_model = self.trainer.face_model
        self.alert_manager = AlertManager(self.websocket_manager)
        self.face_recognition = FaceRecognition(self)

    async def detect_and_process_faces(self, frame, url):
        faces = self.face_model.get(frame)
        detected_faces = await asyncio.gather(
            *(self.face_recognition.process_face(face) for face in faces)
        )
        detected_faces = set(filter(None, detected_faces))

        for result in detected_faces:
            await self.alert_manager.handle_alert(result, frame, url)

    async def continuous_stream_faces(self, url):
        cap = VideoStream(url).start()
        screenshot_interval = 5  # Interval to take a screenshot in seconds
        last_screenshot_time = time.time()
        try:
            while True:
                frame = cap.read()
                if frame is None:
                    continue

                current_time = time.time()
                if current_time - last_screenshot_time >= screenshot_interval:
                    save_screenshot(frame, path="../media/screenshots/suspends")
                    last_screenshot_time = current_time

                await self.detect_and_process_faces(frame, url)
        except (KeyboardInterrupt, websockets.exceptions.ConnectionClosedError):
            logging.info(f"Stream {url} terminated.")
        finally:
            cap.stop()

    async def multiple_cameras(self):
        tasks = [self.continuous_stream_faces(url) for url in self.urls]
        await asyncio.gather(*tasks)


async def websocket_server(websocket, path):
    manager = stream.websocket_manager
    try:
        logging.info("Attempt to connect received.")
        message = await websocket.recv()
        data = json.loads(message)
        await manager.register(websocket, data)

        while True:
            # Here you can add any additional message handling logic if needed
            await asyncio.sleep(10)

    except websockets.exceptions.ConnectionClosedError as e:
        logging.error(f"Connection closed: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}")
    finally:
        await manager.unregister(websocket)


if __name__ == "__main__":
    # camera_urls = ["http://192.168.1.152:5000/video"]
    database = Database()
    camera_urls = database.get_camera_urls()
    stream = MainStream(absolute_path + "/criminals/", camera_urls)
    loop = asyncio.get_event_loop()
    print("Starting websocket server")
    loop.run_until_complete(websockets.serve(websocket_server, "0.0.0.0", 5000))
    print("Websocket server started")

    loop.run_until_complete(stream.multiple_cameras())
