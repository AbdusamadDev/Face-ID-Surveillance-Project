import websockets

print("webserver.py" + "\n" * 5)


class WebSocket:
    def __init__(self, host="0.0.0.0", port=12345):
        self.host = host
        self.port = port
        self.clients = set()

    async def register(self, websocket):
        self.clients.add(websocket)

    async def unregister(self, websocket):
        self.clients.remove(websocket)

    async def send_to_all(self, message):
        for client in self.clients:
            await client.send(message)

    async def handler(self, websocket, path):
        await self.register(websocket)
        try:
            await websocket.recv()
        except websockets.ConnectionClosedOK:
            pass
        finally:
            await self.unregister(websocket)
