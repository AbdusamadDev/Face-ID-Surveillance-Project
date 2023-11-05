import logging
from geopy.distance import geodesic


logging.basicConfig(level=logging.INFO)


class WebSocketManager:
    def __init__(self):
        self.web_clients = set()
        self.apk_clients = set()
        self.locations = {}

    async def register(self, websocket, data):
        if data["state"] == "apk":
            self.apk_clients.add(websocket)
            self.locations[websocket] = (data["latitude"], data["longitude"])
        else:
            self.web_clients.add(websocket)
        logging.info(
            f"Registered a {data['state']} client. Total web: {len(self.web_clients)}, apk: {len(self.apk_clients)}"
        )
        print(str(websocket.path))
        print(data)

    async def unregister(self, websocket):
        if websocket in self.apk_clients:
            self.apk_clients.remove(websocket)
            del self.locations[websocket]
        elif websocket in self.web_clients:
            self.web_clients.remove(websocket)
        logging.info(
            f"Unregistered a client. Remaining web: {len(self.web_clients)}, apk: {len(self.apk_clients)}"
        )

    async def send_to_all(self, message):
        for web_client in self.web_clients:
            if web_client.open:
                await web_client.send(message)

    async def send_to_nearest_client(self, message):
        nearest_client, _ = self.find_nearest_client()
        if nearest_client and nearest_client.open:
            await nearest_client.send(message)

    def find_nearest_client(self):
        camera_location = (41.0649, 71.4782)
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
            distance = geodesic(camera_location, location).kilometers

            if distance < nearest_distance:
                nearest_distance = distance
                nearest_client = ws

        return nearest_client, nearest_distance
