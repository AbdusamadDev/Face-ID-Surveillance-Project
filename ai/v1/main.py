import asyncio
from camera import CameraConnection
from recognition import FaceRecognition
from stream import MultipleStream
from webserver import WebSocket
import websockets

print("main.py" + "\n" * 5)


async def main():
    # Connect to the camera
    camera_connection = CameraConnection(["http://192.168.1.142:5000/video"])
    await camera_connection.connect_all()


    face_recognition = FaceRecognition("../../media")
    websocket_server = WebSocket()
    server = await websockets.serve(websocket_server.handler, websocket_server.host, websocket_server.port)
    multi_stream = MultipleStream(camera_connection.cameras, face_recognition)
    multi_stream.process_camera(multi_stream.cameras[0])

    # async def run_multi_stream():
    #     multi_stream.run()
    # multi_stream_task = asyncio.create_task(run_multi_stream())
    # await multi_stream_task

asyncio.run(main())
