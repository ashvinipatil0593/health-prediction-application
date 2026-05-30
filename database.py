import sqlite3

conn = sqlite3.connect("patients.db", check_same_thread=False)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS patients(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    dob TEXT,
    email TEXT,
    glucose REAL,
    haemoglobin REAL,
    cholesterol REAL,
    remarks TEXT
)
""")

conn.commit()