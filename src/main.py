# Gabriel Leung <gleung@westmont.edu>
# Ryan Magnuson <rmagnuson@westmont.edu>
## SETUP ##
import uvicorn
from fastapi import FastAPI, HTTPException
import mysql.connector
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from pymongo import MongoClient


from event import router as event_router

## API ##
app = FastAPI()
app.include_router(event_router)
import redis
from attendance import redis_connect, checkin, checkout, get_attendance, get_attendance_count, end_event
from mysql_connect import connect_sql

## PYDANTIC ##
class Query(BaseModel):
    query: str


##GLOBALS##
cnx = None  # MySQL connection
mongo_client = None
mongo_db = None
event_types_col = None
event_custom_col = None

USERNAME = None
PASSWORD = None
HOST = None
DB = None
MONGO_URI = None


class AttendanceItem(BaseModel):
    event_id: int
    student_id: int | None = None

## SQL FUNCTIONS ##

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

#MONGODB##

def connect_mongo():
    global mongo_client,mongo_db,event_types_col,event_custom_col
    try:
        mongo_client = MongoClient(MONGO_URI)
        mongo_db = mongo_client["finalProj_workorder"]

        # Collections
        event_types_col = mongo_db["eventTypes"]
        event_custom_col = mongo_db["eventCustomData"]

        # Indexes
        event_types_col.create_index("typeId", unique=True)
        event_custom_col.create_index("meetId", unique=True)
        event_custom_col.create_index("typeId")

        print(" Connected to MongoDB Atlas!")
        return mongo_client, mongo_db, event_types_col, event_custom_col
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise


##END POINTS##
@app.get("/")
def main():
    return {"message": "CS125 Paper Youth Group DB",
            "note": "THIS IS A FAKE DATABASE FOR LEARNING PURPOSES ONLY"}

@app.get("/query")
async def query(q: Query):
    response = ask_db(q.query)
    return response


@app.get("/test-mongo")
def test_mongo():
    try:
        if mongo_client is None:
            raise Exception("MongoDB client not initialized.")
        mongo_client.admin.command("ping")
        return {"message": "MongoDB connection OK"}
    except Exception as e:
        return {"error": str(e)}

## MAIN ##
if __name__ == '__main__':

    load_dotenv()
# Redis #
@app.post("/attendance/{ep}")
async def redis_post(ep: str, a: AttendanceItem):
    """
    Handles posts to Redis, where "ep" is "endpoint"
    """
    if ep == "checkin":
        checkin(r, a.event_id, a.student_id)
    elif ep == "checkout":
        checkout(r, a.event_id, a.student_id)
    elif ep == "end_event":
        end_event(r, a.event_id)
    else:
        raise HTTPException(status_code=404, detail="Page not found")

@app.get("/attendance/{ep}")
async def redis_get(ep: str, a: AttendanceItem):
    """
    Handles "get" requests from Redis, where "ep" is "endpoint"
    """
    if ep == "get":
        return get_attendance(r, a.event_id) # student_id unneeded (?)
    elif ep == "get_count":
        return get_attendance_count(r, a.event_id)
    else:
        raise HTTPException(status_code=404, detail="Page not found")

## MAIN ##
if __name__ == '__main__':
    cnx = connect_sql()
    r = redis_connect()

    HOST = os.getenv("HOST")
    DB = os.getenv("DB")
    MONGO_URI = os.getenv("MONGO_URI")
    # cnx = connect_sql()
    connect_mongo()

    uvicorn.run(app, host=HOST, port=8000)


