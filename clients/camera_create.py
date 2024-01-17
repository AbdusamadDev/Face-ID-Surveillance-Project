import requests


image = open("main.jpg", "rb")
for i in range(25,30):
    print(
        requests.post(
            "http://0.0.0.0:7000/api/camera/",
            data={
                "name": f"Camera {i}",
                "url": f"rtsp://admin:p@rolo12345@192.168.254.201:554/h264/ch{i}/main/av_stream",
                "longitude": 45.465,
                "latitude": 78.4565,
            },
            files={"file": ("main.jpg", image, "image/jpeg")},
            headers={"Authorization": "Token 459ede94edbd1c8a1fc1a47194bebaf79523853e"},
        ).json()
    )
