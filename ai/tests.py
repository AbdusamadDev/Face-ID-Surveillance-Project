import torch
import insightface
import cv2
import os
import numpy as np
import faiss
import time
import threading


class CameraProcessor(threading.Thread):
    def __init__(self, face_trainer, camera_index, threshold, disappearance_timeout=5):
        super(CameraProcessor, self).__init__()
        self.face_trainer = face_trainer
        self.camera_index = camera_index
        self.threshold = threshold
        self.disappearance_timeout = disappearance_timeout
        self.last_detection_time = {}

    def run(self):
        while True:
            camera = cv2.VideoCapture(self.camera_index)
            if not camera.isOpened():
                print(f"Error: Could not open camera {self.camera_index}")
                time.sleep(2)
                continue
            else:
                print("Connected")
            while True:
                ret, frame = camera.read()
                if not ret:
                    print(
                        f"Error: Could not read frame from camera {self.camera_index}"
                    )
                    break
                self.face_trainer.process_frame(
                    frame, self.threshold, self.camera_index, self.last_detection_time
                )
            camera.release()
            time.sleep(1)


class Surveillance:
    def __init__(self, root_dir):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        try:
            self.face_model = insightface.app.FaceAnalysis()
            ctx_id = 0
            self.face_model.prepare(ctx_id=ctx_id)
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
        threshold=0.6,
        camera_index=0,
        last_detection_time=None,
        save_path="screenshots",
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
            result = self.search_similar_face(query_embedding, threshold)
            if result:
                print("Last detection time: ", last_detection_time)
                self.check_disappeared_faces(last_detection_time, face_id=result)
                current_time = time.time()
                if (
                    result not in last_detection_time
                    or (current_time - last_detection_time[result]) > threshold
                ):
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
                    self.save_screenshot(frame, result, save_path)

    def save_screenshot(self, frame, face_name, save_path):
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{face_name}_{timestamp}.png"
        screenshot_path = os.path.join(save_path, filename)

        cv2.imwrite(screenshot_path, frame)
        print(f"Screenshot saved: {screenshot_path}")

    def check_disappeared_faces(self, last_detection_time, face_id):
        current_time = time.time()
        last_seen = last_detection_time.get(face_id)
        if last_seen is not None:
            if (current_time - last_seen) > 5:
                del last_detection_time[face_id]
        # disappeared_faces = [
        #     face
        #     for face, last_time in last_detection_time.items()
        #     if (current_time - last_time) > 5
        # ]
        # for face in disappeared_faces:
        #     print(f"Face {face} has disappeared.")
        #     del last_detection_time[face]

    def process_camera_frames_parallel(self, camera_urls, threshold=500):
        threads = []
        for camera_url in camera_urls:
            thread = CameraProcessor(self, camera_url, threshold)
            threads.append(thread)

        for thread in threads:
            thread.start()


root_directory = "/home/ubuntu/project/BazaarSurveillance/media/criminals/"
face_trainer = Surveillance(root_directory)

# Specify multiple camera URLs
camera_urls = [
    f"rtsp://admin:p@rolo12345@192.168.254.201:554/h264/ch48/main/av_stream",
    f"rtsp://admin:p@rolo12345@192.168.254.201:554/h264/ch41/main/av_stream"
    # for i in  [5,41,44,48,29,30,31,34,35,37]
]

face_trainer.process_camera_frames_parallel(camera_urls)
