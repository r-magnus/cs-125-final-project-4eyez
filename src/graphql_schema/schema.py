import strawberry
from typing import List, Optional
from src.mysql_connect import connect_sql
from src.attendance import redis_connect, get_attendance as get_attendance_logic
from src.attendance import checkin as checkin_logic, checkout as checkout_logic
from pydantic import BaseModel
from datetime import date
from src.event import connect_mongo # Moved to top

# Pydantic models for business logic
class CustomFieldDefinition(BaseModel):
    name: str
    type: str

@strawberry.type
class CustomFieldDefinitionGQL: # New Strawberry type
    name: str
    type: str

class CustomFieldRequest(BaseModel):
    name: str
    description: Optional[str] = None
    fields: List[CustomFieldDefinition]

class CustomValue(BaseModel):
    fieldName: str
    value: str

class CreateEventRequest(BaseModel):
    meetId: int
    title: Optional[str] = None # Make title optional
    createdByID: int
    typeId: int
    location: str
    startDate: date
    endDate: date
    customValues: List[CustomValue]


@strawberry.type
class Person:
    personId: int
    firstName: str
    lastName: str

@strawberry.type
class Student(Person):
    grade: str

@strawberry.type
class Volunteer(Person):
    pass

@strawberry.type
class Admin(Person):
    pass

@strawberry.type
class Guardian(Person):
    pass

@strawberry.type
class EventType:
    typeId: int
    typeName: str
    description: str
    fields: List[CustomFieldDefinitionGQL]

@strawberry.type
class Meeting:
    meetId: int
    title: str

@strawberry.type
class Event(Meeting):
    createdByID: int
    typeId: int
    location: str
    startDate: str
    endDate: str
    type: str

@strawberry.type
class MeetingSignUpItem:
    id: int
    signeeId: int
    signedUpById: int
    meetingId: int

@strawberry.type
class AttendanceItem:
    id: int
    signupId: int
    STATUS: str

@strawberry.type
class PastAttendanceItem:
    signeeId: int
    status: str

def get_students() -> List[Student]:
    cnx = connect_sql()
    cursor = cnx.cursor(dictionary=True)
    query = "SELECT p.personId, p.firstName, p.lastName, s.grade FROM Person p JOIN Student s ON p.personId = s.personId"
    cursor.execute(query)
    students = [Student(**row) for row in cursor.fetchall()]
    cursor.close()
    cnx.close()
    return students

def get_volunteers() -> List[Volunteer]:
    cnx = connect_sql()
    cursor = cnx.cursor(dictionary=True)
    query = "SELECT p.personId, p.firstName, p.lastName FROM Person p JOIN Volunteer v ON p.personId = v.personId"
    cursor.execute(query)
    volunteers = [Volunteer(**row) for row in cursor.fetchall()]
    cursor.close()
    cnx.close()
    return volunteers

def get_admins() -> List[Admin]:
    cnx = connect_sql()
    cursor = cnx.cursor(dictionary=True)
    query = "SELECT p.personId, p.firstName, p.lastName FROM Person p JOIN Admin a ON p.personId = a.personId"
    cursor.execute(query)
    admins = [Admin(**row) for row in cursor.fetchall()]
    cursor.close()
    cnx.close()
    return admins

def get_guardians() -> List[Guardian]:
    cnx = connect_sql()
    cursor = cnx.cursor(dictionary=True)
    query = "SELECT p.personId, p.firstName, p.lastName FROM Person p JOIN Guardian g ON p.personId = g.personId"
    cursor.execute(query)
    guardians = [Guardian(**row) for row in cursor.fetchall()]
    cursor.close()
    cnx.close()
    return guardians

