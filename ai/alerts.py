from datetime import datetime
from models import Database
import cv2
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SCREENSHOT_PATH = Path("../media/screenshots")


class AlertManager:
    def __init__(self, websocket):
        self.websocket = websocket
        self.last_alert_time = {}
        self.face_last_seen = {}
        self.database = Database()

    async def handle_alert(self, detected_face, frame, url):
        now = datetime.now()
        last_alert_time = self.last_alert_time.get(detected_face, datetime.min)
        time_since_last_alert = (now - last_alert_time).total_seconds()
        time_since_last_seen = (
            now - self.face_last_seen.get(detected_face, datetime.min)
        ).total_seconds()

        if time_since_last_seen > 5 and time_since_last_alert > 3:
            details = self.database.get_details(detected_face)
            camera = self.database.get_camera(url)
            context = {
                "id": details[0],
                "first_name": detected_face,
                "last_name": details[1],
                "age": details[2],
                "description": details[-1],
                "url": url,
                "camera": camera,
            }
            print("Context: ", context)
            await self.websocket.send_to_all(json.dumps(context))
            self.save_screenshot(detected_face, frame)
            self.last_alert_time[detected_face] = now

        self.face_last_seen[detected_face] = now

    def save_screenshot(self, detected_face, frame):
        with ThreadPoolExecutor() as executor:
            executor.submit(self._save_image, detected_face, frame)

    def _save_image(self, detected_face, frame):
        now = datetime.now()
        path = SCREENSHOT_PATH / detected_face / f"{now.year}/{now.month}/{now.day}"
        path.mkdir(parents=True, exist_ok=True)
        filename = path / f"{now.hour}-{now.minute}-{now.second}.jpg"
        cv2.imwrite(str(filename), frame)
