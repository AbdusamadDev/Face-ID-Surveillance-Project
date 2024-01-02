import time
import requests
import multiprocessing


def ddos_like_request(index):
    # print(
    requests.get(
        "http://0.0.0.0:8000/api/mud/",
        headers={
            "longitude": "69.2401" + str(index),
            "latitude": "41.2995" + str(index),
        },
    ).json(),


# )

# Tashkent  
while True:
    print(
        requests.get(
            "http://0.0.0.0:8000/api/mud/",
            headers={
                "longitude": "69.2401",
                "latitude": "41.2995",
            },
        ).json(),
    )
    time.sleep(1)

# while True:
#     start = time.time()
#     for i in range(1000):
#         multiprocessing.Process(target=ddos_like_request, args=(i,)).start()
#     print(time.time() - start)
#     time.sleep(3)
