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
