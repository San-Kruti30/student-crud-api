import sqlite3
from datetime import date
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, Response, status

from .database import get_conn, init_db
from .schemas import StudentCreate, StudentOut, StudentUpdate

app = FastAPI(title="Students CRUD API")

@app.on_event("startup")
def startup():
    init_db()

def to_db(data: dict) -> dict:
    return {k: (v.isoformat() if isinstance(v, date) else v) for k, v in data.items()}



# ---------- CREATE ----------
@app.post("/students", response_model=StudentOut, status_code=201)
def create_student(student: StudentCreate):
    data = to_db(student.model_dump())
    cols = ", ".join(data)
    marks = ", ".join("?" for _ in data)
    try:
        with get_conn() as conn:
            cur = conn.execute(
                f"INSERT INTO students ({cols}) VALUES ({marks})", list(data.values())
            )
            row = conn.execute("SELECT * FROM students WHERE id = ?", (cur.lastrowid,)).fetchone()
    except sqlite3.IntegrityError:
        raise HTTPException(409, "A student with this email already exists")
    return dict(row)











# ---------- READ: list + filter ----------
@app.get("/students", response_model=List[StudentOut])
def list_students(
    name: Optional[str] = None,
    course: Optional[str] = None,
    born_after: Optional[date] = None,
    born_before: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    sql, params = "SELECT * FROM students WHERE 1=1", []
    if name:
        sql += " AND name LIKE ?"; params.append(f"%{name}%")
    if course:
        sql += " AND course = ?"; params.append(course)
    if born_after:
        sql += " AND date_of_birth > ?"; params.append(born_after.isoformat())
    if born_before:
        sql += " AND date_of_birth < ?"; params.append(born_before.isoformat())
    sql += " ORDER BY id LIMIT ? OFFSET ?"; params += [limit, skip]
    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(r) for r in rows]

# ---------- READ: one student ----------
@app.get("/students/{student_id}", response_model=StudentOut)
def get_student(student_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "Student not found")
    return dict(row)








# ---------- UPDATE ----------
@app.patch("/students/{student_id}", response_model=StudentOut)
@app.put("/students/{student_id}", response_model=StudentOut)
def update_student(student_id: int, changes: StudentUpdate):
    data = to_db(changes.model_dump(exclude_unset=True))
    if not data:
        raise HTTPException(400, "No fields provided to update")
    set_clause = ", ".join(f"{k} = ?" for k in data)
    try:
        with get_conn() as conn:
            cur = conn.execute(
                f"UPDATE students SET {set_clause} WHERE id = ?", [*data.values(), student_id]
            )
            if cur.rowcount == 0:
                raise HTTPException(404, "Student not found")
            row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    except sqlite3.IntegrityError:
        raise HTTPException(409, "A student with this email already exists")
    return dict(row)











# ---------- DELETE ----------
@app.delete("/students/{student_id}", status_code=204)
def delete_student(student_id: int):
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    if cur.rowcount == 0:
        raise HTTPException(404, "Student not found")
    return Response(status_code=204)
