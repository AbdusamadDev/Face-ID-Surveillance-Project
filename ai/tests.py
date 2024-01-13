import torch
import insightface
import cv2
import os
import numpy as np
import faiss
import time


class FaceTrainer:
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

    def process_frame(self, frame, threshold=0.6):
        query_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        query_faces = self.face_model.get(query_image)

        if not query_faces:
            print("No faces found in the current frame.")
            return

        for face in query_faces:
            query_embedding = face.embedding
            result = self.search_similar_face(query_embedding, threshold)

            if result:
                print(f"Similar face in the folder: {result}")
            else:
                print("No similar face found in the current frame.")

    def process_camera_frames(
        self,
        camera_index="rtsp://admin:p@rolo12345@192.168.254.201:554/h264/ch41/main/av_stream",
        threshold=600,
    ):
        camera = cv2.VideoCapture(camera_index)

        while True:
            ret, frame = camera.read()
            self.process_frame(frame, threshold)


# Example usage:
root_directory = "/home/ubuntu/project/BazaarSurveillance/media/criminals/"
face_trainer = FaceTrainer(root_directory)

# Process frames from the camera with default camera index (0)
face_trainer.process_camera_frames()
