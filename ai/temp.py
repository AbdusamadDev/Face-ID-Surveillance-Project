import time
import logging
from imutils.video import VideoStream
from train import FaceTrainer
import asyncio
import websockets
import json
from path import absolute_path
import tracemalloc
from recognition import FaceRecognition
from web import WebSocketManager
from alerts import AlertManager

tracemalloc.start()


logging.basicConfig(level=logging.INFO)


class MainStream:
    def __init__(self, root_dir, camera_urls):
        self.websocket_manager = WebSocketManager()
        self.alert_manager = AlertManager(self.websocket_manager)
        self.trainer = FaceTrainer(root_dir)
        self.index = self.trainer.index
        self.known_face_names = self.trainer.known_face_names
        self.face_model = self.trainer.face_model
        self.face_recognition = FaceRecognition(self)
        self.urls = camera_urls

    async def detect_and_process_faces(self, frame, url):
        faces = self.trainer.face_model.get(frame)
        detected_faces = {
            await face
            for face in map(self.face_recognition.process_face, faces)
            if face
        }
        for result in detected_faces:
            await self.alert_manager.handle_alert(result, frame, url)

    async def continuous_stream_faces(self, url):
        cap = VideoStream(url).start()
        while True:
            frame = cap.read()
            if frame is None:
                break
            await self.detect_and_process_faces(frame, url)
        cap.stop()

    async def multiple_cameras(self):
        await asyncio.gather(*(self.continuous_stream_faces(url) for url in self.urls))


async def websocket_server(websocket, _):
    try:
        location_data = json.loads(await websocket.recv())
        await stream.websocket_manager.register(
            websocket, (location_data["latitude"], location_data["longitude"])
        )
        while websocket.open:
            await asyncio.sleep(10)
    finally:
        await stream.websocket_manager.unregister(websocket)


if __name__ == "__main__":
    stream = MainStream(
        absolute_path + "/criminals/", ["http://192.168.1.152:5000/video"]
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(websockets.serve(websocket_server, "0.0.0.0", 5000))
    loop.run_until_complete(stream.multiple_cameras())

    loop.run_until_complete(stream.multiple_cameras())
