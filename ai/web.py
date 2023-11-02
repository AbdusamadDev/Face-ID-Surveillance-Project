import asyncio
import json
import logging
from geopy.distance import geodesic


logging.basicConfig(level=logging.INFO)


class WebSocketManager:
    def __init__(self):
        self.clients = {}

    async def register(self, websocket, location, state):
        self.clients[websocket] = (location, state)
        logging.info(f"Client registered. Total clients: {len(self.clients)}.")

    async def unregister(self, websocket):
        if websocket in self.clients:
            del self.clients[websocket]
            logging.info(f"Client unregistered. Total clients: {len(self.clients)}.")
        else:
            logging.warning("Attempted to unregister an unknown client.")

    async def send_to_nearest_apk_client(self, message, location):
        nearest_client, _ = self.find_nearest_client(location, client_type="apk")
        if nearest_client:
            await nearest_client.send(json.dumps(message))

    async def broadcast_to_web_clients(self, message):
        web_clients = [
            ws for ws, (_, state) in self.clients.items() if state == "web" and ws.open
        ]
        if web_clients:
            await asyncio.gather(
                *(client.send(json.dumps(message)) for client in web_clients)
            )

    def find_nearest_client(self, location, client_type=None):
        nearest_client = None
        nearest_distance = float("inf")
        for client, (client_loc, state) in self.clients.items():
            if client_type and state != client_type:
                continue
            distance = geodesic(location, client_loc).kilometers
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_client = client
        return nearest_client, nearest_distance


websocket_manager = WebSocketManager()
