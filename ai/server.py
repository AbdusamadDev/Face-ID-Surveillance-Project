# from imutils.video import VideoStream
# from urllib.parse import urlparse
# from datetime import datetime
# import websockets
# import logging
# import asyncio
# import json
# import cv2
# import os

# from ai.face_recognition import FaceRecognition
# from ai.socket_manager import WebSocketManager
# from ai.alert_manager import AlertManager
# from ai.utils import host_address
# from ai.train import FaceTrainer
# from ai.models import Database
# from dotenv import load_dotenv

# load_dotenv()
# logging.basicConfig(level=logging.DEBUG)
# root_dir = os.getenv("BASE_DIR")


# class MainStream:
#     def __init__(self):
#         self.database = Database()
#         self.websocket_manager = WebSocketManager()
#         print(root_dir)
#         self.trainer = FaceTrainer(os.path.join(root_dir, "media/criminals"))
#         self.index = self.trainer.index
#         self.known_face_names = self.trainer.known_face_names
#         self.face_model = self.trainer.face_model
#         self.alert_manager = AlertManager(self.websocket_manager)
#         self.face_recognition = FaceRecognition(self)
#         self.processing_queue = asyncio.Queue()
#         self.tasks = []

#     async def capture_and_send_frames(self, url):
#         cap = VideoStream(url, codec='h264', fps=30).start()

#         try:
#             while True:
#                 frame = cap.read()
#                 if frame is not None:
#                     asyncio.create_task(self.process_frame(frame, url))
#                 await asyncio.sleep(0.01)  # Adjust the sleep time based on your needs
#         except asyncio.CancelledError:
#             print(f"Task for {url} has been cancelled.")
#         finally:
#             cap.stop()

#     async def process_frames(self):
#         """Processes frames from all cameras."""
#         last_screenshot_time = datetime.now()
#         screenshot_interval = 5
#         while True:
#             frame, url = await self.processing_queue.get()
#             self.face_recognition.current_frame = frame
#             current_time = datetime.now()
#             faces = self.face_model.get(frame)
#             tasks = [self.face_recognition.process_face(face) for face in faces]
#             results = await asyncio.gather(*tasks)
#             for name in results:
#                 if name is not None:
#                     await self.alert_manager.handle_alert(
#                         frame=frame, detected_face=name, url=url
#                     )
#             if (
#                 current_time - last_screenshot_time
#             ).total_seconds() >= screenshot_interval:
#                 print("\n"*5)
#                 self.save_screenshot(frame, url, current_time)
#                 last_screenshot_time = current_time

#     async def reload_face_encodings_periodically(self):
#         while True:
#             self.index, self.known_face_names = self.trainer.load_face_encodings(
#                 os.path.join(root_dir, "media/criminals")
#             )
#             (
#                 self.face_recognition.index,
#                 self.face_recognition.known_face_names,
#             ) = self.trainer.load_face_encodings(
#                 os.path.join(root_dir, "media/criminals")
#             )
#             await asyncio.sleep(60)

#     async def start_camera_streams(self):
#         tasks = [
#             asyncio.create_task(self.capture_and_send_frames(url))
#             for url in database.get_camera_urls()
#         ]
#         tasks.append(asyncio.create_task(self.process_frames()))
#         await asyncio.gather(*tasks)

#     async def reconnect_cameras_periodically(self, interval=30):
#         while True:
#             print("Length of tasks: ", len(self.tasks))
#             for task in self.tasks:
#                 task.cancel()

#             await asyncio.gather(*self.tasks, return_exceptions=True)
#             self.tasks = []  # Clear the tasks list after they are cancelled
#             task = asyncio.create_task(self.start_camera_streams())
#             self.tasks.append(task)
#             print("Length of tasks: ", len(self.tasks))
#             await asyncio.sleep(interval)

#     def save_screenshot(self, frame, url, timestamp):
#         """Saves a screenshot with a specific naming format, including only the IP address from the URL."""
#         parsed_url = urlparse(url)
#         ip_address = parsed_url.hostname
#         formatted_time = timestamp.strftime("%Y-%m-%d|%H-%M-%S")
#         filename = f"{formatted_time}|{ip_address}.jpg"
#         directory = os.path.join(root_dir)
#         os.makedirs(directory, exist_ok=True)  # Ensure directory exists
#         filepath = os.path.join(directory, filename)
#         print(filename, filepath, directory)
#         print("\n" * 5)
#         cv2.imwrite(filepath, frame)


