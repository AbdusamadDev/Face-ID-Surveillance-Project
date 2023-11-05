from datetime import datetime
from models import Database
import json
from utils import host_address, save_screenshot


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
            await self.send_alert(detected_face, url)
            year, month, day = datetime.now().timetuple()[:3]
            path = (
                f"../media/screenshots/criminals/{detected_face}/{year}/{month}/{day}"
            )
            image_name = save_screenshot(frame, path=path, camera_url=url)
            camera_object = self.database.get_camera(url)
            if camera_object:
                camera_object = camera_object[0]
            self.database.insert_records(
                image=f"{host_address}{image_name[2:]}",
                date_recorded=datetime.now(),
                criminal=int(detected_face),
                camera=camera_object
            )
            self.last_alert_time[detected_face] = now

        self.face_last_seen[detected_face] = now

    async def send_alert(self, detected_face, url):
        details = self.database.get_details(detected_face)
        camera = self.database.get_camera(url)
        camera_details = camera or None
        camera_context = {
            "id": camera_details[0],
            "name": camera_details[1],
            "url": camera_details[2],
            "longitude": camera_details[3],
            "latitude": camera_details[4],
            "image": host_address + "/" + camera_details[-1]
        }
        context = {
            "id": details[0],
            "first_name": details[1],
            "last_name": details[2],
            "middle_name": details[-1],
            "age": details[3],
            "description": details[4],
            "date_joined": str(details[5]),
            "url": url,
            "camera": camera_context,
        }

        print("Context: ", context)
        await self.websocket_manager.send_to_all(
            json.dumps(context)
        )
        await self.websocket_manager.send_to_nearest_client(
            json.dumps(context)
        )
