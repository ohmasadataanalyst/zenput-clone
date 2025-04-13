import streamlit as st
from datetime import datetime, time, date
import sqlite3
import json
import pandas as pd

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
            st.experimental_rerun()
        else:
            st.error("Invalid credentials")

# --- Logout Function ---
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.experimental_rerun()

# --- Admin Pages ---
def admin_home():
    st.title("🏠 Admin Home")
    st.write("Welcome, admin. Choose an action below:")
    if st.button("➕ Create New Form"):
        st.session_state.admin_page = "Form Builder"
    if st.button("📁 Assign New Project"):
        st.session_state.admin_page = "Assign Projects"
    if st.button("📊 View Projects Overview"):
        st.session_state.admin_page = "Projects Overview"

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
    assigned_to = st.selectbox("Assign To Branch", [u for u in USERS if USERS[u]["role"] == "branch"])
    submission_days = st.multiselect("Days of Submission", ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    submission_time = st.time_input("Submission Time", value=time(10, 0))
    start_date = st.date_input("Start Date", value=date.today())
    end_date = st.date_input("End Date", value=date.today())

    if st.button("Assign Project"):
        c.execute("INSERT INTO projects VALUES (?, ?, ?, ?, ?, ?, ?)", (
            project_name, assigned_to, form_choice,
            json.dumps(submission_days),
            submission_time.strftime("%H:%M"),
            start_date.strftime("%m/%d/%Y"),
            end_date.strftime("%m/%d/%Y")
        ))
        conn.commit()
        st.success("📌 Project Assigned!")

def admin_projects_overview():
    st.title("📊 Projects Overview")
    c.execute("SELECT * FROM projects")
    all_projects = c.fetchall()
    if not all_projects:
        st.info("No projects assigned yet.")
        return

    df = pd.DataFrame(all_projects, columns=["Project Name", "Assigned To", "Form", "Days", "Time", "Start Date", "End Date"])
    st.dataframe(df)

# --- Branch User Homepage with Projects Tab ---
def branch_home():
    st.title("🏠 Branch Home")
    st.write(f"Welcome, {st.session_state.username}!")
    view = st.radio("Select View", ["Active Projects", "Submitted Projects", "Missed Submissions"])

    if view == "Active Projects":
        branch_active_projects()
    elif view == "Submitted Projects":
        branch_submitted_projects()
    elif view == "Missed Submissions":
        branch_missed_submissions()

def branch_active_projects():
    st.subheader("📋 Active Projects")
    c.execute("SELECT * FROM projects WHERE assigned_to = ?", (st.session_state.username,))
    projects = c.fetchall()
    today = date.today()
    active_projects = []
    for p in projects:
        # p[5] is start date, p[6] is end date, p[3] is JSON list of days
        start_dt = datetime.strptime(p[5], "%m/%d/%Y").date()
        end_dt = datetime.strptime(p[6], "%m/%d/%Y").date()
        allowed_days = json.loads(p[3])
        if start_dt <= today <= end_dt and today.strftime("%A") in allowed_days:
            active_projects.append(p)

    if not active_projects:
        st.info("No active projects available for submission today.")
        return

    selected_project = st.selectbox("Choose an Active Project", [p[0] for p in active_projects])
    selected = next(p for p in active_projects if p[0] == selected_project)
    # Check if submission already exists:
    c.execute("SELECT * FROM submissions WHERE project = ? AND submitted_by = ?", (selected_project, st.session_state.username))
    submission = c.fetchone()
    if submission:
        st.success("You have already submitted for this project.")
        return

    c.execute("SELECT * FROM forms WHERE form_name = ?", (selected[2],))
    form = c.fetchone()
    if not form:
        st.error("Form not found!")
        return

    form_questions = json.loads(form[1])
    st.subheader(f"🧾 Form: {form[0]}")
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

def branch_submitted_projects():
    st.subheader("📜 Submitted Projects")
    c.execute("SELECT * FROM submissions WHERE submitted_by = ?", (st.session_state.username,))
    submitted = c.fetchall()
    if not submitted:
        st.info("No submitted forms yet.")
        return

    for sub in submitted:
        st.markdown(f"### 📌 {sub[0]}")
        st.write(f"Form: {sub[1]}")
        st.write(f"Submitted at: {sub[4]}")
        responses = json.loads(sub[2])
        df = pd.DataFrame(responses.items(), columns=["Question", "Response"])
        st.dataframe(df)
        st.download_button("📥 Download as Excel", df.to_csv(index=False).encode(), file_name=f"{sub[0]}_{sub[4].replace('/', '-')}.csv", mime="text/csv")
        st.markdown("---")

def branch_missed_submissions():
    st.subheader("⛔ Missed Submissions")
    c.execute("SELECT * FROM projects WHERE assigned_to = ?", (st.session_state.username,))
    projects = c.fetchall()
    today = date.today()
    missed_projects = []
    for p in projects:
        end_dt = datetime.strptime(p[6], "%m/%d/%Y").date()
        # Consider a project missed if today is past the end date and no submission was recorded.
        c.execute("SELECT * FROM submissions WHERE project = ? AND submitted_by = ?", (p[0], st.session_state.username))
        submission = c.fetchone()
        if today > end_dt and not submission:
            missed_projects.append(p)
    if not missed_projects:
        st.info("No missed submissions.")
        return
    for p in missed_projects:
        st.markdown(f"### 📌 {p[0]}")
        st.write(f"Assigned Form: {p[2]}")
        st.write(f"Submission Deadline: {p[6]}")
        st.markdown("---")

# --- Main ---
if not st.session_state.logged_in:
    login_page()
else:
    st.sidebar.markdown(f"👋 Logged in as: **{st.session_state.username}**")
    if st.sidebar.button("🚪 Logout"):
        logout()

    if st.session_state.role == "admin":
        if "admin_page" not in st.session_state:
            st.session_state.admin_page = "Home"
        menu = st.sidebar.radio("Admin Menu", ["Home", "Form Builder", "Assign Projects", "Projects Overview"])
        st.session_state.admin_page = menu
        if st.session_state.admin_page == "Home":
            admin_home()
        elif st.session_state.admin_page == "Form Builder":
            admin_form_builder()
        elif st.session_state.admin_page == "Assign Projects":
            admin_project_page()
        elif st.session_state.admin_page == "Projects Overview":
            admin_projects_overview()
    else:
        # Branch homepage with projects tab
        branch_home()
