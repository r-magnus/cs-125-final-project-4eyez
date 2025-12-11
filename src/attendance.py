# @author Ryan Magnuson <rmagnuson@westmont.edu>

import redis
import mysql.connector
import os
from src.mysql_connect import connect_sql

def redis_connect():
    try:
        return redis.Redis(
                host=os.getenv("REDIS_HOST"),
                port=int(os.getenv("REDIS_PORT")),
                username='default',
                password=os.getenv("REDIS_PASS"),
                # ssl=True,
                decode_responses=True
            )
    except Exception as e:
        print(f"An exception occurred connecting to Redis: {e}")

def checkin(r, event_id, student_id):
    r.sadd(f"event:{event_id}:checkedIn", student_id)

def checkout(r, event_id, student_id):
    r.srem(f"event:{event_id}:checkedIn", student_id)

def get_attendance(r, event_id, student_id=None):
    """
    Gets EITHER a list of attending students, given simply an event_id,
    OR whether or not a student is attending a particular event, if student_id
    is provided.
    """
    if student_id:
        return r.sismember(f"event:{event_id}:checkedIn", student_id)
    else:
        return r.smembers(f"event:{event_id}:checkedIn")

def get_attendance_count(r, event_id):
    return r.scard(f"event:{event_id}:checkedIn")

def end_event(r, event_id):
    def record_attendance(cnx, event_id, members):
        crs = cnx.cursor()
        # formatted = ', '.join([str(mem) for mem in members])
        res = []
        for mem in members:
            crs.execute("""
                        SELECT signeeId, meetingId
                        FROM MeetingSignUpItem
                        WHERE meetingId = %(event_id)s AND signeeId IN (%(mems)s)
                        """, {'event_id': event_id,
                              'mems': mem})
            res.append(crs.fetchall()[0])

        presents = [{'id': personId, 'stat': 'Present'} for (personId, meetingId) in res]

        crs.execute("""
                    SELECT signeeId, meetingId
                    FROM MeetingSignUpItem
                    WHERE meetingId = %(event_id)s
                    """, {'event_id': event_id})
        absents = [{'id': personId, 'stat': 'Absent'} for (personId, meetingId) in crs.fetchall() if {'id': personId, 'stat': 'Present'} not in presents]

        attendance = presents + absents

        # formatted = ', '.join([str((int(mem['id']), mem['stat'])) for mem in attendance])
        for person in attendance:
            crs.execute(f"""
                            INSERT INTO attendanceItem (signupId, STATUS)
                            VALUES
                            (%s, %s)
                            """, (person['id'], person['stat']))

        cnx.commit()
        crs.close()
        cnx.close()

    members = r.smembers(f"event:{event_id}:checkedIn")

    # send to mysql
    cnx = connect_sql()
    record_attendance(cnx, event_id, members)

    r.delete(f"event:{event_id}:checkedIn")