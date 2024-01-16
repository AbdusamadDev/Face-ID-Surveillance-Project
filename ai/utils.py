import socket
import numpy as np
from jose import jwt
from jose.exceptions import JWTError
import cv2
import os
from datetime import datetime
from urllib.parse import urlparse

SECRET_KEY = "your_secret_key"  # Should be kept secret and safe


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
    if not isinstance(frame, np.ndarray) or frame.size == 0:
        print("Invalid frame received, skipping screenshot.")
        return None

    if not os.path.exists(path):
        os.makedirs(path)

    parsed_url = urlparse(camera_url)
    ip_address = parsed_url.hostname
    timestamp = datetime.now().strftime("%Y-%m-%d|%H-%M-%S")
    filename = f"{path}/{timestamp}|{ip_address}.jpg"
    cv2.imwrite(filename, frame)
    return filename


def generate_jwt(data):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(
        hours=1
    )  # Token expires in 1 hour
    token = jwt.encode({"data": data, "exp": expiration}, SECRET_KEY, algorithm="HS256")
    return token


def verify_jwt(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload  # Return the payload if token is valid
    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except JWTError:
        # Token is invalid
        return None


host_address = host()
