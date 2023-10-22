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

    async def process_face(self, face):
        embedding = face.embedding
        similarity, index = self.index.search(embedding.reshape(1, -1), 1)
        if similarity[0, 0] < 500:
            return self.known_face_names[index[0, 0]]
        return None
