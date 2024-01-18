from django.apps import AppConfig
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()

def run():
    script_path = os.path.join(os.getenv("BASE_DIR"), "ai/tests.py")
    subprocess.Popen(["python3", script_path])


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def ready(self) -> None:
        run()
        print("Being ready soon")
        return super().ready()
