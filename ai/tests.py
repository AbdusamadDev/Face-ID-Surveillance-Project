import torch
import insightface
import cv2
import os
import numpy as np
import faiss
import time
import threading
import os
from dotenv import load_dotenv
from datetime import datetime

from ai.models import Database
from ai.server import WebSocketServer
from ai.utils import save_screenshot


load_dotenv()


# class CameraProcessor(threading.Thread):
#     def __init__(self, face_trainer, camera_index, threshold, disappearance_timeout=5):
#         super(CameraProcessor, self).__init__()
#         self.face_trainer = face_trainer
#         self.camera_index = camera_index
#         self.threshold = threshold
#         self.disappearance_timeout = disappearance_timeout
#         self.last_detection_time = {}

#     def run(self):
#         while True:
#             camera = cv2.VideoCapture(self.camera_index)
#             if not camera.isOpened():
#                 print(f"Error: Could not open camera {self.camera_index}")
#                 print("Reconnecting after a minute...")
#                 time.sleep(60)
#                 continue
#             else:
#                 print("Connected to camera: ", self.camera_index)
#             current_time = time.time()
#             while True:
#                 ret, frame = camera.read()
#                 if not ret:
#                     print(
#                         f"Error: Could not read frame from camera {self.camera_index}"
#                     )
#                     break
#                 self.process_frame(
#                     frame, self.threshold, self.camera_index, self.last_detection_time
#                 )
#                 if (time.time() - current_time) > 5:
#                     save_screenshot(
#                         frame=frame,
#                         camera_url=self.camera_index,
#                         path=os.path.join(path, "media/screenshots/suspends"),
#                     )
#                     current_time = time.time()
#             camera.release()
#             time.sleep(1)


