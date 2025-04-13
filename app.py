import streamlit as st
from datetime import datetime, time, date
import sqlite3
import json

# --- Setup SQLite DB ---
conn = sqlite3.connect("zenput_data.db", check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS forms (
    form_name TEXT PRIMARY KEY,
    questions TEXT,
    created_at TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS projects (
    project_name TEXT,
    assigned_to TEXT,
    form_used TEXT,
    days TEXT,
    time TEXT,
    start TEXT,
    end TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS submissions (
    project TEXT,
    form TEXT,
    responses TEXT,
    submitted_by TEXT,
    timestamp TEXT
)''')

conn.commit()

# --- Simulated user roles (in real app, use auth) ---
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "branch01": {"password": "b01pass", "role": "branch"},
    "branch02": {"password": "b02pass", "role": "branch"},
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

# --- Login Page ---
def login_page():
    st.title("🔐 Zenput Clone Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = USERS.get(username)
        if user and user["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = user["role"]
            st.success(f"Welcome {username}!")
        else:
            st.error("Invalid credentials")

# --- Admin Pages ---
def admin_home():
    st.title("🏠 Admin Home")
    st.write("Welcome, admin. Choose an action below:")
    if st.button("➕ Create New Form"):
        st.session_state.admin_page = "Form Builder"
    if st.button("📁 Assign New Project"):
        st.session_state.admin_page = "Assign Projects"

def admin_form_builder():
    st.title("🛠️ Form Builder")
    form_name = st.text_input("Form Name")
    num_fields = st.number_input("Number of Questions", 1, 20, 5)

    st.subheader("🧩 Define Questions")
    questions = []
    for i in range(int(num_fields)):
        q = {}
        q["label"] = st.text_input(f"Question {i+1} Text", key=f"label_{i}")
        q["type"] = st.selectbox("Type", ["Text", "Yes/No", "Multiple Choice", "Number", "Checkbox", "Date/Time", "Rating", "Email", "Stopwatch", "Photo", "Signature", "Barcode", "Video", "Document", "Formula", "Location"], key=f"type_{i}")
        if q["type"] == "Multiple Choice":
            q["options"] = st.text_input(f"Options (comma-separated)", key=f"options_{i}").split(",")
        if q["type"] == "Rating":
            q["max_rating"] = st.slider(f"Max Rating", 1, 10, 5, key=f"rating_{i}")
        if q["type"] == "Formula":
            q["formula"] = st.text_input(f"Formula Expression", key=f"formula_{i}")
        questions.append(q)

    if st.button("Save Form"):
        c.execute("INSERT OR REPLACE INTO forms VALUES (?, ?, ?)", (form_name, json.dumps(questions), datetime.now().strftime("%m/%d/%Y %H:%M")))
        conn.commit()
        st.success("✅ Form Saved!")

def admin_project_page():
    st.title("📁 Assign Project")
    c.execute("SELECT form_name FROM forms")
    forms = [r[0] for r in c.fetchall()]
    project_name = st.text_input("Project Name")
    form_choice = st.selectbox("Choose Form to Use", forms if forms else ["No forms yet"])
    submission_days = st.multiselect("Days of Submission", ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    submission_time = st.time_input("Submission Time", value=time(10, 0))
    start_date = st.date_input("Start Date", value=date.today())
    end_date = st.date_input("End Date", value=date.today())
    assigned_to = st.selectbox("Assign To", [u for u in USERS if USERS[u]["role"] == "branch"])

    if st.button("Assign Project"):
        c.execute("INSERT INTO projects VALUES (?, ?, ?, ?, ?, ?, ?)", (project_name, assigned_to, form_choice, json.dumps(submission_days), submission_time.strftime("%H:%M"), start_date.strftime("%m/%d/%Y"), end_date.strftime("%m/%d/%Y")))
        conn.commit()
        st.success("📌 Project Assigned!")

# --- Branch Form Filling ---
def branch_user_page():
    st.title("📝 My Projects")
    c.execute("SELECT * FROM projects WHERE assigned_to = ?", (st.session_state.username,))
    my_projects = c.fetchall()

    if not my_projects:
        st.info("No projects assigned to you yet.")
        return

    selected_project = st.selectbox("Choose a Project", [p[0] for p in my_projects])
    selected = next(p for p in my_projects if p[0] == selected_project)
    c.execute("SELECT * FROM forms WHERE form_name = ?", (selected[2],))
    form = c.fetchone()

    if not form:
        st.error("Form not found!")
        return

    form_questions = json.loads(form[1])
    st.subheader(f"📋 Form: {form[0]}")
    st.write(f"Submit by {selected[4]} on {json.loads(selected[3])}")
    st.write(f"🗓️ Active from {selected[5]} to {selected[6]}")

    responses = {}
    for q in form_questions:
        if q["type"] == "Text":
            responses[q["label"]] = st.text_input(q["label"])
        elif q["type"] == "Yes/No":
            responses[q["label"]] = st.radio(q["label"], ["Yes", "No"])
        elif q["type"] == "Multiple Choice":
            responses[q["label"]] = st.selectbox(q["label"], q.get("options", []))
        elif q["type"] == "Number":
            responses[q["label"]] = st.number_input(q["label"], step=1.0)
        elif q["type"] == "Checkbox":
            responses[q["label"]] = st.checkbox(q["label"])
        elif q["type"] == "Date/Time":
            responses[q["label"]] = st.date_input(q["label"]).strftime("%m/%d/%Y")
        elif q["type"] == "Rating":
            responses[q["label"]] = st.slider(q["label"], 1, q.get("max_rating", 5))
        elif q["type"] == "Email":
            responses[q["label"]] = st.text_input(q["label"], placeholder="example@email.com")
        elif q["type"] == "Photo":
            uploaded = st.file_uploader(q["label"], type=["png", "jpg", "jpeg"])
            if uploaded:
                responses[q["label"]] = uploaded.name
                st.image(uploaded)
        elif q["type"] == "Video":
            uploaded = st.file_uploader(q["label"], type=["mp4", "mov", "avi"])
            if uploaded:
                responses[q["label"]] = uploaded.name
                st.video(uploaded)
        elif q["type"] == "Formula":
            responses[q["label"]] = f"= {q.get('formula', '')}"
        else:
            responses[q["label"]] = f"[{q['type']}] field here"

    if st.button("Submit Form"):
        c.execute("INSERT INTO submissions VALUES (?, ?, ?, ?, ?)", (
            selected_project,
            form[0],
            json.dumps(responses),
            st.session_state.username,
            datetime.now().strftime("%m/%d/%Y %H:%M")
        ))
        conn.commit()
        st.success("✅ Form submitted!")

# --- Main ---
if not st.session_state.logged_in:
    login_page()
else:
    if st.session_state.role == "admin":
        if "admin_page" not in st.session_state:
            st.session_state.admin_page = "Home"
        menu = st.sidebar.radio("Admin Menu", ["Home", "Form Builder", "Assign Projects"])
        st.session_state.admin_page = menu
        if st.session_state.admin_page == "Home":
            admin_home()
        elif st.session_state.admin_page == "Form Builder":
            admin_form_builder()
        elif st.session_state.admin_page == "Assign Projects":
            admin_project_page()
    else:
        branch_user_page()
