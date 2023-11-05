import socket
import cv2
import os
from datetime import datetime


def host():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        public_ip = "http://" + str(s.getsockname()[0]) + ":8000"
    except Exception:
        public_ip = "Unable to get IP"
    finally:
        s.close()
    return public_ip


def save_screenshot(frame, camera_url, path):
    if not os.path.exists(path):
        os.makedirs(path)
    timestamp = datetime.now().strftime("%Y-%m-%d|%H-%M-%S")
    filename = f"{path}/{timestamp}|{camera_url.split('/')[2]}.jpg"
    cv2.imwrite(filename, frame)
    return filename


host_address = host()