def get_event_types() -> List[EventType]:
    cnx = connect_sql()
    cursor = cnx.cursor(dictionary=True)
    query = "SELECT typeId, typeName, description FROM eventType"
    cursor.execute(query)
    event_types_data = cursor.fetchall()
    cursor.close()
    cnx.close()

    event_type_collection, _ = connect_mongo() # Connect to MongoDB

    event_types = []
    for row in event_types_data:
        mongo_doc = event_type_collection.find_one({"typeId": row['typeId']})
        fields_data = mongo_doc.get("fields", []) if mongo_doc else []
        event_types.append(EventType(
            typeId=row['typeId'],
            typeName=row['typeName'],
            description=row['description'],
            fields=[CustomFieldDefinitionGQL(**f) for f in fields_data]
        ))
    return event_types

def get_events() -> List[Event]:
    cnx = connect_sql()
    cursor = cnx.cursor(dictionary=True)
    query = """
        SELECT m.meetId, m.title, e.createdByID, e.typeId, e.location, e.startDate, e.endDate, et.typeName AS type
        FROM Meeting m
        JOIN Event e ON m.meetId = e.meetId
        JOIN eventType et ON e.typeId = et.typeId
    """
    cursor.execute(query)
    events = [Event(
        meetId=row['meetId'],
        title=row['title'],
        createdByID=row['createdByID'],
        typeId=row['typeId'],
        location=row['location'],
        startDate=str(row['startDate']),
        endDate=str(row['endDate']),
        type=row['type']
    ) for row in cursor.fetchall()]
    cursor.close()
    cnx.close()
    return events

def get_signups(meeting_id: int) -> List[MeetingSignUpItem]:
    cnx = connect_sql()
    cursor = cnx.cursor(dictionary=True)
    query = "SELECT id, signeeId, signedUpById, meetingId FROM MeetingSignUpItem WHERE meetingId = %s"
    cursor.execute(query, (meeting_id,))
    signups = [MeetingSignUpItem(**row) for row in cursor.fetchall()]
    cursor.close()
    cnx.close()
    return signups

@strawberry.input
class CustomFieldDefinitionInput:
    name: str
    type: str

@strawberry.input
class CreateEventTypeInput:
    name: str
    description: Optional[str] = None
    fields: List[CustomFieldDefinitionInput]

@strawberry.input
class CustomValueInput:
    fieldName: str
    value: str

@strawberry.input
class CreateEventInput:
    meetId: int
    title: Optional[str] = None # Make title optional
    createdByID: int
    typeId: int
    location: str
    startDate: str
    endDate: str
    customValues: List[CustomValueInput]

