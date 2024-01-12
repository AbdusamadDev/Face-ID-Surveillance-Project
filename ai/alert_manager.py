from ai.models import Database
from datetime import datetime
from ai.utils import save_screenshot, host_address
import json


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
            year, month, day = datetime.now().timetuple()[:3]
            path = (
                f"../media/screenshots/criminals/{detected_face}/{year}/{month}/{day}"
            )
            image_name = save_screenshot(frame, path=path, camera_url=url)
            await self.send_alert(
                detected_face, url, path=host_address + image_name[2:]
            )
            camera_object = self.database.get_camera(url)
            if camera_object:
                camera_object = camera_object.get("id")
            self.database.insert_records(
                image=f"{host_address}{image_name[2:]}",
                date_recorded=datetime.now(),
                criminal=int(detected_face),
                camera=camera_object,
            )
            self.database.add_temp()
            self.last_alert_time[detected_face] = now

        self.face_last_seen[detected_face] = now

    async def send_alert(self, detected_face, url, path):
        details = self.database.get_details(detected_face)
        camera = self.database.get_camera(url)
        camera["image"] = host_address + "/media/" + camera.get("image")
        details["date_created"] = str(details.get("date_created"))
        details["image"] = (
            host_address + "/media/criminals/" + str(detected_face) + "/" + "main.jpg"
        )
        result = {"identity": details, "camera": camera, "screenshot": path}
        await self.websocket_manager.send_to_all(json.dumps(result))
        print(result)
