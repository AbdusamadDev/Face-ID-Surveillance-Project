import asyncio
import cv2

print("main.py" + "\n" * 5)


class CameraConnection:
    def __init__(self, camera_urls):
        self.camera_urls = camera_urls
        self.max_retries = 3
        self.cameras = []

    async def connect_camera(self, url):
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                cap = cv2.VideoCapture(url)
                if cap.isOpened():
                    print("Camera is connected")
                    return cap
            except:
                retry_count += 1
                await asyncio.sleep(5)  # wait 5 seconds before retrying
        raise ConnectionError(f"Failed to connect to {url} after {self.max_retries} retries")

    async def connect_all(self):
        for url in self.camera_urls:
            camera = await self.connect_camera(url)
            self.cameras.append(camera)
        print("All cameras connected")
        return self.cameras
