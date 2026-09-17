from fastapi import FastAPI
import sqlite3

app = FastAPI(title="Campus Internship & Placement Tracker")


def get_db():
    return sqlite3.connect("placement.db")


def create_tables():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        year INTEGER NOT NULL,
        email TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT,
        website TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS opportunities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        type TEXT NOT NULL,
        eligibility TEXT,
        deadline TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        opportunity_id INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'Applied'
    )
    """)

    db.commit()
    db.close()


create_tables()


@app.get("/")
def home():
    return {
        "message": "Placement Tracker API is running!"
    }
@app.post("/students")
def add_student(
    name: str,
    department: str,
    year: int,
    email: str
):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO students (name, department, year, email) VALUES (?, ?, ?, ?)",
        (name, department, year, email)
    )

    db.commit()
    student_id = cursor.lastrowid
    db.close()

    return {
        "message": "Student added successfully",
        "student_id": student_id
    }
@app.get("/students")
def get_students():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    db.close()

    return {
        "students": students
    }
@app.post("/companies")
def add_company(name: str, location: str = "", website: str = ""):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO companies (name, location, website) VALUES (?, ?, ?)",
        (name, location, website)
    )

    db.commit()
    company_id = cursor.lastrowid
    db.close()

    return {
        "message": "Company added successfully",
        "company_id": company_id
    }
@app.get("/companies")
def get_companies():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM companies")
    companies = cursor.fetchall()

    db.close()

    return {
        "companies": companies
    }
@app.post("/opportunities")
def add_opportunity(
    company_id: int,
    title: str,
    type: str,
    eligibility: str = "",
    deadline: str = ""
):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """INSERT INTO opportunities
           (company_id, title, type, eligibility, deadline)
           VALUES (?, ?, ?, ?, ?)""",
        (company_id, title, type, eligibility, deadline)
    )

    db.commit()
    opportunity_id = cursor.lastrowid
    db.close()

    return {
        "message": "Opportunity added successfully",
        "opportunity_id": opportunity_id
    }
@app.get("/opportunities")
def get_opportunities():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT opportunities.id, companies.name, opportunities.title,
               opportunities.type, opportunities.eligibility,
               opportunities.deadline
        FROM opportunities
        JOIN companies ON opportunities.company_id = companies.id
    """)

    opportunities = cursor.fetchall()
    db.close()

    return {
        "opportunities": opportunities
    }
@app.post("/applications")
def apply_for_opportunity(student_id: int, opportunity_id: int):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO applications (student_id, opportunity_id) VALUES (?, ?)",
        (student_id, opportunity_id)
    )

    db.commit()
    application_id = cursor.lastrowid
    db.close()

    return {
        "message": "Application submitted",
        "application_id": application_id
    }
@app.get("/applications")
def get_applications():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT applications.id, students.name, opportunities.title,
               applications.status
        FROM applications
        JOIN students ON applications.student_id = students.id
        JOIN opportunities ON applications.opportunity_id = opportunities.id
    """)

    applications = cursor.fetchall()
    db.close()

    return {
        "applications": applications
    }
@app.put("/applications/{application_id}/status")
def update_status(application_id: int, status: str):
    allowed = {"Applied", "Shortlisted", "Selected", "Rejected"}

    if status not in allowed:
        return {"error": "Invalid status"}

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE applications SET status = ? WHERE id = ?",
        (status, application_id)
    )

    db.commit()
    db.close()

    return {
        "message": "Status updated successfully"
    }
@app.get("/opportunities/search")
def search_opportunities(keyword: str):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT opportunities.id, companies.name, opportunities.title,
               opportunities.type, opportunities.eligibility,
               opportunities.deadline
        FROM opportunities
        JOIN companies ON opportunities.company_id = companies.id
        WHERE opportunities.title LIKE ?
           OR opportunities.type LIKE ?
           OR companies.name LIKE ?
    """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))

    results = cursor.fetchall()
    db.close()

    return {"results": results}
