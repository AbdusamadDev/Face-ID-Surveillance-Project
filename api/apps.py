from django.apps import AppConfig
import subprocess
import os
from dotenv import load_dotenv
from threading import Thread

load_dotenv()


def frontend():
    frontend_path = os.path.join("/home/ubuntu/project/MarketPlaceSecurityApp/dist/")
    os.system(f"cd {frontend_path} && serve -s .")


def run():
    script_path = os.path.join(os.getenv("BASE_DIR"), "ai/tests.py")
    subprocess.Popen(["python3", script_path])


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    # def ready(self) -> None:
    #     run()
    #     Thread(target=frontend).start()
    #     return super().ready()


{
    "id": 283,
    "criminal": {
        "id": 1,
        "first_name": "qweqweqw",
        "middle_name": "qw",
        "last_name": "weqweqwe",
        "age": 22,
        "description": "asdasds",
        "date_created": "2024-01-20T08:51:56.449220Z",
        "image_url": "http://192.168.1.252:8000/media/criminals/1/main.jpg",
        "image_path": "http://192.168.1.252:8000/media/screenshots/criminals/1/2024/01/20/2024-01-20:07-14-24.jpg",
    },
    "camera": {
        "id": 6,
        "name": "OFFICEasdasdasdasdasd",
        "image": "/media/cameras/odam_CKklHUH.jpg",
        "url": "rtsp://admin:p@rolo12345@192.168.254.201:554/h264/ch41/main/av_stream",
        "longitude": 21.00898683071137,
        "latitude": 52.231140984941085,
    },
    "date_recorded": "2024-01-20T12:14:24.917483Z",
}
