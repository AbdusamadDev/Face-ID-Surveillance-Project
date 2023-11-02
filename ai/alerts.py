import os
import json
import cv2
from datetime import datetime
from models import Database


class AlertManager:
    def __init__(self, websocket_manager):
        self.websocket_manager = websocket_manager
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
            self.save_screenshot(detected_face, frame)
            await self.send_alert(detected_face, url)
            self.last_alert_time[detected_face] = now

        self.face_last_seen[detected_face] = now

    def save_screenshot(self, detected_face, frame):
        year, month, day = datetime.now().timetuple()[:3]
        path = f"../media/screenshots/{detected_face}/{year}/{month}/{day}"
        if not os.path.exists(path):
            os.makedirs(path)
        filename = (
            path
            + f"/{datetime.now().hour}-{datetime.now().minute}-{datetime.now().second}.jpg"
        )
        cv2.imwrite(filename, frame)

    async def send_alert(self, detected_face, url):
        details = self.database.get_details(detected_face)
        camera = self.database.get_camera(url)
        camera_details = camera or None

        context = {
            "id": details[0],
            "first_name": detected_face,
            "last_name": details[1],
            "age": details[2],
            "description": details[-1],
            "url": url,
            "camera": camera_details,
        }
        location = (40.9983, 71.67257)
        print("Result in alert manager: \n\n", context)
        await self.websocket_manager.broadcast_to_web_clients(
            json.dumps({"event": "all_clients", "context": context})
        )
        await self.websocket_manager.send_to_nearest_apk_client(
            message=json.dumps({"event": "nearest_client", "context": context}),
            location=location,
        )
