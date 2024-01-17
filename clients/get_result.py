import requests
import time


index = 0
while True:
    print(
        requests.get(
            "http://0.0.0.0:8000/api/web-results/",
            headers={"Authorization": "Token 459ede94edbd1c8a1fc1a47194bebaf79523853e"},
        ).json()
    )
    time.sleep(1)
    index += 1
    print(index)
