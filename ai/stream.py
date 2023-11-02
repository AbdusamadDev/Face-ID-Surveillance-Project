import asyncio
import time
import logging
from imutils.video import VideoStream
from web import WebSocketManager
from alerts import AlertManager
from recognition import FaceRecognition
from train import FaceTrainer
import websockets


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
