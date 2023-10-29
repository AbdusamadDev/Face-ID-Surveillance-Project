import time
import logging
import cv2
from datetime import datetime
from imutils.video import VideoStream
from train import FaceTrainer
from models import Database
import asyncio
import os
import websockets
import json
from utils import host_address
from path import absolute_path
from web import WebSocketManager
from alerts import AlertManager
from recognition import FaceRecognition

logging.basicConfig(level=logging.INFO)


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


async def websocket_server(websocket, path, stream):
    await stream.websocket_manager.register(websocket)
    try:
        while True:
            if websocket.open:
                await websocket.ping()
            await asyncio.sleep(10)
    except websockets.exceptions.ConnectionClosedError:
        logging.error("Connection closed")
    finally:
        await stream.websocket_manager.unregister(websocket)


if __name__ == "__main__":
    camera_urls = ["http://192.168.1.152:5000/video"]
    stream = MainStream(absolute_path + "/criminals/", camera_urls)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        websockets.serve(lambda *args: websocket_server(*args, stream), "0.0.0.0", 5000)
    )

    loop.run_until_complete(stream.multiple_cameras())
