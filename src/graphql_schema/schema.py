
import strawberry
from typing import List
from src.mysql_connect import connect_sql

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

def get_students() -> List[Student]:
    cnx = connect_sql()
    cursor = cnx.cursor(dictionary=True)
    query = """
        SELECT p.personId, p.firstName, p.lastName, s.grade
        FROM Person p
        JOIN Student s ON p.personId = s.personId
    """
    cursor.execute(query)
    students = [Student(**row) for row in cursor.fetchall()]
    cursor.close()
    cnx.close()
    return students

def get_volunteers() -> List[Volunteer]:
    cnx = connect_sql()
    cursor = cnx.cursor(dictionary=True)
    query = """
        SELECT p.personId, p.firstName, p.lastName
        FROM Person p
        JOIN Volunteer v ON p.personId = v.personId
    """
    cursor.execute(query)
    volunteers = [Volunteer(**row) for row in cursor.fetchall()]
    cursor.close()
    cnx.close()
    return volunteers

def get_admins() -> List[Admin]:
    cnx = connect_sql()
    cursor = cnx.cursor(dictionary=True)
    query = """
        SELECT p.personId, p.firstName, p.lastName
        FROM Person p
        JOIN Admin a ON p.personId = a.personId
    """
    cursor.execute(query)
    admins = [Admin(**row) for row in cursor.fetchall()]
    cursor.close()
    cnx.close()
    return admins

@strawberry.type
class Query:
    students: List[Student] = strawberry.field(resolver=get_students)
    volunteers: List[Volunteer] = strawberry.field(resolver=get_volunteers)
    admins: List[Admin] = strawberry.field(resolver=get_admins)

custom_schema = strawberry.Schema(query=Query)
