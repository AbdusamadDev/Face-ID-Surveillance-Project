import cv2
from datetime import datetime

from train import FaceTrainer
from models import get_details

print("recognition.py" + "\n" * 5)


class FaceRecognition:
    def __init__(self, root_dir):
        print("Face recognition class is being initiated")
        self.trainer = FaceTrainer(root_dir)
        self.index = self.trainer.index
        self.known_face_names = self.trainer.known_face_names
        self.face_model = self.trainer.face_model
        self.last_alert_time = {}
        self.face_last_seen = {}

    def process_face(self, face):
        embedding = face.embedding
        similarity, index = self.index.search(embedding.reshape(1, -1), 1)
        if similarity[0, 0] < 500:
            return self.known_face_names[index[0, 0]]
        return None

    def recognize_frame(self, frame):
        faces = self.face_model.get(frame)
        detected_faces = set()  # Keep track of faces detected in the current frame

        for face in faces:
            result = self.process_face(face)
            if result:
                detected_faces.add(result)  # Add to currently detected faces
                now = datetime.now()
                time_since_last_seen = (now - self.face_last_seen.get(result, datetime.min)).total_seconds()

                if time_since_last_seen > 5 and result not in self.last_alert_time:
                    filename = "../screenshots/%s_%s.jpg" % (result, str(datetime.now()))
                    cv2.imwrite(filename, frame)
                    details = get_details(result)
                    try:
                        context = {
                            "first_name": result,
                            "last_name": details[1],
                            "age": details[2],
                            "description": details[-1],
                            "image": f"http://192.168.1.122:5000/media/{result}"
                        }
                        print("Context: ", context)
                        # Send data through WebSocket or other means if needed.
                    except Exception as error:
                        print("Details of exception: ", details)
                        print(error)

                    self.last_alert_time[result] = now  # Update last alert time

                # Update the last seen time for the face
                self.face_last_seen[result] = now

        current_time = datetime.now()
        faces_to_remove = [face for face, timestamp in self.face_last_seen.items() if
                           (current_time - timestamp).total_seconds() > 5]
        for face in faces_to_remove:
            self.face_last_seen.pop(face, None)
            self.last_alert_time.pop(face, None)  # Make it eligible for future alerts
