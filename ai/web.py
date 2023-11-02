import logging
import json
from geopy.distance import geodesic


class WebSocketManager:
    def __init__(self):
        self.connections = set()
        self.locations = {}

    async def register(self, websocket, location):
        self.connections.add(websocket)
        self.locations[websocket] = location
        logging.info(
            f"Registered a client. Current connections: {len(self.connections)}"
        )
        logging.info(self.connections)

    async def unregister(self, websocket):
        if websocket in self.connections:
            self.connections.remove(websocket)
            if websocket in self.locations:
                del self.locations[websocket]
            logging.info(
                f"Unregistered a client. Remaining connections: {len(self.connections)}"
            )
        else:
            logging.warning(f"Trying to unregister a websocket that's not registered.")

    async def send_to_all(self, message):
        for connection in self.connections:
            if connection.open:
                await connection.send(
                    json.dumps({"event": "all_clients", "context": message})
                )
            else:
                await self.unregister(connection)

    async def send_to_nearest_client(self, message, location):
        nearest_client, _ = self.find_nearest_client(location)
        if nearest_client and nearest_client.open:
            await nearest_client.send(
                json.dumps({"event": "nearest_client", "context": message})
            )

    async def print_client_locations(self):
        nearest_client, nearest_distance = self.find_nearest_client()
        if nearest_client is not None:
            msg = f"Nearest client is at {nearest_client.remote_address} with distance {nearest_distance} km"
            await self.send_to_nearest_client(
                json.dumps({"event": "nearest_client", "message": msg})
            )

    def find_nearest_client(self, location):
        nearest_distance = float("inf")
        nearest_client = None
        for ws, location in self.locations.items():
            if not isinstance(location, tuple) or len(location) != 2:
                logging.error(type(location))
                logging.error(f"Invalid location data: {location}")
                continue

            try:
                lat, long = float(location[0]), float(location[1])
            except ValueError:
                logging.error(f"Invalid coordinates: {location}")
                continue

            location = (lat, long)
            distance = geodesic(location, location).kilometers

            if distance < nearest_distance:
                nearest_distance = distance
                nearest_client = ws

        return nearest_client, nearest_distance
