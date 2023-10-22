from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List
import asyncio
import cv2
from datetime import datetime
import json
import time
from imutils.video import VideoStream
import os
from models import get_details, get_camera
from train import FaceTrainer
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)


class WebSocketManager:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)

    async def broadcast(self, data: str):
        for connection in self.connections:
            await connection.send_text(data)


class ConnectionManager(WebSocketManager):
    pass


class WebSocketManager:
    def __init__(self):
        self.connections = set()

    async def register(self, websocket):
        self.connections.add(websocket)

    async def unregister(self, websocket):
        self.connections.remove(websocket)

    async def send_to_all(self, message):
        if self.connections:
            for connection in self.connections:
                if connection.open:
                    await connection.send(message)


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

    async def handle_alert(self, detected_face, frame, url):
        now = datetime.now()
        last_alert_time = self.last_alert_time.get(detected_face, datetime.min)
        time_since_last_alert = (now - last_alert_time).total_seconds()

        time_since_last_seen = (
            now - self.face_last_seen.get(detected_face, datetime.min)
        ).total_seconds()

        if (
            time_since_last_seen > 5 and time_since_last_alert > 3
        ):  # 3 seconds between alerts
            self.save_screenshot(detected_face, frame)
            await self.send_alert(detected_face, url)
            self.last_alert_time[detected_face] = now  # Update last alert time

        # Update the last seen time for the face
        self.face_last_seen[detected_face] = now

    def save_screenshot(self, detected_face, frame):
        year, month, day = datetime.now().timetuple()[:3]
        path = f"../screenshots/{detected_face}/{year}/{month}/{day}"
        if not os.path.exists(path):
            os.makedirs(path)
        filename = (
            path
            + f"/{datetime.now().hour}-{datetime.now().minute}-{datetime.now().second}.jpg"
        )
        cv2.imwrite(filename, frame)

    # Modify send_alert method in AlertManager class
    async def send_alert(self, detected_face, url):
        details = get_details(detected_face)
        camera = get_camera(url)
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
        await self.websocket_manager.send_to_all(json.dumps(context))


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
        except KeyboardInterrupt:
            logging.info(f"Stream {url} terminated by the user.")
        finally:
            cap.stop()

    async def multiple_cameras(self):
        tasks = [self.continuous_stream_faces(url) for url in self.urls]
        await asyncio.gather(*tasks)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client said: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client left the chat")


@app.on_event("startup")
async def startup_event():
    camera_urls = ["http://192.168.1.142:5000/video"]
    stream = MainStream("../media", camera_urls)
    asyncio.create_task(stream.multiple_cameras())

