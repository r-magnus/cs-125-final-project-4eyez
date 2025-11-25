# cs-125-final-project-4eyez
The final project for CS125, combining a whole lot of DBs for a youth group event management application.

---

## TEAM 4 EYEZ

---

### How-To

"How do I run this thing?"

* Create a virtual environment with `python -m venv .venv`
  * Activate with `source .venv/bin/activate`
  * Install dependencies with `pip install -r requirements.txt`
* Create a `.env` file. Populate it with:
  * `USERNAME = <Your MYSQL User>`
  * `PASSWORD = <Your MYSQL Password>`
  * `HOST = 127.0.0.1`
  * `DB = finalProj_workorder`
* Run the `schema.sql` file, then the `sampleData.sql` file to populate the tables.
* Finally, run the server with `python src/main.py`, from project root.

Upon completing these instructions, the query-able server will be running on `localhost`,
available for queries.

---

### Who is using this?
- Admin
  - Youth pastors
  - Volunteers (kinda)
    
- “Audience”
  - Parent/guardians
  - Students

### What do they want to do?
- Admin: want to create events, plan volunteers ,take attendance
  - Volunteers: Sign up for volunteer slots
    - Record/upload notes
    - Attendance per-event
    - Assist leader (pastor) in various admin tasks
      
- Audience:
  - Students: Sign up themselves
  - Parents/Guardians: Sign up their kids against their will

### What should/shouldn’t they be able to do?
- Admin
  - Basically does everything (create an event, volunteer for an event, take notes, etc.)
  - Can’t sign up other people lol
    
- Audience
  - Signs up for events
    - Parent/guardians can sign up for their kid(s)
  - Can’t perform admin tasks
    - Take attendance, upload notes, create events

---

Github: https://github.com/r-magnus/cs-125-final-project-4eyez
