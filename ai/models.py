import sqlite3


def get_details(first_name):
    connection = sqlite3.connect("../db.sqlite3")
    cursor = connection.cursor()
    query = cursor.execute(
        """SELECT * FROM api_criminals WHERE first_name=?""", (first_name,)
    ).fetchall()
    if query:
        return query[0]
    return []


def get_camera(url):
    connection = sqlite3.connect("../db.sqlite3")
    cursor = connection.cursor()
    query = cursor.execute(
        """SELECT * FROM api_camera WHERE url=?""", (url,)
    ).fetchall()
    if query:
        return query[0]
    return []

def get_camera_urls():
    connection = sqlite3.connect("../db.sqlite3")
    cursor = connection.cursor()
    cameras = cursor.execute("""SELECT url FROM api_camera""").fetchall()
    return [camera[0] for camera in cameras]