@strawberry.type
class Mutation:
    @strawberry.mutation
    def deleteEvent(self, meet_id: int) -> bool:
        try:
            cnx = connect_sql()
            cursor = cnx.cursor()
            query = "DELETE FROM Meeting WHERE meetId = %s"
            cursor.execute(query, (meet_id,))
            cnx.commit()
            cursor.close()
            cnx.close()
            return True
        except Exception as e:
            raise Exception(f"Error deleting event: {e}")

    @strawberry.mutation
    def create_event_type(self, event_type_data: CreateEventTypeInput) -> EventType:
        request = CustomFieldRequest(
            name=event_type_data.name,
            description=event_type_data.description,
            fields=[{"name": f.name, "type": f.type} for f in event_type_data.fields],
        )
        try:

            cnx = connect_sql()
            event_type_collection, _ = connect_mongo()

            with cnx.cursor() as cur:
                cur.execute(
                    "INSERT INTO eventType (typeName, description) VALUES (%s, %s)",
                    (request.name, request.description),
                )
                cnx.commit()
                type_id = cur.lastrowid
            
            doc = {
                "typeId": type_id,
                "name": request.name,
                "description": request.description,
                "fields": request.fields
            }
            event_type_collection.insert_one(doc)
            
            return EventType(
                typeId=type_id,
                typeName=request.name,
                description=request.description or "",
                fields=[CustomFieldDefinitionGQL(**f) for f in request.fields]
            )
        except Exception as e:
            raise Exception(f"Error creating event type: {e}")

    @strawberry.mutation
    def create_event(self, event_data: CreateEventInput) -> Event:
        # Determine the effective title early
        title_from_input = str(event_data.title) if event_data.title is not None else None
        effective_title = title_from_input if title_from_input else "Untitled Event"

        custom_values = [CustomValue(fieldName=cv.fieldName, value=cv.value) for cv in event_data.customValues]
        request = CreateEventRequest(
            meetId=event_data.meetId,
            title=effective_title,
            createdByID=event_data.createdByID,
            typeId=event_data.typeId,
            location=event_data.location,
            startDate=date.fromisoformat(event_data.startDate),
            endDate=date.fromisoformat(event_data.endDate),
            customValues=custom_values,
        )

        try:

            event_type_collection, custom_event_collection = connect_mongo()

            schema_doc = event_type_collection.find_one({"typeId": request.typeId})
            if not schema_doc:
                # If not found in MongoDB, check MySQL and create in MongoDB if exists in MySQL
                cnx_mysql = connect_sql()
                cursor_mysql = cnx_mysql.cursor(dictionary=True)
                cursor_mysql.execute(
                    "SELECT typeName, description FROM eventType WHERE typeId = %s",
                    (request.typeId,)
                )
                mysql_event_type = cursor_mysql.fetchone()
                cursor_mysql.close()
                cnx_mysql.close()

                if mysql_event_type:
                    # Create the MongoDB document for the missing eventType
                    doc = {
                        "typeId": request.typeId,
                        "name": mysql_event_type['typeName'],
                        "description": mysql_event_type['description'],
                        "fields": [] # No custom fields by default if created this way
                    }
                    event_type_collection.insert_one(doc)
                    schema_doc = doc # Use the newly created doc for validation below
                else:
                    raise Exception("Unknown event typeId") # Not in MySQL either, so it's truly unknown

            allowed_fields = {f["name"] for f in schema_doc.get("fields", [])}
            for cv in request.customValues:
                if cv.fieldName not in allowed_fields:
                    raise Exception(f"Unknown custom field for this event type: {cv.fieldName}")

            cnx = connect_sql()
            with cnx.cursor() as cur:
                # Check if Meeting exists, if not, create it
                cur.execute("SELECT meetId FROM Meeting WHERE meetId = %s", (request.meetId,))
                existing_meeting = cur.fetchone()
                if not existing_meeting:
                    cur.execute(
                        "INSERT INTO Meeting (meetId, title) VALUES (%s, %s)",
                        (request.meetId, effective_title),
                    )

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

            values_dict = {cv.fieldName: cv.value for cv in request.customValues}
            mongo_doc = {
                "eventId": request.meetId,
                "meetId": request.meetId,
                "createdByID": request.createdByID,
                "typeId": request.typeId,
                "values": values_dict
            }
            custom_event_collection.insert_one(mongo_doc)
            
            # The title for the returned Event object is still fetched from the DB
            # with cnx.cursor(dictionary=True) as cur:
            #    cur.execute("SELECT title FROM Meeting WHERE meetId = %s", (request.meetId,))
            #    meeting = cur.fetchone()
            #    title = meeting['title'] if meeting else "" # This will now always exist or be the newly created one

            with cnx.cursor(dictionary=True) as cur:
                cur.execute("SELECT typeName FROM eventType WHERE typeId = %s", (request.typeId,))
                event_type_name_data = cur.fetchone()
                event_type_name = event_type_name_data['typeName'] if event_type_name_data else "Unknown Type"
            
            cnx.close()

            return Event(
                meetId=request.meetId,
                title=effective_title, # Use the effective_title
                createdByID=request.createdByID,
                typeId=request.typeId,
                location=request.location,
                startDate=str(request.startDate),
                endDate=str(request.endDate),
                type=event_type_name
            )
        except Exception as e:
            raise Exception(f"Error creating event: {e}")

    @strawberry.mutation
    def checkin(self, event_id: int, student_id: int) -> bool:
        try:
            r = redis_connect()
            checkin_logic(r, event_id, student_id)
            return True
        except Exception as e:
            raise Exception(f"Error checking in: {e}")

    @strawberry.mutation
    def checkout(self, event_id: int, student_id: int) -> bool:
        try:
            r = redis_connect()
            checkout_logic(r, event_id, student_id)
            return True
        except Exception as e:
            raise Exception(f"Error checking out: {e}")

    @strawberry.mutation
    def signUpForEvent(self, meeting_id: int, signee_id: int, signed_up_by_id: int) -> MeetingSignUpItem:
        try:
            cnx = connect_sql()
            cursor = cnx.cursor(dictionary=True)
            query = "INSERT INTO MeetingSignUpItem (meetingId, signeeId, signedUpById) VALUES (%s, %s, %s)"
            cursor.execute(query, (meeting_id, signee_id, signed_up_by_id))
            new_id = cursor.lastrowid
            cnx.commit()
            cursor.close()
            cnx.close()
            return MeetingSignUpItem(id=new_id, meetingId=meeting_id, signeeId=signee_id, signedUpById=signed_up_by_id)
        except Exception as e:
            raise Exception(f"Error signing up for event: {e}")

    @strawberry.mutation
    def removeSignUp(self, signup_id: int) -> bool:
        try:
            cnx = connect_sql()
            cursor = cnx.cursor()
            query = "DELETE FROM MeetingSignUpItem WHERE id = %s"
            cursor.execute(query, (signup_id,))
            cnx.commit()
            cursor.close()
            cnx.close()
            return True
        except Exception as e:
            raise Exception(f"Error removing sign up: {e}")

