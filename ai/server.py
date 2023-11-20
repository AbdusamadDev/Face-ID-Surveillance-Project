import asyncio
import json
import tracemalloc
from datetime import datetime
import logging
import websockets
from geopy.distance import geodesic
from imutils.video import VideoStream
import os

from models import Database
from path import abs_path
from train import FaceTrainer
from utils import save_screenshot, host_address

tracemalloc.start()
logging.basicConfig(level=logging.DEBUG)


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

    async def unregister(self, websocket):
        # Removing the websocket and updating locations if it's an APK client
        if websocket in self.apk_clients:
            self.apk_clients.remove(websocket)
            del self.locations[websocket]
        elif websocket in self.web_clients:
            self.web_clients.remove(websocket)

    async def send_to_nearest_client(self, message, camera_location):
        self.refresh_clients()
        nearest_client, _ = self.find_nearest_client(camera_location)
        if nearest_client:
            if nearest_client.open:
                await nearest_client.send(message)

    async def send_to_all(self, message):
        for web_client in self.web_clients:
            if web_client.open:
                await web_client.send(message)

    def find_nearest_client(self, camera_location):
        nearest_distance = float("inf")
        nearest_client = None
        for ws, location in self.locations.items():
            if not isinstance(location, tuple) or len(location) != 2:
                continue

            try:
                lat, long = float(location[0]), float(location[1])
            except ValueError:
                continue

            location = (lat, long)
            distance = geodesic(camera_location, location).kilometers

            if distance < nearest_distance:
                nearest_distance = distance
                nearest_client = ws

        return nearest_client, nearest_distance

    def refresh_clients(self):
        for ws in list(self.apk_clients):
            if not ws.open:
                self.apk_clients.remove(ws)


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
            image_name = save_screenshot(frame, path=path, camera_url=url)
            camera_object = self.database.get_camera(url)
            if camera_object:
                camera_object = camera_object.get("id")
            self.database.insert_records(
                image=f"{host_address}{image_name[2:]}",
                date_recorded=datetime.now(),
                criminal=int(detected_face),
                camera=camera_object
            )
            self.last_alert_time[detected_face] = now

        self.face_last_seen[detected_face] = now

    async def send_alert(self, detected_face, url):
        details = self.database.get_details(detected_face)
        camera = self.database.get_camera(url)
        camera["image"] = host_address + "/media/" + camera.get("image")
        details["date_created"] = str(details.get('date_created'))
        details["image"] = host_address + "/media/criminals/" + str(detected_face) + "/" + "main.jpg"
        await self.websocket_manager.send_to_all(
            json.dumps({"identity": details, "camera": camera})
        )
        await self.websocket_manager.send_to_nearest_client(
            json.dumps({"identity": details, "camera": camera}),
            camera_location=(camera["longitude"], camera["latitude"])
        )
        print({"identity": details, "camera": camera})


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
        """ Captures frames and sends them to the processing queue. """
        cap = VideoStream(url).start()
        while True:
            frame = cap.read()
            if frame is not None:
                await self.processing_queue.put((frame, url))
            await asyncio.sleep(0.1)

    async def process_frames(self):
        """ Processes frames from all cameras. """
        while True:
            frame, url = await self.processing_queue.get()
            self.face_recognition.current_frame = frame
            faces = self.face_model.get(frame)
            tasks = [self.face_recognition.process_face(face) for face in faces]
            results = await asyncio.gather(*tasks)
            for name in results:
                if name is not None:
                    await self.alert_manager.handle_alert(frame=frame, detected_face=name, url=url)

    async def reload_face_encodings_periodically(self):
        while True:
            print("Reloading face encodings...")
            self.index, self.known_face_names = self.trainer.load_face_encodings(self.root_dir)
            self.face_recognition.index, self.face_recognition.known_face_names = self.trainer.load_face_encodings(
                self.root_dir)
            print("Length of face encodings: ", len(self.face_recognition.known_face_names))
            await self.update_camera_streams()
            await asyncio.sleep(10)

    async def start_camera_streams(self):
        """Start frame capture tasks for all cameras and the central processing task."""
        tasks = [asyncio.create_task(self.capture_and_send_frames(url)) for url in self.urls]
        tasks.append(asyncio.create_task(self.process_frames()))
        await asyncio.gather(*tasks)

    async def update_camera_streams(self):
        new_urls = self.database.get_camera_urls()
        added_urls = set(new_urls) - set(self.urls)

        if added_urls:
            print(f"New cameras added: {added_urls}")
            for url in added_urls:
                asyncio.create_task(self.capture_and_send_frames(url))
            self.urls.extend(added_urls)


async def websocket_server(websocket, path):
    manager = stream.websocket_manager
    try:
        message = await websocket.recv()
        data = json.loads(message) or None
        await manager.register(websocket, data)

        while True:
            # Here you can add any additional message handling logic if needed
            await asyncio.sleep(10)

    except websockets.exceptions.ConnectionClosedError as e:
        await manager.unregister(websocket)
    except json.JSONDecodeError as e:
        await manager.unregister(websocket)
    finally:
        await manager.unregister(websocket)


# Function to list all image paths in a specific directory
def list_image_paths(directory):
    relative_paths = [os.path.join(directory, f) for f in os.listdir(directory) if
                      os.path.isfile(os.path.join(directory, f))]
    absolute_paths = [path.replace('../', host_address + "/", 1) for path in relative_paths]
    return absolute_paths


async def send_image_paths(websocket, path):
    sent_image_paths = set()
    connection_time = datetime.now()
    screenshots_dir = "../media/screenshots/suspends/"

    while True:
        current_image_files = set(
            f for f in os.listdir(screenshots_dir) if os.path.isfile(os.path.join(screenshots_dir, f)))
        current_image_paths = {os.path.join(screenshots_dir, f) for f in current_image_files}
        new_paths = current_image_paths - sent_image_paths
        for file_path in new_paths:
            creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
            if creation_time > connection_time:
                image_name = os.path.basename(file_path)
                camera_url = image_name.split('|')[-1].rstrip('.jpg')
                camera_object = database.get_by_similar(camera_url)
                image_url = file_path.replace('../', host_address + "/", 1)
                camera_object["image"] = host_address + "/media/" + camera_object.get("image")
                message = {"image_path": image_url, "camera_object": camera_object}
                await websocket.send(json.dumps(message))
                sent_image_paths.add(file_path)
        await asyncio.sleep(5)


async def image_path_server(websocket, path):
    consumer_task = asyncio.ensure_future(send_image_paths(websocket, path))
    done, pending = await asyncio.wait([consumer_task], return_when=asyncio.FIRST_COMPLETED)
    for task in pending:
        task.cancel()


async def main():
    ws_server = await websockets.serve(websocket_server, "0.0.0.0", 5000)
    camera_streams_task = asyncio.create_task(stream.start_camera_streams())
    reload_encodings_task = asyncio.create_task(stream.reload_face_encodings_periodically())
    await asyncio.gather(
        ws_server.wait_closed(),
        camera_streams_task,
        reload_encodings_task,  # Include the new task here
    )


if __name__ == "__main__":
    database = Database()
    urls = database.get_camera_urls()
    stream = MainStream(abs_path() + "media/criminals", urls)
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
