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
            self.cursor = cursor
            cursor.execute(query, params)
            result = cursor.fetchall()
            conn.commit()
            conn.close()
            return result
        except Exception as e:
            print(f"An error occurred: {e}")
            conn.close()
            return None

    def get_details(self, employee_id):
        query = "SELECT * FROM api_criminals WHERE id=%s"
        rows = self._execute_query(query, (employee_id,))
        labels = [
            "id",
            "first_name",
            "last_name",
            "age",
            "description",
            "date_created",
            "middle_name",
        ]
        if rows is not None:
            try:
                rows_dict = {label: row for label, row in zip(labels, rows[0])}
                print(rows_dict)
                return rows_dict
            except:
                print(rows)
        return None

    def get_camera(self, url):
        query = "SELECT * FROM api_camera WHERE url=%s"
        rows = self._execute_query(query, (url,))
        labels = ["id", "name", "url", "longitude", "latitude", "image"]
        if rows is not None:
            rows_dict = {label: row for label, row in zip(labels, rows[0])}
            return rows_dict
        return None
    
    def get_camera_by_id(self, pk):
        query = "SELECT * FROM api_camera WHERE id=%s"
        rows = self._execute_query(query, (pk,))
        labels = ["id", "name", "url", "longitude", "latitude", "image"]
        if rows is not None:
            rows_dict = {label: row for label, row in zip(labels, rows[0])}
            return rows_dict
        return None

    def get_camera_urls(self):
        query = "SELECT url FROM api_camera"
        rows = self._execute_query(query, ())
        return [row[0] for row in rows] if rows else []

    def get_encodings(self):
        query = self._execute_query(
            """SELECT criminal_id, encoding FROM api_encodings;""", ()
        )
        return [row[-1] for row in query], [rower[0] for rower in query]

    def insert_records(self, image, date_recorded, criminal, camera):
        connection = self._db_connect()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO api_criminalsrecords (image_path, date_recorded, criminal_id, camera_id)
            VALUES (%s, %s, %s, %s)
            """,
            (image, date_recorded, criminal, camera),
        )
        connection.commit()

    def get_by_similar(self, partial_url):
        query = """SELECT * FROM api_camera WHERE url ILIKE %s;"""
        connection = self._db_connect()
        cursor = connection.cursor()

        # Add '%' wildcard before and after the partial_url to find similar matches
        like_pattern = f"%{partial_url}%"

        cursor.execute(query, (like_pattern,))
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        keys = ["id", "name", "url", "longitude", "latitude", "image"]
        if results:
            results = results[0]
        context_zip = list(zip(keys, results))
        context = {key: val for key, val in context_zip}

        return context

    def add_temp(self):
        last_created_record = self._execute_query(
            """SELECT * FROM api_criminalsrecords ORDER BY id DESC LIMIT 1;""",
            tuple(),
        )
        if last_created_record:
            last_created_record = last_created_record[0][0]
        conn = self._db_connect()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO api_temprecords (record_id) VALUES (%s);""",
            (last_created_record,),
        )
        conn.commit()
        return last_created_record

    def is_authenticated(self, token):
        token = self._execute_query(
            """SElECT user_id FROM authtoken_token WHERE key=%s;""", (token,)
        )
        if token:
            return True
        return False

    def add_web_temp_records(
        self, criminal_id, camera_id, screenshot_url, date_created
    ):
        conn = self._db_connect()
        cursor = conn.cursor()
        self.cursor = cursor
        cursor.execute(
            """INSERT INTO api_webtemprecords (criminal_id, camera_id, 
            image, date_created) VALUES (%s, %s, %s, %s);""",
            (criminal_id, camera_id, screenshot_url, date_created),
        )
        conn.commit()
        conn.close()


if __name__ == "__main__":
    database = Database()
    print(database.is_authenticated("459ede94edbd1c8a1fc1a47194bebaf79523853e"))
