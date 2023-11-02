import logging
import json
from geopy.distance import geodesic


class WebSocketManager:
    def __init__(self):
        self.clients = {}  # { websocket: location }

    async def register(self, websocket, location):
        self.clients[websocket] = location
        logging.info(f"Registered a client. Total clients: {len(self.clients)}")

    async def unregister(self, websocket):
        if websocket in self.clients:
            del self.clients[websocket]
            logging.info(
                f"Unregistered a client. Remaining clients: {len(self.clients)}"
            )
        else:
            logging.warning("Unregistering an unrecognized client.")

    async def send_to_nearest_client(self, message, location):
        nearest_client, _ = self.find_nearest_client(location)
        if (
            nearest_client
            and nearest_client.open
            and self.clients[nearest_client][1] == "apk"
        ):
            await nearest_client.send(
                json.dumps({"event": "nearest_client", "context": message})
            )

    async def send_to_all(self, message):
        disconnected = []
        for client in self.clients:
            print(self.clients)
            if client.open and self.clients[client][1] == "web":
                await client.send(
                    json.dumps({"event": "all_clients", "context": message})
                )
            else:
                disconnected.append(client)

        for client in disconnected:
            await self.unregister(client)

    def find_nearest_client(self, loc):
        nearest_distance = float("inf")
        nearest_client = None
        for client, client_loc in self.clients.items():
            try:
                distance = geodesic(loc, client_loc).kilometers
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_client = client
            except (ValueError, TypeError):
                logging.error(f"Invalid location or coordinates: {client_loc}")

        return nearest_client, nearest_distance
