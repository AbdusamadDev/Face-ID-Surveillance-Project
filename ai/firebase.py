import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
import time

cred = credentials.Certificate("creds.json")
firebase_admin.initialize_app(
    cred,
    {
        "databaseURL": "https://bazaarsurveillanceproject-default-rtdb.asia-southeast1.firebasedatabase.app"
    },
)


message = messaging.Message(
    notification=messaging.Notification(
        title="Hello World", body="This is a Hello World message!"
    ),
    topic="global",
)
while True:
    time.sleep(20)
    response = messaging.send(message)
    print(response)
