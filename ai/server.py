import asyncio
import websockets
from web import websocket_manager
import logging
import json

from path import absolute_path
from stream import MainStream

logging.basicConfig(level=logging.DEBUG)


async def websocket_handler(websocket, path):
    try:
        print(type(websocket))
        websocket.send("hello")
        location = await websocket.recv()
        location_data = json.loads(location)
        latitude, longitude, state = (
            location_data["latitude"],
            location_data["longitude"],
            location_data["state"],
        )
        await websocket_manager.register(websocket, (latitude, longitude), state)

        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                if websocket.open:
                    await websocket_manager.broadcast_to_web_clients({"echo": data})
                    await websocket_manager.send_to_nearest_apk_client(
                        {"echo": data}, (latitude, longitude)
                    )
            except websockets.exceptions.ConnectionClosed as e:
                logging.error(f"Connection closed: {e}")
                break  # Exit the loop and end the handler for this connection.
            except json.JSONDecodeError as e:
                logging.error(f"JSON decode error: {e}")
            except Exception as e:
                logging.error(f"Unexpected error: {e}")

    except websockets.exceptions.ConnectionClosedError as e:
        logging.error(f"Initial connection closed with error: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"Initial JSON decode error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error during registration: {e}")
    finally:
        await websocket_manager.unregister(websocket)


if __name__ == "__main__":
    start_server = websockets.serve(websocket_handler, "0.0.0.0", 5000)
    camera_urls = ["http://192.168.1.152:5000/video"]
    stream = MainStream(absolute_path + "/criminals/", camera_urls)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server)
    logging.info("WebSocket server started. Awaiting client connections...")
    loop.run_until_complete(stream.multiple_cameras())
    loop.run_forever()