@strawberry.type
class Query:
    students: List[Student] = strawberry.field(resolver=get_students)
    volunteers: List[Volunteer] = strawberry.field(resolver=get_volunteers)
    admins: List[Admin] = strawberry.field(resolver=get_admins)
    guardians: List[Guardian] = strawberry.field(resolver=get_guardians)
    event_types: List[EventType] = strawberry.field(resolver=get_event_types)
    events: List[Event] = strawberry.field(resolver=get_events)
    signups: List[MeetingSignUpItem] = strawberry.field(resolver=get_signups)

    @strawberry.field
    def event(self, info, meetId: int) -> Optional[Event]:
        cnx = connect_sql()
        cursor = cnx.cursor(dictionary=True)
        query = """
            SELECT m.meetId, m.title, e.createdByID, e.typeId, e.location, e.startDate, e.endDate, et.typeName AS type
            FROM Meeting m
            JOIN Event e ON m.meetId = e.meetId
            JOIN eventType et ON e.typeId = et.typeId
            WHERE m.meetId = %s
        """
        cursor.execute(query, (meetId,))
        event_data = cursor.fetchone()
        cursor.close()
        cnx.close()

        if event_data:
            return Event(
                meetId=event_data["meetId"],
                title=event_data["title"],
                createdByID=event_data["createdByID"],
                typeId=event_data["typeId"],
                location=event_data["location"],
                startDate=str(event_data["startDate"]),
                endDate=str(event_data["endDate"]),
                type=event_data["type"]
            )
        return None

    @strawberry.field
    def attendance(self, event_id: int) -> List[int]:
        try:
            r = redis_connect()
            return [int(student_id) for student_id in get_attendance_logic(r, event_id)]
        except Exception as e:
            raise Exception(f"Error getting attendance: {e}")

    @strawberry.field
    def pastAttendance(self, event_id: int) -> List[PastAttendanceItem]:
        try:
            cnx = connect_sql()
            cursor = cnx.cursor(dictionary=True)
            query = """
                SELECT msi.signeeId, ai.STATUS
                FROM attendanceItem ai
                JOIN MeetingSignUpItem msi ON ai.signupId = msi.id
                WHERE msi.meetingId = %s
            """
            cursor.execute(query, (event_id,))
            attendance_items = [PastAttendanceItem(signeeId=row['signeeId'], status=row['STATUS']) for row in cursor.fetchall()]
            cursor.close()
            cnx.close()
            return attendance_items
        except Exception as e:
            raise Exception(f"Error getting past attendance: {e}")

custom_schema = strawberry.Schema(query=Query, mutation=Mutation)