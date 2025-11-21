# Gabriel Leung <gleung@westmont.edu>
# Ryan Magnuson <rmagnuson@westmont.edu>

## SETUP ##
import uvicorn
from fastapi import FastAPI
import mysql.connector
import os
from dotenv import load_dotenv

## SQL FUNCTIONS ##
def connect_sql():
    cnx = mysql.connector.connect(
        user=USERNAME,
        password=PASSWORD,
        host=HOST,
        database=DB
    )
    return cnx

def ask_db(q: str):

    return ""


## API ##
app = FastAPI()

@app.get("/")
def main():
    return {"message": "CS125 Paper Youth Group DB"}

@app.get("/query/{statement}")
async def query(statement: str):
    response = ask_db(statement)
    return ""

## MAIN ##
if __name__ == '__main__':
    load_dotenv()

    USERNAME = os.getenv("USERNAME")
    PASSWORD = os.getenv("PASSWORD")
    HOST = os.getenv("HOST")
    DB = os.getenv("DB")

    cnx = connect_sql()

    uvicorn.run(app, host=HOST, port=8000)

