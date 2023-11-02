SIMILARITY_THRESHOLD = 500


class FaceRecognition:
    def __init__(self, main_stream):
        self.index = main_stream.index
        self.known_face_names = main_stream.known_face_names
        self.face_model = main_stream.face_model

    def process_frame(self, frame):
        faces = self.face_model.get(frame)
        return set(filter(None, [self.process_face(face) for face in faces]))

    async def process_face(self, face):
        similarity, index = self.index.search(face.embedding.reshape(1, -1), 1)
        return (
            self.known_face_names[index[0, 0]]
            if similarity[0, 0] < SIMILARITY_THRESHOLD
            else None
        )
