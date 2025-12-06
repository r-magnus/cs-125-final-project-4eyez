# Gabriel Leung <gleung@westmont.edu>
# Ryan Magnuson <rmagnuson@westmont.edu>

## SETUP ##
import uvicorn
from fastapi import FastAPI, HTTPException
import mysql.connector
import os
from dotenv import load_dotenv
from pydantic import BaseModel
import redis
from attendance import redis_connect, checkin, checkout, get_attendance, get_attendance_count, end_event
from mysql_connect import connect_sql

## PYDANTIC ##
class Query(BaseModel):
    query: str

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

    uvicorn.run(app, host=HOST, port=8000)

