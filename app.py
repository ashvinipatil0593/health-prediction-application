import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import re
import os
from google import genai

st.set_page_config(layout="wide")

st.title("Health Prediction Application")

st.info("""
Normal Health Ranges

Glucose: 70 - 140 mg/dL

Haemoglobin: 12 - 16 g/dL

Cholesterol: Below 200 mg/dL
""")


def generate_remarks(glucose, haemoglobin, cholesterol):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return "Gemini API key not found."

    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""
        You are a health prediction assistant.

        Glucose: {glucose}
        Haemoglobin: {haemoglobin}
        Cholesterol: {cholesterol}

        Rules:
        - Mention only possible health risk.
        - Keep response under 15 words.
        - Return only one sentence.
        - No medical disclaimer.
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception:
        return "AI prediction failed."


conn = sqlite3.connect("patients.db", check_same_thread=False)
cursor = conn.cursor()

st.subheader("Add New Patient")

name = st.text_input("Enter Patient Name")

st.write("Select Date of Birth")

col1, col2, col3 = st.columns(3)

with col1:
    year = st.selectbox(
        "Year",
        range(date.today().year, 1950, -1)
    )

with col2:
    month = st.selectbox(
        "Month",
        [f"{i:02d}" for i in range(1, 13)]
    )

with col3:
    day = st.selectbox(
        "Day",
        [f"{i:02d}" for i in range(1, 32)]
    )

dob = f"{day}-{month}-{year}"

email = st.text_input("Enter Email Address")

glucose = st.number_input(
    "Enter Glucose Level (Normal Range: 70 - 140 mg/dL)",
    min_value=0.0
)

haemoglobin = st.number_input(
    "Enter Haemoglobin Level (Normal Range: 12 - 16 g/dL)",
    min_value=0.0
)

cholesterol = st.number_input(
    "Enter Cholesterol Level (Normal Range: Below 200 mg/dL)",
    min_value=0.0
)


if st.button("Submit"):

    if name == "":
        st.error("Patient name is required")

    elif email == "":
        st.error("Email address is required")

    elif not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
        st.error("Please enter a valid email address")

    elif glucose <= 0 or haemoglobin <= 0 or cholesterol <= 0:
        st.error("Blood test values must be greater than 0")

    else:
        remarks = generate_remarks(glucose, haemoglobin, cholesterol)

        cursor.execute("""
        INSERT INTO patients
        (name,dob,email,glucose,haemoglobin,cholesterol,remarks)
        VALUES (?,?,?,?,?,?,?)
        """,
        (
            name,
            dob,
            email,
            glucose,
            haemoglobin,
            cholesterol,
            remarks
        ))

        conn.commit()

        st.success("Patient Saved Successfully")


st.subheader("View Patient Records")

if st.button("View Patients"):

    conn = sqlite3.connect("patients.db")

    df = pd.read_sql("SELECT * FROM patients", conn)

    st.dataframe(df, width="stretch")

    conn.close()


st.subheader("Delete Patient")

patient_id = st.number_input(
    "Enter Patient ID to Delete",
    min_value=1,
    step=1
)

if st.button("Delete Patient"):

    conn = sqlite3.connect("patients.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM patients WHERE id=?",
        (patient_id,)
    )

    conn.commit()
    conn.close()

    st.success("Patient Deleted Successfully")


st.subheader("Update Patient")

update_id = st.number_input(
    "Enter Patient ID to Update",
    min_value=1,
    step=1,
    key="update_id"
)

updated_name = st.text_input(
    "Enter Updated Name",
    key="updated_name"
)

updated_email = st.text_input(
    "Enter Updated Email",
    key="updated_email"
)

updated_glucose = st.number_input(
    "Enter Updated Glucose Level",
    min_value=0.0,
    key="updated_glucose"
)

updated_haemoglobin = st.number_input(
    "Enter Updated Haemoglobin Level",
    min_value=0.0,
    key="updated_haemoglobin"
)

updated_cholesterol = st.number_input(
    "Enter Updated Cholesterol Level",
    min_value=0.0,
    key="updated_cholesterol"
)

if st.button("Update Patient"):

    if updated_name == "":
        st.error("Updated name is required")

    elif updated_email == "":
        st.error("Updated email is required")

    elif not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", updated_email):
        st.error("Please enter a valid email address")

    elif updated_glucose <= 0 or updated_haemoglobin <= 0 or updated_cholesterol <= 0:
        st.error("Blood test values must be greater than 0")

    else:
        updated_remarks = generate_remarks(
            updated_glucose,
            updated_haemoglobin,
            updated_cholesterol
        )

        conn = sqlite3.connect("patients.db")
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE patients
        SET name=?, email=?, glucose=?, haemoglobin=?, cholesterol=?, remarks=?
        WHERE id=?
        """,
        (
            updated_name,
            updated_email,
            updated_glucose,
            updated_haemoglobin,
            updated_cholesterol,
            updated_remarks,
            update_id
        ))

        conn.commit()
        conn.close()

        st.success("Patient Updated Successfully")