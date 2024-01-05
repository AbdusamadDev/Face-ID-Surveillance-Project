import time
import requests
import random

host = "localhost:8000"
creation = requests.post(
    f"http://{host}/api/mud/",
    json={
        "longitude": str(random.randint(1, 90)),
        "latitude": str(random.randint(1, 90)),
    },
    headers={
        "token": str(
            requests.get(
                f"http://{host}/android/auth/token/",
                headers={
                    "Authorization": "Token 459ede94edbd1c8a1fc1a47194bebaf79523853e"
                },
            )
            .json()
            .get("token")
        )
    },
)
print("Client created: ", creation.json())
print(creation.status_code)


def request(longitude, latitude):
    global creation
    print(
        requests.get(
            f"http://{host}/api/mud/",
            headers={
                "longitude": longitude,
                "latitude": latitude,
                "client-id": str(creation.json().get("client_pk")),
            },
        ).json(),
    )


# Tashkent: lat: 41.2995, long: 69.2401
# Russia: lat: 55.7558, long: 37.6176
tashkent_long, tashkent_lat = 69.2401, 41.2995
moscow_long, moscow_lat = 37.6176, 55.7558
while True:
    print(
        "Russia request: ",
        request(longitude=str(moscow_long), latitude=str(moscow_lat)),
    )
    print(
        "Uzbekistan request: ",
        request(longitude=str(tashkent_long), latitude=str(tashkent_lat)),
    )
    tashkent_long += 1
    tashkent_lat += 1
    moscow_long += 1
    moscow_lat += 1
    time.sleep(2)

# {
#     "uniqe id": {"longitude": 5464, "latitude": 8789789},
#     "uniqe id": {"longitude": 5464, "latitude": 8789789},
# }
