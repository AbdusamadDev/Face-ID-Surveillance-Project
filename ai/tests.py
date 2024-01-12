from imutils.video import VideoStream
from urllib.parse import urlparse
from datetime import datetime
import logging
import time
import cv2
import os
import threading
from ai.face_recognition import FaceRecognition
from ai.socket_manager import WebSocketManager
from ai.alert_manager import AlertManager
from ai.utils import host_address
from ai.train import FaceTrainer
from ai.models import Database
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.DEBUG)
root_dir = os.getenv("BASE_DIR")


class MainStream:
    def __init__(self):
        self.database = Database()
        self.websocket_manager = WebSocketManager()
        print(root_dir)
        self.trainer = FaceTrainer(os.path.join(root_dir, "media/criminals"))
        self.index = self.trainer.index
        self.known_face_names = self.trainer.known_face_names
        self.face_model = self.trainer.face_model
        self.alert_manager = AlertManager(self.websocket_manager)
        self.face_recognition = FaceRecognition(self)
        self.processing_queue = []
        self.tasks = []

    def capture_and_send_frames(self, url):
        cap = VideoStream(url).start()
        try:
            while True:
                frame = cap.read()
                if frame is not None:
                    self.processing_queue.append((frame, url))
        except KeyboardInterrupt:
            print(f"Task for {url} has been cancelled.")
        finally:
            cap.stop()

    def process_frames(self):
        """Processes frames from all cameras."""
        last_screenshot_time = datetime.now()
        screenshot_interval = 5
        while True:
            if self.processing_queue:
                frame, url = self.processing_queue.pop(0)
                self.face_recognition.current_frame = frame
                current_time = datetime.now()
                faces = self.face_model.get(frame)
                results = [self.face_recognition.process_face(face) for face in faces]
                for name in results:
                    if name is not None:
                        self.alert_manager.handle_alert(
                            frame=frame, detected_face=name, url=url
                        )
                if (
                    current_time - last_screenshot_time
                ).total_seconds() >= screenshot_interval:
                    print("\n"*5)
                    self.save_screenshot(frame, url, current_time)
                    last_screenshot_time = current_time

    def reload_face_encodings_periodically(self):
        while True:
            self.index, self.known_face_names = self.trainer.load_face_encodings(
                os.path.join(root_dir, "media/criminals")
            )
            (
                self.face_recognition.index,
                self.face_recognition.known_face_names,
            ) = self.trainer.load_face_encodings(
                os.path.join(root_dir, "media/criminals")
            )
            time.sleep(60)

    def start_camera_streams(self):
        for url in database.get_camera_urls():
            print("Connected: ", url)
            self.capture_and_send_frames(url)



    # def reconnect_cameras_periodically(self, interval=5):
    #     while True:
    #         print("Length of threads: ", threading.active_count())
    #         for thread in threading.enumerate():
    #             if thread != threading.current_thread():
    #                 thread.join()

    #         self.processing_queue.clear()
    #         self.start_camera_streams()
    #         print("Length of threads: ", threading.active_count())
    #         time.sleep(interval)

    def save_screenshot(self, frame, url, timestamp):
        """Saves a screenshot with a specific naming format, including only the IP address from the URL."""
        parsed_url = urlparse(url)
        ip_address = parsed_url.hostname
        formatted_time = timestamp.strftime("%Y-%m-%d|%H-%M-%S")
        filename = f"{formatted_time}|{ip_address}.jpg"
        directory = os.path.join(root_dir, "media/screenshots/suspends")
        os.makedirs(directory, exist_ok=True)  # Ensure directory exists
        filepath = os.path.join(directory, filename)
        print(filename, filepath, directory)
        print("\n" * 5)
        cv2.imwrite(filepath, frame)




    # reload_encodings_thread = threading.Thread(target=stream.reload_face_encodings_periodically)
    # camera_reconnection_thread = threading.Thread(target=stream.reconnect_cameras_periodically)
    # camera_reconnection_thread.start()
    # reload_encodings_thread.start()
    


if __name__ == "__main__":
    database = Database()
    stream = MainStream()
    logging.basicConfig(level=logging.INFO)
    frame_thread = threading.Thread(target=stream.start_camera_streams)
    frame_thread.start()
    base_thread = threading.Thread(target=stream.process_frames)
    base_thread.start()