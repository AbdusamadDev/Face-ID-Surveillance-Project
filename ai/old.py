import time
import logging
import cv2
from datetime import datetime
from imutils.video import VideoStream
from train import FaceTrainer
from models import get_details, get_camera
import asyncio
from concurrent.futures import ThreadPoolExecutor
import os

logging.basicConfig(level=logging.INFO)


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

    def process_face(self, face):
        embedding = face.embedding
        similarity, index = self.index.search(embedding.reshape(1, -1), 1)
        if similarity[0, 0] < 500:
            return self.known_face_names[index[0, 0]]
        return None


class AlertManager:
    def __init__(self):
        self.last_alert_time = {}
        self.face_last_seen = {}

    def handle_alert(self, detected_face, frame, url):
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
            self.send_alert(detected_face, url)
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
    def send_alert(self, detected_face, url):
        details = get_details(detected_face)
        camera = get_camera(url)
        camera_details = camera or None

        context = {
            "first_name": detected_face,
            "last_name": details[1],
            "age": details[2],
            "description": details[-1],
            "url": url,
            "camera": camera_details,
        }
        print("Context: ", context)
        # Broadcasting the alert message


class MainStream:
    def __init__(self, root_dir, camera_urls):
        self.urls = camera_urls
        self.trainer = FaceTrainer(root_dir)
        self.index = self.trainer.index
        self.known_face_names = self.trainer.known_face_names
        self.face_model = self.trainer.face_model
        self.alert_manager = AlertManager()
        self.face_recognition = FaceRecognition(self)

    def detect_and_process_faces(self, frame, start, url):
        faces = self.face_model.get(frame)
        detected_faces = set()
        for face in faces:
            result = self.face_recognition.process_face(face)
            if result:
                detected_faces.add(result)
                self.alert_manager.handle_alert(result, frame, url)

    async def continuous_stream_faces(self, url):
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            cap = VideoStream(url).start()
            try:
                while True:
                    frame = cap.read()
                    if frame is None:
                        continue
                    current_time = time.time()
                    await loop.run_in_executor(
                        executor,
                        self.detect_and_process_faces,
                        frame,
                        current_time,
                        url,
                    )
            except KeyboardInterrupt:
                logging.info(f"Stream {url} terminated by the user.")
            finally:
                cap.stop()

    async def multiple_cameras(self):
        tasks = [self.continuous_stream_faces(url) for url in self.urls]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    CAMERA_URL = ["http://192.168.1.142:5000/video"]
    main_stream = MainStream("../media", CAMERA_URL)
    asyncio.run(main_stream.multiple_cameras())