from geopy.distance import geodesic


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

    async def unregister(self, websocket):
        # Removing the websocket and updating locations if it's an APK client
        if websocket in self.apk_clients:
            self.apk_clients.remove(websocket)
            del self.locations[websocket]
        elif websocket in self.web_clients:
            self.web_clients.remove(websocket)

    async def send_to_nearest_client(self, message, camera_location):
        self.refresh_clients()
        nearest_client, _ = self.find_nearest_client(camera_location)
        if nearest_client:
            if nearest_client.open:
                await nearest_client.send(message)

    async def send_to_all(self, message):
        for web_client in self.web_clients:
            if web_client.open:
                await web_client.send(message)

    def find_nearest_client(self, camera_location):
        nearest_distance = float("inf")
        nearest_client = None
        for ws, location in self.locations.items():
            if not isinstance(location, tuple) or len(location) != 2:
                continue

            try:
                lat, long = float(location[0]), float(location[1])
            except ValueError:
                continue

            location = (lat, long)
            distance = geodesic(camera_location, location).kilometers

            if distance < nearest_distance:
                nearest_distance = distance
                nearest_client = ws

        return nearest_client, nearest_distance

    def refresh_clients(self):
        for ws in list(self.apk_clients):
            if not ws.open:
                self.apk_clients.remove(ws)
