import socket


def characters() -> list:
    letters = [chr(i) for i in list(range(97, 123)) + list(range(65, 91))]
    underscore = ["_"]
    digits = [str(k) for k in list(range(10))]
    return letters + underscore + digits


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


allowed_characters = characters()
host_address = host()
