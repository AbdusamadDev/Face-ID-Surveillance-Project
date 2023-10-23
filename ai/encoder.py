import torch
import insightface
import cv2


class FaceTrainer:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        try:
            self.face_model = insightface.app.FaceAnalysis()
            ctx_id = 0
            self.face_model.prepare(ctx_id=ctx_id)
        except Exception as e:
            print(f"Failed to load models: {e}")
            raise

    def read_image(self, image_path):
        return cv2.imread(image_path)

    def get_face_encodings(self, img):
        faces = self.face_analyzer.get(img)
        encodings = [face.normed_embedding for face in faces]
        return encodings

    def get_encodings(self, image_path):
        img = self.read_image(image_path)
        encodings = self.get_face_encodings(img)
        return encodings
