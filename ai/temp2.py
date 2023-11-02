from train import FaceTrainer
from imutils.video import VideoStream
import asyncio
from pathlib import Path
import logging
from alerts import AlertManager
from recognition import FaceRecognition

logging.basicConfig(level=logging.INFO)



class MainStream:
    def __init__(self, root_dir, camera_urls, websocket):
        self.urls = camera_urls
        self.websocket = websocket
        self.trainer = FaceTrainer(root_dir)
        self.index = self.trainer.index
        self.known_face_names = self.trainer.known_face_names
        self.face_model = self.trainer.face_model

    async def detect_and_process_faces(self, frame, url):
        if not hasattr(self, "face_recognition"):
            self.face_recognition = FaceRecognition(self)
        if not hasattr(self, "alert_manager"):
            self.alert_manager = AlertManager(self.websocket)
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
                await self.detect_and_process_faces(frame, url)
        except Exception as e:
            logging.error(f"Error in stream {url}: {e}")
        finally:
            cap.stop()

    async def multiple_cameras(self):
        tasks = (self.continuous_stream_faces(url) for url in self.urls)
        await asyncio.gather(*tasks)
