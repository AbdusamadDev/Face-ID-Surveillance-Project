import multiprocessing

print("stream.py" + "\n" * 5)


class MultipleStream:
    def __init__(self, cameras, face_recognition):
        self.cameras = cameras
        self.face_recognition = face_recognition

    def process_camera(self, camera):
        print("Process camera function is being called")
        while True:
            ret, frame = camera.read()
            if ret:
                results = self.face_recognition.recognize_frame(frame)
            else:
                print("Failed to read frame from camera")

    # def run(self):
    #     print("Multiple stream class - run method is running")
    #     processes = []
    #     for camera in self.cameras:
    #         p = multiprocessing.Process(target=self.process_camera, args=(camera,))
    #         p.start()
    #         processes.append(p)
    #
    #     for p in processes:
    #         p.join()
