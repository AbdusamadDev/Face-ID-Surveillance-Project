from temp2 import MainStream  # I assume you meant ai.py, not temp2
from path import absolute_path
import asyncio
import websockets


class WebSocketServer:
    def __init__(self):
        self.clients = set()

    async def register(self, websocket):
        self.clients.add(websocket)

    async def unregister(self, websocket):
        self.clients.remove(websocket)
        await websocket.close()

    async def send_to_all(self, message):
        if self.clients:
            await asyncio.gather(*(client.send(message) for client in self.clients))

    async def handler(self, websocket, path):
        await self.register(websocket)
        try:
            async for message in websocket:
                await self.send_to_all(message)
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            await self.unregister(websocket)


if __name__ == "__main__":
    server = WebSocketServer()
    print("Server starting")
    loop = asyncio.get_event_loop()
    start_server = websockets.serve(server.handler, "localhost", 8765)
    camera_urls = ["http://192.168.1.152:5000/video"]
    stream = MainStream(absolute_path + "/criminals/", camera_urls, websocket=server)
    loop.run_until_complete(start_server)
    face_recognition_task = loop.create_task(stream.multiple_cameras())
    loop.run_forever()
