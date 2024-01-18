from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError
from urllib.parse import urlparse
from dotenv import load_dotenv
from datetime import datetime
from models import Database
import websockets
import logging
import asyncio
import json
import os


load_dotenv()


class WebSocketServer:
    def __init__(self, addr: tuple) -> None:
        logging.basicConfig(level=logging.INFO)
        self.addr = addr
        self.database = Database()
        self.clients = dict()

    async def connect(self, client, key):
        logging.info((" Client connected: " + str(client)))
        self.clients[key] = client

    async def recieve(self, client):
        return await client.recv()

    async def disconnect(self, key):
        try:
            logging.info(" Current clients: " + str(self.clients))
            self.clients.pop(key)
            logging.info(" Clients after disconnection: " + str(self.clients))
        except Exception as e:
            logging.warning(" Error occured: " + str(e))

    async def broadcast(self, data):
        logging.info(f"Sending message: {data}")
        for client in self.clients.values():
            await client.send(data)

    async def communicate(self, input_client, key):
        base_path = os.path.join(os.getenv("BASE_DIR"), "media/screenshots/suspends")
        
        while True:
            try:
                logging.info(" Target client life: " + str(input_client.open))
                logging.info(" Target client address: " + str(input_client.remote_address))
                logging.info(" Keeping alive: [%s]" % datetime.now())
                logging.info(" Client addresses: " + str(self.clients))

                # Iterate through subfolders in 'suspends' folder
                for folder in sorted(os.listdir(base_path)):
                    folder_path = os.path.join(base_path, folder)
                    pk = folder_path.split("/")[-1]
                    # Get the latest image in each subfolder
                    newest_image_path = os.path.join(sorted(os.listdir(folder_path))[-1])
                    print("Newest image path: ", newest_image_path)
                    print("Folder Path: ", folder_path)
                    # Broadcast the information about the latest image
                    await self.broadcast(
                        json.dumps(
                            {
                                "image": str(
                                    f"http://0.0.0.0:8000/media/screenshots/suspends/{pk}/" + newest_image_path,
                                ),
                                "date": str(datetime.now()),
                                "camera": self.database.get_camera_by_id(pk=pk),
                            }
                        )
                    )

                await asyncio.sleep(5)

            except RuntimeError as error:
                logging.info(" Number of clients: " + str(len(self.clients)))
                await self.disconnect(key)
                break
            except Exception as error:
                logging.error(str(error))
                await self.disconnect(key)
                break

    async def handle_server(self, websocket, path):
        while True:
            uuid = path.split("/")
            print("Length of uuid: ", len(uuid))
            if len(uuid) == 2:
                uuid = uuid[-1]
                if uuid in self.clients.keys():
                    await websocket.send(
                        json.dumps({"error": "UUID key is identical, try another key!"})
                    )
                    break
            else:
                await websocket.send(
                    json.dumps(
                        {
                            "error": "Uri must be specified correctly: ws://host:port/<uuid key here>"
                        }
                    )
                )
                break
            message = await websocket.recv()
            data = json.loads(message)
            token = data.get("token", None)
            if token is not None:
                if self.database.is_authenticated(token):
                    await self.connect(websocket, key=uuid)
                else:
                    await websocket.send(json.dumps({"msg": "Invalid token provided!"}))
                    await self.disconnect(uuid)
                    break
            else:
                await websocket.send(json.dumps({"msg": "Token is not provided!"}))
                await self.disconnect(uuid)
                break

            logging.info(" URi: " + str(path))
            try:
                if websocket.open:
                    # Main and simple way to pass user to conversation
                    logging.info(" Number of clients: " + str(len(self.clients)))
                    await self.communicate(websocket, uuid)
                    break
                else:
                    await self.disconnect(uuid)
                    break
            except (ConnectionClosedError, ConnectionClosedOK):
                await self.disconnect(uuid)
                break

    def run(self):
        run_server = websockets.serve(self.handle_server, *self.addr)
        logging.info(f" Websocket server started running on {self.addr}")
        logging.info(" Ctrl+c to get out of loop")
        asyncio.get_event_loop().run_until_complete(run_server)
        asyncio.get_event_loop().run_forever()
