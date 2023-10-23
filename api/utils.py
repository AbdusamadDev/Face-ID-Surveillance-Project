import psycopg2
import numpy as np
import os
import insightface
import socket
import faiss
from dotenv import load_dotenv

load_dotenv()


def characters() -> list:
    letters = [chr(i) for i in list(range(97, 123)) + list(range(65, 91))]
    underscore = ["_"]
    digits = [str(k) for k in list(range(10))]
    return letters + underscore + digits


def host():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        public_ip = "http://" + str(s.getsockname()[0]) + ":8000"
    except Exception:
        public_ip = "Unable to get IP"
    finally:
        s.close()
    return public_ip


def is_similar(new_encoding, threshold=250):
    existing_encodings = get_all_encodings_from_db()
    new_encoding = new_encoding.reshape(1, -1)
    index = faiss.IndexFlatL2(existing_encodings.shape[1])
    index.add(existing_encodings)
    D, I = index.search(new_encoding, 1)
    if D[0][0] < threshold:
        return True

    return False


def get_face_encoding(img_np):
    model = insightface.app.FaceAnalysis()
    model.prepare(ctx_id=0)
    faces = model.get(img_np)
    if len(faces) == 0:
        print("No face found")
        return None
    return faces


def get_all_encodings_from_db():
    try:
        conn = psycopg2.connect(
            dbname=os.environ.get("DBNAME"),
            user=os.environ.get("DBUSER"),
            password=os.environ.get("DBPASSWORD"),
            host=os.environ.get("DBHOST"),
            port=os.environ.get("DBPORT"),
        )
        cursor = conn.cursor()
        cursor.execute("SELECT encoding FROM api_encodings")
        encoding_list = cursor.fetchall()
        cursor.close()
        conn.close()
        encodings = np.array([np.array(item[0]) for item in encoding_list])
        return encodings
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


allowed_characters = characters()
host_address = host()
process_image = get_face_encoding
is_already_in = is_similar
