# Gabriel Leung <gleung@westmont.edu>
# Ryan Magnuson <rmagnuson@westmont.edu>
## SETUP ##
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from pymongo import MongoClient
from src.event import router as event_router
from strawberry.fastapi import GraphQLRouter
from src.graphql_schema.schema import custom_schema
import redis
from src.attendance import redis_connect, checkin, checkout, get_attendance, get_attendance_count, end_event
from src.mysql_connect import connect_sql

## API ##
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(event_router)
graphql_app = GraphQLRouter(custom_schema)
app.include_router(graphql_app, prefix="/graphql")

## PYDANTIC ##
class Query(BaseModel):
    query: str

class EventItem(BaseModel):
    event_id: int


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


## SQL FUNCTIONS ##
# def connect_sql():
#     global cnx
#     try:
#         cnx = mysql.connector.connect(
#             user=USERNAME,
#             password=PASSWORD,
#             host=HOST,
#             database=DB
#         )
#         return cnx
#     except Exception as e:
#         print(f"Error connecting to DB: {e}")
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


##connect##
@app.on_event("startup")
def startup_event():
    """
    This runs when uvicorn starts (including in Docker).
    Initializes env, MySQL, Redis, and Mongo.
    """
    global cnx, r, MONGO_URI

    load_dotenv()
    MONGO_URI = os.getenv("MONGO_URI")

    # MySQL
    cnx = connect_sql()
    if cnx:
        print(" Connected to MySQL in startup_event")
    else:
        print(" Failed to connect to MySQL in startup_event")

    # Redis
    r = redis_connect()
    print(" Connected to Redis in startup_event")

    # Mongo
    connect_mongo()



##END POINTS##
@app.get("/")
def main():
    return {"message": "CS125 Paper Youth Group DB",
            "note": "THIS IS A FAKE DATABASE FOR LEARNING PURPOSES ONLY"}

# @app.get("/query")
# async def query(q: Query):
#     response = ask_db(q.query)
#     return response

@app.get("/events/{ep}")
async def events(ep: str, event: EventItem):
    crs = cnx.cursor()
    if ep == "get_active":
        q = """
        SELECT * FROM Event e
        WHERE e.endDate > CURRENT_DATE()
        """
        crs.execute(q)
        res = crs.fetchall()
        crs.close()
        return res

    elif ep == "get_signees":
        q = """
        SELECT * FROM Person p
        JOIN MeetingSignUpItem m ON m.signeeId = p.personId
        WHERE m.meetingId = %s
        """
        crs.execute(q, (event.event_id,))
        res = crs.fetchall()
        crs.close()
        return res

    elif ep == "get_author":
        q = """
        SELECT * FROM Person p
        JOIN Event e ON e.createdByID = p.personId
        WHERE e.meetId = %s
        """
        crs.execute(q, event.event_id)
        res = crs.fetchall()
        crs.close()
        return res

@app.get("/people/{ep}")
async def people(ep: str):
    crs = cnx.cursor()
    if ep == "students":
        q = """
        SELECT * FROM Student s
        JOIN Person p ON s.personId = p.personId
        WHERE s.personId = p.personId
        """
        crs.execute(q)
        res = crs.fetchall()
        crs.close()
        return res
    elif ep == "volunteers":
        q = """
        SELECT * FROM Volunteer s
        JOIN Person p ON s.personId = p.personId
        WHERE s.personId = p.personId
        """
        crs.execute(q)
        res = crs.fetchall()
        crs.close()
        return res
    elif ep == "admins":
        q = """
        SELECT * FROM Admin s
        JOIN Person p ON s.personId = p.personId
        WHERE s.personId = p.personId
        """
        crs.execute(q)
        res = crs.fetchall()
        crs.close()
        return res


@app.get("/test-mongo")
def test_mongo():
    try:
        if mongo_client is None:
            raise Exception("MongoDB client not initialized.")
        mongo_client.admin.command("ping")
        return {"message": "MongoDB connection OK"}
    except Exception as e:
        return {"error": str(e)}

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
# if __name__ == '__main__':
#     load_dotenv()
#     cnx = connect_sql()
#     r = redis_connect()
#
#     HOST = os.getenv("HOST")
#     DB = os.getenv("DB")
#     MONGO_URI = os.getenv("MONGO_URI")
#     # cnx = connect_sql()
#     connect_mongo()
#
#     uvicorn.run(app, host=HOST, port=8000)

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)



