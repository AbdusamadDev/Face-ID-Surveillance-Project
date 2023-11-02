import time
import logging
import cv2
from datetime import datetime
from imutils.video import VideoStream
from train import FaceTrainer
import asyncio
import os
import websockets
import json
from path import absolute_path
from geopy.distance import geodesic
import tracemalloc

tracemalloc.start()


logging.basicConfig(level=logging.INFO)


class WebSocketManager:
    def __init__(self):
        self.connections = set()
        self.locations = {}

    async def register(self, websocket, location):
        self.connections.add(websocket)
        self.locations[websocket] = location
        logging.info(
            f"Registered a client. Current connections: {len(self.connections)}"
        )
        logging.info(self.connections)

    async def unregister(self, websocket):
        if websocket in self.connections:
            self.connections.remove(websocket)
            if websocket in self.locations:
                del self.locations[websocket]
            logging.info(
                f"Unregistered a client. Remaining connections: {len(self.connections)}"
            )
        else:
            logging.warning(f"Trying to unregister a websocket that's not registered.")

    async def send_to_all(self, message):
        for connection in self.connections:
            if connection.open:
                await connection.send(
                    json.dumps({"event": "all_clients", "context": message})
                )
            else:
                await self.unregister(connection)

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
            print(type(location))
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


import os
from datetime import datetime
import json
from models import Database
import cv2


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
            self.save_screenshot(detected_face, frame)
            await self.send_alert(detected_face, url)
            self.last_alert_time[detected_face] = now

        self.face_last_seen[detected_face] = now

    def save_screenshot(self, detected_face, frame):
        year, month, day = datetime.now().timetuple()[:3]
        path = f"../media/screenshots/{detected_face}/{year}/{month}/{day}"
        if not os.path.exists(path):
            os.makedirs(path)
        filename = (
            path
            + f"/{datetime.now().hour}-{datetime.now().minute}-{datetime.now().second}.jpg"
        )
        cv2.imwrite(filename, frame)

    async def send_alert(self, detected_face, url):
        details = self.database.get_details(detected_face)
        camera = self.database.get_camera(url)
        camera_details = camera or None

        context = {
            "id": details[0],
            "first_name": detected_face,
            "last_name": details[1],
            "age": details[2],
            "description": details[-1],
            "url": url,
            "camera": camera_details,
        }
        print("Context: ", context)
        await self.websocket_manager.send_to_all(
            json.dumps({"event": "all_clients", "context": context})
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

    async def detect_and_process_faces(self, frame, start, url):
        faces = self.face_model.get(frame)
        detected_faces = await asyncio.gather(
            *(self.face_recognition.process_face(face) for face in faces)
        )
        detected_faces = set(filter(None, detected_faces))

        for result in detected_faces:
            await self.alert_manager.handle_alert(result, frame, url)

    async def continuous_stream_faces(self, url):
        cap = VideoStream(url).start()
        try:
            while True:
                frame = cap.read()
                if frame is None:
                    continue
                current_time = time.time()
                await self.detect_and_process_faces(frame, current_time, url)
        except (KeyboardInterrupt, websockets.exceptions.ConnectionClosedError):
            logging.info(f"Stream {url} terminated.")
        finally:
            cap.stop()

    async def multiple_cameras(self):
        tasks = [self.continuous_stream_faces(url) for url in self.urls]
        await asyncio.gather(*tasks)


async def websocket_server(websocket, path):
    try:
        logging.info("Attempt to connect received.")
        location = await websocket.recv()
        location_data = json.loads(location)
        location = (location_data["latitude"], location_data["longitude"])
        await stream.websocket_manager.register(websocket, location)
        while True:
            if websocket.open:
                await websocket.ping()
            await asyncio.sleep(10)
    except websockets.exceptions.ConnectionClosedError as e:
        logging.error(f"Connection closed: {e}")
    except asyncio.exceptions.IncompleteReadError as e:
        logging.error(f"Incomplete read: {e}")
    finally:
        await stream.websocket_manager.unregister(websocket)


if __name__ == "__main__":
    camera_urls = ["http://192.168.1.152:5000/video"]
    stream = MainStream(absolute_path + "/criminals/", camera_urls)
    loop = asyncio.get_event_loop()
    print("Starting websocket server")
    loop.run_until_complete(websockets.serve(websocket_server, "0.0.0.0", 5000))
    print("Websocket server started")

    loop.run_until_complete(stream.multiple_cameras())