class Surveillance:
    def __init__(self, root_dir):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        try:
            self.face_model = insightface.app.FaceAnalysis()
            self.root_dir = root_dir
            ctx_id = 0
            self.face_model.prepare(ctx_id=ctx_id)
            self.disappearance_timeout = 5
            self.last_detection_time = {}
        except Exception as e:
            print(f"Failed to load models: {e}")
            raise

        self.index, self.known_face_names = self.load_face_encodings(root_dir)

    def load_face_encodings(self, root_dir):
        known_face_encodings = []
        known_face_names = []
        for dir_name in os.listdir(root_dir):
            dir_path = os.path.join(root_dir, dir_name)
            if os.path.isdir(dir_path):
                for file_name in os.listdir(dir_path):
                    if file_name.endswith((".jpg", ".png")):
                        image_path = os.path.join(dir_path, file_name)
                        image = cv2.imread(image_path)
                        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                        faces = self.face_model.get(image)

                        if faces:
                            for face in faces:
                                embedding = face.embedding
                                known_face_encodings.append(embedding)
                                known_face_names.append(dir_name)

        known_face_encodings = np.array(known_face_encodings)
        index = faiss.IndexFlatL2(known_face_encodings.shape[1])
        index.add(known_face_encodings)
        return index, known_face_names

    def search_similar_face(self, query_embedding, threshold=0.6):
        D, I = self.index.search(np.array([query_embedding]), 1)
        if D[0][0] <= threshold:
            similar_face_name = self.known_face_names[I[0][0]]
            return similar_face_name
        else:
            return None

    def process_frame(
        self,
        frame,
        camera_index=0,
        last_detection_time=None,
    ):
        if frame is None:
            print(f"Error: Unable to read frame from the camera {camera_index}.")
            return

        query_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        query_faces = self.face_model.get(query_image)

        if not query_faces:
            return

        for face in query_faces:
            query_embedding = face.embedding
            result = self.search_similar_face(query_embedding, 520)
            if result:
                self.check_disappeared_faces(last_detection_time, face_id=result)
                current_time = time.time()
                if result not in last_detection_time:
                    rect_color = (0, 255, 0)  # Green color
                    rect_thickness = 2
                    bbox = face.bbox.astype(int)
                    cv2.rectangle(
                        frame,
                        (bbox[0], bbox[1]),
                        (bbox[2], bbox[3]),
                        rect_color,
                        rect_thickness,
                    )
                    print(f"Similar face in the folder: {result}")
                    last_detection_time[result] = current_time
                    timestamp = time.strftime("%Y/%m/%d")
                    path = os.path.join(
                        "media/screenshots/criminals/", result, str(timestamp)
                    )
                    self.save_screenshot(frame, path)
                    print("Camera index::::::::: ", database.get_camera(camera_index))
                    database.add_web_temp_records(
                        result,
                        database.get_camera(camera_index).get("id"),
                        screenshot_url="http://0.0.0.0:8000/" + path,
                        date_created=datetime.now(),
                    )

    def save_screenshot(self, frame, save_path):
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        timestamp = time.strftime("%Y-%m-%d:%H-%M-%S")
        filename = f"{timestamp}.jpg"
        screenshot_path = os.path.join(save_path, filename)

        cv2.imwrite(screenshot_path, frame)
        print(f"Screenshot saved: {screenshot_path}")

    def check_disappeared_faces(self, last_detection_time, face_id):
        current_time = time.time()
        last_seen = last_detection_time.get(face_id)
        if last_seen is not None:
            if (current_time - last_seen) > 10:
                print(last_detection_time[face_id])
                del last_detection_time[face_id]

    def process_camera_frames_parallel(self, urls):
        threads = []

        for camera_url in urls:
            thread = threading.Thread(target=self.bind, args=(camera_url,))
            threads.append(thread)

        for thread in threads:
            time.sleep(1)
            thread.start()

    def reload_face_encodings(self):
        while True:
            print("Length of face encodings: ", self.index.ntotal)
            self.index.reset()
            self.known_face_names.clear()
            self.index, self.known_face_names = self.load_face_encodings(self.root_dir)
            time.sleep(5)

    def reconnect_cameras(self):
        pending_cameras = []
        while True:
            current_camera_urls = database.get_camera_urls()
            self.process_camera_frames_parallel(pending_cameras)
            pending_cameras.clear()
            time.sleep(5)
            for camera in database.get_camera_urls():
                if camera not in current_camera_urls:
                    pending_cameras.append(camera)
            print("Pending connect cameras: ", pending_cameras)

    def bind(self, url):
        while True:
            camera = cv2.VideoCapture(url)
            if not camera.isOpened():
                print(f"Error: Could not open camera {url}")
                print("Reconnecting after a minute...")
                time.sleep(60)
                continue
            else:
                print("Connected to camera: ", url)
            current_time = time.time()
            while True:
                ret, frame = camera.read()
                if not ret:
                    print(
                        f"Error: Could not read frame from camera {url}"
                    )
                    break
                self.process_frame(
                    frame, url, self.last_detection_time
                )
                if (time.time() - current_time) > 5:
                    save_screenshot(
                        frame=frame,
                        camera_url=url,
                        path=os.path.join(path, "media/screenshots/suspends"),
                    )
                    current_time = time.time()
            camera.release()
            time.sleep(1)


if __name__ == "__main__":
    path = os.getenv("BASE_DIR")
    root_directory = os.path.join(path, "media/criminals/")
    face_trainer = Surveillance(root_directory)
    database = Database()
    reload_face_encodings_thread = threading.Thread(
        target=face_trainer.reload_face_encodings
    )
    reload_face_encodings_thread.start()
    reconnect_cameras_thread = threading.Thread(target=face_trainer.reconnect_cameras)
    reconnect_cameras_thread.start()
    face_trainer.process_camera_frames_parallel(database.get_camera_urls())
    import logging

    try:
        logging.basicConfig(level=logging.INFO)
        server = WebSocketServer(addr=("0.0.0.0", 11223))
        server.run()
    except KeyboardInterrupt:
        logging.info(" Shutting down gracefully!")