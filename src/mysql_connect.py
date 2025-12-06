import mysql.connector
import os
from dotenv import load_dotenv

def connect_sql():
    try:
        load_dotenv()

        USERNAME = os.getenv("USERNAME")
        PASSWORD = os.getenv("PASSWORD")
        HOST = os.getenv("HOST")
        DB = os.getenv("DB")

        cnx = mysql.connector.connect(
            user=USERNAME,
            password=PASSWORD,
            host=HOST,
            database=DB
        )

        return cnx
    except Exception as e:
        print(f"Error connecting to DB: {e}")