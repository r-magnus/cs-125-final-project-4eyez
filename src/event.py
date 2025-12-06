from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Literal, Optional
import os

import mysql.connector
from pymongo import MongoClient
from dotenv import load_dotenv



router = APIRouter()

##ENV/ GLOBALS
load_dotenv()

USERNAME= os.getenv('USERNAME')
PASSWORD= os.getenv('PASSWORD')
HOST= os.getenv('HOST')
DB=os.getenv('DB')
MONGO_URI=os.getenv('MONGO_URI')

# sql_cnx = None
# mongo_client = None
# mongo_db = None
# event_types_col = None
# event_custom_col = None

##helper functions

def connect_sql():
    # global sql_cnx
    try:
        # sql_cnx = mysql.connector.connect
        return mysql.connector.connect(
            user=USERNAME,
            password=PASSWORD,
            host=HOST,
            database=DB
        )
        # return sql_cnx
    except Exception as e:
        print(f"Error connecting to DB: {e}")

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

        print(" Connected to MongoDB")
        return event_types_col, event_custom_col
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise HTTPException(status_code=500, detail="MongoDB connection failed")


## Pydantic model

FieldType = Literal["text","number","boolean"]

class CustomFieldDefinition(BaseModel):
    name: str
    type: FieldType

class CreateEventTypeRequest(BaseModel):
    name: str
    description: Optional[str]= None
    fields:List[CustomFieldDefinition]

class EventTypeResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]= None
    fields: List[CustomFieldDefinition]


##END POINTS##
@router.post("/event-types", response_model=EventTypeResponse)
def create_event_type(request: CreateEventTypeRequest):

    cnx = connect_sql()
    types_col,_ = connect_mongo()

    # cur=cnx.cursor()

    try:
        with cnx.cursor()as cur:
            cur.execute(
            "INSERT INTO eventType (typeName, description) VALUES (%s, %s)",
            (request.name, request.description),
            )
            cnx.commit()
            type_id = cur.lastrowid
    except Exception as e:
        cnx.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cnx.close()

    doc= {
        "typeId": type_id,
        "name": request.name,
        "description": request.description,
        "fields": [f.dict() for f in request.fields]
    }

    try:
        types_col.insert_one(doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return EventTypeResponse(
        id=type_id,
        name=request.name,
        description=request.description,
        fields=request.fields
    )
