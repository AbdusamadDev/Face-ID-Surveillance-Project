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
import concurrent.futures

from models import Database
from server import WebSocketServer
from utils import save_screenshot


load_dotenv()


class Surveillance:
    def __init__(self, root_dir, database):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        try:
            self.face_model = insightface.app.FaceAnalysis()
            self.root_dir = root_dir
            ctx_id = 0
            self.face_model.prepare(ctx_id=ctx_id)
            self.disappearance_timeout = 5
            self.last_detection_time = {}
        except Exception as e:
            raise

        self.database = database
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

    def process_frame(self, data):
        frame = data.get("frame")
        camera_index = data.get("camera_url")
        last_detection_time = data.get("last_detection_time", {})
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
                    print(f"Result: ", result, "\n" * 5)

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
                    last_detection_time[result] = current_time
                    timestamp = time.strftime("%Y/%m/%d")
                    path = os.path.join(
                        "media/screenshots/criminals/", result, str(timestamp)
                    )
                    self.save_screenshot(frame, path)
                    print("Adding to database")
                    self.database.add_web_temp_records(
                        result,
                        self.database.get_camera(camera_index).get("id"),
                        screenshot_url="http://0.0.0.0:8000/" + path,
                        date_created=datetime.now(),
                    )
                    self.database.insert_records(
                        image="http://0.0.0.0:8000/" + path,
                        criminal=result,
                        camera=self.database.get_camera(camera_index).get("id"),
                        date_recorded=datetime.now()
                    )

    def save_screenshot(self, frame, save_path):
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        timestamp = time.strftime("%Y-%m-%d:%H-%M-%S")
        filename = f"{timestamp}.jpg"
        screenshot_path = os.path.join(save_path, filename)

        cv2.imwrite(screenshot_path, frame)

    def check_disappeared_faces(self, last_detection_time, face_id):
        current_time = time.time()
        last_seen = last_detection_time.get(face_id)
        if last_seen is not None:
            if (current_time - last_seen) > 10:
                del last_detection_time[face_id]

    def reload_face_encodings(self):
        while True:
            print("Everything working")
            self.index.reset()
            self.known_face_names.clear()
            self.index, self.known_face_names = self.load_face_encodings(self.root_dir)
            time.sleep(5)

    def reconnect_cameras(self):
        pending_cameras = []
        while True:
            current_camera_urls = self.database.get_camera_urls()
            self.process_camera_frames_parallel(pending_cameras)
            pending_cameras.clear()
            time.sleep(60)
            for camera in self.database.get_camera_urls():
                if camera not in current_camera_urls:
                    pending_cameras.append(camera)

    def process_camera_frames_parallel(self, urls):
        with concurrent.futures.ThreadPoolExecutor(max_workers=70) as executor:
            futures = {
                executor.submit(self.bind, camera_url): camera_url
                for camera_url in urls
            }

            for future in concurrent.futures.as_completed(futures):
                camera_url = futures[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"Error processing camera {camera_url}: {e}")

    def bind(self, url):
        while True:
            camera = cv2.VideoCapture(url)

            if not camera.isOpened():
                time.sleep(60)
                continue
            else:
                print("Connected to camera: ", url)

            current_time = time.time()
            while True:
                ret, frame = camera.read()
                if not ret:
                    print(f"Error: Could not read frame from camera {url}")
                    break

                data = {
                    "camera_url": url,
                    "frame": frame,
                    "last_detection_time": self.last_detection_time,
                }
                self.process_frame(data)

                if (time.time() - current_time) > 5:
                    save_screenshot(
                        frame=frame,
                        camera_url=url,
                        path=os.path.join(
                            path, 
                            f"media/screenshots/suspends/{self.database.get_camera(url).get('id')}"
                        ),
                    )
                    current_time = time.time()
            camera.release()
            time.sleep(1)


if __name__ == "__main__":
    path = os.getenv("BASE_DIR")
    root_directory = os.path.join(path, "media/criminals/")
    database = Database()
    face_trainer = Surveillance(root_directory, database)
    reload_face_encodings_thread = threading.Thread(
        target=face_trainer.reload_face_encodings
    )
    reload_face_encodings_thread.start()
    reconnect_cameras_thread = threading.Thread(target=face_trainer.reconnect_cameras)
    reconnect_cameras_thread.start()
    threading.Thread(
        target=face_trainer.process_camera_frames_parallel,
        args=(database.get_camera_urls(),)
        ).start()
    import logging

    try:
        logging.basicConfig(level=logging.INFO)
        server = WebSocketServer(addr=("0.0.0.0", 11222))
        server.run()
    except KeyboardInterrupt:
        logging.info("Shutting down gracefully!")