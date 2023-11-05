import asyncio
import json
import logging
import tracemalloc

import websockets
import os

from models import Database
from path import absolute_path
from utils import host_address
from stream import MainStream

tracemalloc.start()
logging.basicConfig(level=logging.INFO)


async def websocket_server(websocket, path):
    manager = stream.websocket_manager
    try:
        logging.info("Attempt to connect received.")
        message = await websocket.recv()
        data = json.loads(message) or None
        await manager.register(websocket, data)

        while True:
            await asyncio.sleep(10)

    except websockets.exceptions.ConnectionClosedError as e:
        logging.error(f"Connection closed: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}")
    finally:
        await manager.unregister(websocket)


def list_image_paths(directory):
    relative_paths = [os.path.join(directory, f) for f in os.listdir(directory) if
                      os.path.isfile(os.path.join(directory, f))]
    absolute_paths = [path.replace('../', host_address + "/", 1) for path in relative_paths]
    return absolute_paths


async def send_image_paths(websocket, path):
    sent_image_paths = set()
    while True:
        current_image_paths = set(list_image_paths("../media/screenshots/suspends/"))
        new_paths = current_image_paths - sent_image_paths  # Determine new files that haven't been sent
        for image_path in new_paths:
            image_name = os.path.basename(image_path)
            camera_url = image_name.split('|')[-1].rstrip('.jpg')
            camera_object = database.get_by_similar(camera_url)
            message = {"image_path": image_path, "camera_object": camera_object}
            await websocket.send(json.dumps(message))
            sent_image_paths.add(image_path)
        await asyncio.sleep(5)


# Modify the image_path_server coroutine to pass the database object to send_image_paths
async def image_path_server(websocket, path):
    consumer_task = asyncio.ensure_future(send_image_paths(websocket, path))
    done, pending = await asyncio.wait([consumer_task], return_when=asyncio.FIRST_COMPLETED)
    for task in pending:
        task.cancel()


async def main():
    image_server = await websockets.serve(image_path_server, "0.0.0.0", 5678)
    ws_server = await websockets.serve(websocket_server, "0.0.0.0", 5000)
    camera_streams = [await stream.continuous_stream_faces(url) for url in stream.urls]
    await asyncio.gather(ws_server, image_server, *camera_streams)


if __name__ == "__main__":
    database = Database()
    urls = database.get_camera_urls()
    stream = MainStream(absolute_path + "/criminals/", urls)
    asyncio.run(main())
