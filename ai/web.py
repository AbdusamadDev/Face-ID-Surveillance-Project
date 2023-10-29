class WebSocketManager:
    def __init__(self):
        self.connections = set()

    async def register(self, websocket):
        self.connections.add(websocket)

    async def unregister(self, websocket):
        self.connections.remove(websocket)

    async def send_to_all(self, message):
        if self.connections:
            for connection in self.connections:
                if connection.open:
                    await connection.send(message)
