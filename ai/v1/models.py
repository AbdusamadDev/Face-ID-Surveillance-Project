import sqlite3

print("models.py" + "\n" * 5)


def get_details(first_name):
    connection = sqlite3.connect("../../db.sqlite3")
    cursor = connection.cursor()
    query = cursor.execute("""SELECT * FROM api_criminals WHERE first_name=?""",
                           (first_name,))
    if query:
        return query.fetchall()[0]
    return []


def get_camera(url):
    connection = sqlite3.connect("../db.sqlite3")
    cursor = connection.cursor()
    query = cursor.execute("""SELECT * FROM api_camera WHERE url=?""", (url,))
    if query:
        return query.fetchall()[0]
    return []
