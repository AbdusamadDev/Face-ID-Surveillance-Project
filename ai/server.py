import asyncio
import websockets
import logging
import json
from path import absolute_path
from stream import MainStream


async def websocket_server(websocket, path):
    try:
        logging.info("Attempt to connect received.")
        location = await websocket.recv()
        location_data = json.loads(location)
        location = (location_data["latitude"], location_data["longitude"])
        await stream.websocket_manager.register(websocket, location)
        while True:
            if websocket.open:
                await websocket.ping()
            await asyncio.sleep(10)
    except websockets.exceptions.ConnectionClosedError as e:
        logging.error(f"Connection closed: {e}")
    except asyncio.exceptions.IncompleteReadError as e:
        logging.error(f"Incomplete read: {e}")
    finally:
        await stream.websocket_manager.unregister(websocket)


if __name__ == "__main__":
    camera_urls = ["http://192.168.1.152:5000/video"]
    stream = MainStream(absolute_path + "/criminals/", camera_urls)
    loop = asyncio.get_event_loop()
    print("Starting websocket server")
    loop.run_until_complete(websockets.serve(websocket_server, "0.0.0.0", 5000))
    print("Websocket server started")

    loop.run_until_complete(stream.multiple_cameras())
