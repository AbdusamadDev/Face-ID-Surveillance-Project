import socket


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


host_address = host()
