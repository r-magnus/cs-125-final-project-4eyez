from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Literal, Optional, Any,Dict
from datetime import date
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



##helper functions

def connect_sql():
    try:
        return mysql.connector.connect(
            user=USERNAME,
            password=PASSWORD,
            host=HOST,
            database=DB
        )
    except Exception as e:
        print(f"Error connecting to DB: {e}")

def connect_mongo():
    global mongo_client,mongo_db,event_type,custom_event
    try:
        mongo_client = MongoClient(MONGO_URI)
        mongo_db = mongo_client["finalProj_workorder"]

        # Collections
        event_type = mongo_db["eventTypes"]
        custom_event = mongo_db["eventCustomData"]

        # Indexes
        event_type.create_index("typeId", unique=True)
        custom_event.create_index("meetId", unique=True)
        custom_event.create_index("typeId")

        print(" Connected to MongoDB")
        return event_type, custom_event
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise HTTPException(status_code=500, detail="MongoDB connection failed")


## Pydantic model

FieldType = Literal["text","number","boolean"]

class CustomFieldDefinition(BaseModel):
    name: str
    type: FieldType

class CustomFieldRequest(BaseModel):
    name: str
    description: Optional[str]= None
    fields:List[CustomFieldDefinition]

class CustomFieldResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]= None
    fields: List[CustomFieldDefinition]

class CustomValue(BaseModel):
    fieldName:str
    value:Any

class CreateEventRequest(BaseModel):
    meetId: int  # should exist in Meeting
    createdByID: int  # Person.personId
    typeId: int  # eventType.typeId
    location: str
    startDate: date
    endDate: date
    customValues: List[CustomValue]

class EventCustomDataResponse(BaseModel):
    meetId: int
    typeId: int
    values:Dict[str, Any]


class SmallGroupCreate(BaseModel):
    meetId: int
    title:str
    nextMeetingDate: date


class SmallGroupResponse(BaseModel):
    meetId: int
    nextMeetingDate: date


##END POINTS##
@router.post("/event-types")
def create_event_type(request: CustomFieldRequest):

    cnx = connect_sql()
    event_type,_ = connect_mongo()



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
        event_type.insert_one(doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return CustomFieldResponse(
        id=type_id,
        name=request.name,
        description=request.description,
        fields=request.fields
    )
@router.post("/events")
def create_event(request: CreateEventRequest):
    cnx = connect_sql()
    event_type,custom_event = connect_mongo()

    schema_doc = event_type.find_one({"typeId": request.typeId})
    if not schema_doc:
        raise HTTPException(status_code=400, detail="Unknown event typeId")

    allowed_fields = {f["name"] for f in schema_doc.get("fields", [])}
    for cv in request.customValues:
        if cv.fieldName not in allowed_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown custom field for this event type: {cv.fieldName}",
            )



    try:
        with cnx.cursor() as cur:
            cur.execute(
        """
                INSERT INTO Event (meetId, createdByID, typeId, location, startDate, endDate)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
        (
                    request.meetId,
                    request.createdByID,
                    request.typeId,
                    request.location,
                    request.startDate,
                    request.endDate,
                ),
            )
        cnx.commit()
    except Exception as e:
        cnx.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cnx.close()

    values_dict= {cv.fieldName: cv.value for cv in request.customValues}

    mongo_doc={
        "meetId": request.meetId,
        "createdByID": request.createdByID,
        "typeId": request.typeId,
        "values": values_dict
    }

    try:
        custom_event.insert_one(mongo_doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Event created with custom data successfully"}

@router.get("/events/{meet_id}/custom-data", response_model=EventCustomDataResponse)
def get_event_custom_data(meet_id: int):
    """
    Fetch custom field values for a given event (by meetId).
    """
    _, custom_event = connect_mongo()
    doc = custom_event.find_one({"meetId": meet_id})
    if not doc:
        raise HTTPException(status_code=404, detail="No custom data for this event")

    return EventCustomDataResponse(
        meetId=doc["meetId"],
        typeId=doc["typeId"],
        values=doc.get("values", {}),
    )

@router.post("/smallgroups", response_model=SmallGroupResponse)
def create_update_smallgroups(body: SmallGroupCreate):
    cnx = connect_sql()
    try:
        with cnx.cursor() as cur:
            # 1) Ensure Meeting exists
            cur.execute("SELECT 1 FROM Meeting WHERE meetId = %s", (body.meetId,))
            exists = cur.fetchone()

            if not exists:
                cur.execute(
                    "INSERT INTO Meeting (meetId, title) VALUES (%s, %s)",
                    (body.meetId, body.title),
                )

            # 2) Insert / update smallGroup
            cur.execute(
                """
                INSERT INTO smallGroup (meetId, nextMeetingDate)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE nextMeetingDate = VALUES(nextMeetingDate)
                """,
                (body.meetId, body.nextMeetingDate),
            )

        cnx.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cnx.close()

    return SmallGroupResponse(
        meetId=body.meetId,
        nextMeetingDate=body.nextMeetingDate,
    )

@router.get("/smallgroups/{meet_id}", response_model=SmallGroupResponse)
def get_smallgroups(meet_id: int):
    cnx = connect_sql()
    try:
        with cnx.cursor() as cur:
            cur.execute("SELECT meetId, nextMeetingDate FROM smallGroup WHERE meetId = %s",
                (meet_id,),
            )
            row = cur.fetchone()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cnx.close()
    if row is None:
        raise HTTPException(status_code=404, detail="SmallGroup not found")

    return SmallGroupResponse(meetId=row[0], nextMeetingDate=row[1])