# async def websocket_server(websocket, path):
#     manager = stream.websocket_manager
#     try:
#         message = await websocket.recv()
#         data = json.loads(message)
#         token = data.get("token", None)
#         if token is not None:
#             if database.is_authenticated(token):
#                 await manager.register(websocket, data)
#             else:
#                 await websocket.send(json.dumps({"msg": "Invalid token provided!"}))
#                 await manager.unregister(websocket)
#         else:
#             await websocket.send(json.dumps({"msg": "Token is not provided!"}))
#             await manager.unregister(websocket)
#         while True:
#             await asyncio.sleep(1000)
#     except websockets.exceptions.ConnectionClosedError as e:  # type: ignore
#         await manager.unregister(websocket)
#     except json.JSONDecodeError as e:
#         await manager.unregister(websocket)
#     finally:
#         await manager.unregister(websocket)


# def list_image_paths(directory):
#     relative_paths = [
#         os.path.join(directory, f)
#         for f in os.listdir(directory)
#         if os.path.isfile(os.path.join(directory, f))
#     ]
#     absolute_paths = [
#         path.replace("../", host_address + "/", 1) for path in relative_paths
#     ]
#     return absolute_paths


# async def send_image_paths(websocket, path):
#     sent_image_paths = set()
#     connection_time = datetime.now()
#     screenshots_dir = "/media/screenshots/suspends/"

#     while True:
#         current_image_files = set(
#             f
#             for f in os.listdir(screenshots_dir)
#             if os.path.isfile(os.path.join(screenshots_dir, f))
#         )
#         current_image_paths = {
#             os.path.join(screenshots_dir, f) for f in current_image_files
#         }
#         new_paths = current_image_paths - sent_image_paths
#         for file_path in new_paths:
#             creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
#             if creation_time > connection_time:
#                 image_name = os.path.basename(file_path)
#                 camera_url = image_name.split("|")[-1].rstrip(".jpg")
#                 camera_object = database.get_by_similar(camera_url)
#                 image_url = file_path.replace("../", host_address + "/", 1)
#                 camera_object["image"] = (
#                     host_address + "/media/" + camera_object.get("image")
#                 )
#                 message = {"image_path": image_url, "camera_object": camera_object}
#                 await websocket.send(json.dumps(message))
#                 sent_image_paths.add(file_path)
#         await asyncio.sleep(5)


# async def image_path_server(websocket, path):
#     consumer_task = asyncio.ensure_future(send_image_paths(websocket, path))
#     done, pending = await asyncio.wait(
#         [consumer_task], return_when=asyncio.FIRST_COMPLETED
#     )
#     for task in pending:
#         task.cancel()


# async def main():
#     ws_server = await websockets.serve(websocket_server, "0.0.0.0", 5000)
#     img_server = await websockets.serve(image_path_server, "0.0.0.0", 5678)
#     reload_encodings_task = asyncio.create_task(
#         stream.reload_face_encodings_periodically()
#     )
#     camera_reconnection = asyncio.create_task(stream.reconnect_cameras_periodically())
#     await asyncio.gather(
#         ws_server.wait_closed(),
#         img_server.wait_closed(),
#         reload_encodings_task,
#         camera_reconnection,
#     )


# if __name__ == "__main__":
#     database = Database()

#     stream = MainStream()
#     logging.basicConfig(level=logging.INFO)
#     asyncio.run(main())


from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError
from dotenv import load_dotenv
from datetime import datetime
from ai.models import Database
import websockets
import logging
import asyncio
import json
import os


load_dotenv()


class WebSocketServer:
    def __init__(self, addr: tuple) -> None:
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
                logging.info(
                    " Target client address: " + str(input_client.remote_address)
                )
                logging.info(" Keeping alive: [%s]" % datetime.now())
                logging.info(" Client addresses: " + str(self.clients))
                newest_image_path = os.path.join(sorted(os.listdir(base_path))[-1])
                await self.broadcast(
                    json.dumps(
                        {
                            "image": str(
                                "http://0.0.0.0:8000/media/screenshots/suspends/"
                                + newest_image_path
                            )
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
                print("Path :::  ", base_path)
                print("Base DR: ", os.getenv("BASE_DIR"))
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
