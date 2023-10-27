import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


class Database:
    def __init__(self):
        self.dbname = os.environ.get("DBNAME")
        self.user = os.environ.get("DBUSER")
        self.password = os.environ.get("DBPASSWORD")
        self.host = os.environ.get("DBHOST")
        self.port = os.environ.get("DBPORT")

    def _db_connect(self):
        return psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )

    def _execute_query(self, query, params):
        try:
            conn = self._db_connect()
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()
            conn.close()
            return result
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def get_details(self, first_name):
        query = "SELECT * FROM api_criminals WHERE id=%s"
        rows = self._execute_query(query, (first_name,))
        return rows[0] if rows else []

    def get_camera(self, url):
        query = "SELECT * FROM api_camera WHERE url=%s"
        rows = self._execute_query(query, (url,))
        return rows[0] if rows else []

    def get_camera_urls(self):
        query = "SELECT url FROM api_camera"
        rows = self._execute_query(query, ())
        return [row[0] for row in rows] if rows else []

    def get_encodings(self):
        query = self._execute_query(
            """SELECT criminal_id, encoding FROM api_encodings;""", ()
        )
        return [row[-1] for row in query], [rower[0] for rower in query]


if __name__ == "__main__":
    database = Database()
    print(database.get_encodings())
