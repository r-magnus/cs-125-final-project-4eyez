# Gabriel Leung <gleung@westmont.edu>
# Ryan Magnuson <rmagnuson@westmont.edu>

## SETUP ##
import uvicorn
from fastapi import FastAPI
import mysql.connector
import os
from dotenv import load_dotenv
from pydantic import BaseModel

## PYDANTIC ##
class Query(BaseModel):
    query: str

## SQL FUNCTIONS ##
def connect_sql():
    try:
        cnx = mysql.connector.connect(
            user=USERNAME,
            password=PASSWORD,
            host=HOST,
            database=DB
        )
        return cnx
    except Exception as e:
        print(f"Error connecting to DB: {e}")

def ask_db(q: str):
    """
    A "safe" method that only allows SELECT-type queries on the current DB.
    """
    try:
        if q.split(" ")[0] != "SELECT" or ';' in q:
            raise Exception("That's not allowed.")
        crs = cnx.cursor()
        crs.execute(q)
        res = crs.fetchall()
        crs.close()

        return res
    except Exception as e:
        print(f"Error with query: {e}")


## API ##
app = FastAPI()

@app.get("/")
def main():
    return {"message": "CS125 Paper Youth Group DB",
            "note": "THIS IS A FAKE DATABASE FOR LEARNING PURPOSES ONLY"}

@app.get("/query")
async def query(q: Query):
    response = ask_db(q.query)
    return response

## MAIN ##
if __name__ == '__main__':
    load_dotenv()

    USERNAME = os.getenv("USERNAME")
    PASSWORD = os.getenv("PASSWORD")
    HOST = os.getenv("HOST")
    DB = os.getenv("DB")

    cnx = connect_sql()

    uvicorn.run(app, host=HOST, port=8000)

