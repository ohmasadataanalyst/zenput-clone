import streamlit as st
from datetime import datetime, time, date, timedelta
import sqlite3
import json
import pandas as pd
import io

# --- Setup SQLite DB ---
conn = sqlite3.connect("zenput_data.db", check_same_thread=False)
c = conn.cursor()

# Create forms table
c.execute('''CREATE TABLE IF NOT EXISTS forms (
    form_name TEXT PRIMARY KEY,
    questions TEXT,
    created_at TEXT
)''')

# Create projects table (9 columns)
c.execute('''CREATE TABLE IF NOT EXISTS projects (
    project_name TEXT,
    assigned_to TEXT,
    form_used TEXT,
    days TEXT,
    start_time TEXT,
    end_time TEXT,
    start_date TEXT,
    end_date TEXT,
    recurring_period TEXT
)''')

# Create submissions table (5 columns)
c.execute('''CREATE TABLE IF NOT EXISTS submissions (
    project TEXT,
    form TEXT,
    responses TEXT,
    submitted_by TEXT,
    timestamp TEXT
)''')

# Create user_hierarchy table (8 columns)
c.execute('''CREATE TABLE IF NOT EXISTS user_hierarchy (
    first_name TEXT,
    last_name TEXT,
    role TEXT,
    permission TEXT,
    email TEXT,
    phone TEXT,
    date_joined TEXT,
    username TEXT PRIMARY KEY
)''')
conn.commit()

# --- Seed user_hierarchy data if empty ---
def seed_user_hierarchy():
    c.execute("SELECT COUNT(*) FROM user_hierarchy")
    if c.fetchone()[0] == 0:
        # --- Provided CSV data (Admins and Area Managers) ---
        csv_data1 = """First Name,Last Name,Role,Permission,Email,Phone,Date Joined
Accommodation,Account,Accommodation Submitter,Submitter,accommodation@aofgroup.com,9.6656E+11,1/6/2024 10:49
Ahmed,Quttb,Admin 1,Admin,a.quttb@aofgroup.com,2.01012E+11,2/23/2025 12:04
Test,Test,Admin 1,Admin,falyousefi@aofgroup.com,9.66559E+11,12/30/2023 16:17
Abdulkarim,Alarifi,Admin 1,Manager,alorifi_k@aofgroup.com,9.66544E+11,4/18/2023 21:22
Ahmed,Abduldim,Admin 1,Manager,a.abduldim@aofgroup.com,9.66537E+11,3/21/2023 11:11
Faisal,ALarifi,Admin 1,Admin,faisal@aofgroup.com,9.66544E+11,10/18/2022 16:08
Abdullah,Alrashed,Admin 1,Admin,alrashed@shawarmaclassic.com,9.66553E+11,8/16/2022 12:32
Omar,aloraifi,Admin 1,Admin,omar@aofgroup.com,9.66504E+11,11/6/2022 13:07
Shawarma,Classic,Admin 1,Owner,it@aofgroup.com,,6/27/2022 21:09
Mohammed,Albarqi,Albawasiq,Manager,m.albarqi@albawasiq.com,9.66502E+11,9/16/2024 13:20
"""
        # --- Provided CSV data (Sales Man Team) ---
        csv_data2 = """First Name,Last Name,Role,Permission,Email,Phone,Date Joined
Mohanad,Alshthly,Sales Man Team,Manager,cashvan@albawasiq.com,9.66556E+11,1/9/2025 14:01
H.,Alsamani,Sales Man Team,Manager,h.alsamani@albawasiq.com,9.66512E+11,9/30/2024 13:41
M.,Hashim,Sales Man Team,Manager,m.hashim@albawasiq.com,9.66594E+11,9/30/2024 13:28
Alsadeq,Alsadeq,Submitter,Submitter,shc.accommodation@gmail.com,9.66557E+11,1/23/2023 14:36
Abdulaziz,Alsalem,Submitter,Admin,a.alsalem@aofgroup.com,9.6655E+11,7/16/2022 15:15
Naim,Trainer,Trainers,Manager,trainer2@aofgroup.com,9.66555E+11,10/8/2024 13:22
Ananda,Trainer,Trainers,Manager,Trainer@aofgroup.com,9.66555E+11,10/6/2024 13:08
Twesste - تويستي,TW01,Twestee supervisor,Submitter,twessteb01@gmail.com,9.66596E+11,2/5/2023 9:20
Mohd Rashid,Padhan,WH role,Manager,m.rashid@aofgroup.com,9.66559E+11,12/23/2023 14:56
"""
        # Combine the CSV data (you can append more blocks as needed)
        combined_csv = csv_data1 + csv_data2
        df = pd.read_csv(io.StringIO(combined_csv))
        # Generate username by concatenating first and last names (lowercase, no spaces)
        df["username"] = (df["First Name"].str.lower() + df["Last Name"].str.lower()).str.replace(" ", "")
        for _, row in df.iterrows():
            # If any value is missing, fill with an empty string
            values = [str(row[col]) if pd.notnull(row[col]) else "" for col in 
                      ["First Name", "Last Name", "Role", "Permission", "Email", "Phone", "Date Joined", "username"]]
            c.execute("INSERT OR REPLACE INTO user_hierarchy VALUES (?, ?, ?, ?, ?, ?, ?, ?)", tuple(values))
        conn.commit()

seed_user_hierarchy()

# --- Build USERS dictionary from DB (with default password "pass") ---
def build_users_dict():
    c.execute("SELECT username, role FROM user_hierarchy")
    rows = c.fetchall()
    users_dict = {}
    for username, role in rows:
        users_dict[username] = {"password": "pass", "role": role}
    # Ensure admin is present with known credentials
    users_dict["admin"] = {"password": "admin123", "role": "admin"}
    # Add explicit branch supervisors (if not in hierarchy)
    users_dict["branch01"] = {"password": "b01pass", "role": "restaurant supervisor"}
    users_dict["branch02"] = {"password": "b02pass", "role": "restaurant supervisor"}
    users_dict["branch03"] = {"password": "b03pass", "role": "restaurant supervisor"}
    return users_dict

USERS = build_users_dict()

# --- Persistent Login using Query Parameters ---
params = st.query_params
if params.get("username") and params.get("role"):
    st.session_state.logged_in = True
    st.session_state.username = params["username"][0]
    st.session_state.role = params["role"][0]
else:
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
            st.set_query_params(username=username, role=user["role"])
            st.rerun()
        else:
            st.error("Invalid credentials")

# --- Logout Function ---
def logout():
    st.set_query_params()  # Clear query parameters
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

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
    if st.button("👥 Manage Users"):
        st.session_state.admin_page = "Users"

def admin_form_builder():
    st.title("🛠️ Form Builder")
    form_name = st.text_input("Form Name")
    num_fields = st.number_input("Number of Questions", 1, 20, 5)
    st.subheader("🧩 Define Questions")
    questions = []
    for i in range(int(num_fields)):
        q = {}
        q["label"] = st.text_input(f"Question {i+1} Text", key=f"label_{i}")
        q["type"] = st.selectbox("Type", 
            ["Text", "Yes/No", "Multiple Choice", "Number", "Checkbox", "Date/Time", 
             "Rating", "Email", "Stopwatch", "Photo", "Signature", "Barcode", "Video", 
             "Document", "Formula", "Location"], key=f"type_{i}")
        if q["type"] == "Multiple Choice":
            q["options"] = st.text_input(f"Options (comma-separated)", key=f"options_{i}").split(",")
        if q["type"] == "Rating":
            q["max_rating"] = st.slider(f"Max Rating", 1, 10, 5, key=f"rating_{i}")
        if q["type"] == "Formula":
            q["formula"] = st.text_input(f"Formula Expression", key=f"formula_{i}")
        questions.append(q)
    if st.button("Save Form"):
        c.execute("INSERT OR REPLACE INTO forms VALUES (?, ?, ?)", 
                  (form_name, json.dumps(questions), datetime.now().strftime("%m/%d/%Y %H:%M")))
        conn.commit()
        st.success("✅ Form Saved!")
        st.write("Current forms:", c.execute("SELECT * FROM forms").fetchall())

def admin_project_page():
    st.title("📁 Assign Project")
    c.execute("SELECT form_name FROM forms")
    forms = [r[0] for r in c.fetchall()]
    if not forms:
        st.error("No forms available. Please create a form first.")
        return
    project_name = st.text_input("Project Name")
    if not project_name.strip():
        st.error("Please enter a valid project name.")
        return
    form_choice = st.selectbox("Choose Form to Use", forms)
    assigned_to = st.selectbox("Assign To (enter 'role:restaurant supervisor' for mass assignment or choose a username)", 
                               list(USERS.keys()) + ["role:restaurant supervisor"])
    submission_days = st.multiselect("Days of Submission", 
                                     ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    allowed_start = st.time_input("Submission Window Start Time", value=time(1, 0))
    allowed_end = st.time_input("Submission Window End Time", value=time(2, 0))
    start_date = st.date_input("Project Start Date", value=date.today())
    end_date = st.date_input("Project End Date", value=date.today() + timedelta(days=7))
    recurring_period = st.selectbox("Recurring Period", ["One-Time", "Daily", "Weekly", "Quarterly", "Yearly"])
    if st.button("Assign Project"):
        c.execute("INSERT INTO projects VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (
            project_name, assigned_to, form_choice,
            json.dumps(submission_days),
            allowed_start.strftime("%H:%M"),
            allowed_end.strftime("%H:%M"),
            start_date.strftime("%m/%d/%Y"),
            end_date.strftime("%m/%d/%Y"),
            recurring_period
        ))
        conn.commit()
        st.success("📌 Project Assigned!")

def admin_projects_overview():
    st.title("📊 Projects Overview")
    c.execute("SELECT * FROM projects")
    all_projects = c.fetchall()
    valid_projects = [row for row in all_projects if len(row) == 9]
    if not valid_projects:
        st.info("No projects assigned yet or data is incomplete.")
        return
    cols = ["Project Name", "Assigned To", "Form", "Days", "Start Time", "End Time", "Start Date", "End Date", "Recurring"]
    try:
        df = pd.DataFrame(valid_projects, columns=cols)
        st.dataframe(df)
    except Exception as e:
        st.error(f"Projects Overview Data error: {e}")

def admin_users_tab():
    st.title("👥 User Hierarchy")
    c.execute("SELECT * FROM user_hierarchy")
    users = c.fetchall()
    if users:
        cols = ["First Name", "Last Name", "Role", "Permission", "Email", "Phone", "Date Joined", "Username"]
        try:
            df = pd.DataFrame(users, columns=cols)
            st.dataframe(df)
            st.download_button("📥 Download CSV", df.to_csv(index=False).encode(), "user_hierarchy.csv", "text/csv")
        except Exception as e:
            st.error(f"Users Data error: {e}")
    else:
        st.info("No user data found.")
    
    st.subheader("Add New User")
    new_first = st.text_input("First Name", key="new_first")
    new_last = st.text_input("Last Name", key="new_last")
    new_role = st.text_input("Role", key="new_role")
    new_permission = st.text_input("Permission", key="new_permission")
    new_email = st.text_input("Email", key="new_email")
    new_phone = st.text_input("Phone", key="new_phone")
    new_date_joined = st.text_input("Date Joined (MM/DD/YYYY HH:MM)", key="new_date_joined")
    new_username = st.text_input("Username", key="new_username")
    if st.button("Add User"):
        try:
            c.execute("INSERT INTO user_hierarchy VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                      (new_first, new_last, new_role, new_permission, new_email, new_phone, new_date_joined, new_username))
            conn.commit()
            st.success("User added successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

# --- Branch User Pages ---
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
    c.execute("SELECT * FROM projects")
    all_projects = c.fetchall()
    branch_projects = []
    for p in all_projects:
        assigned = p[1]
        if assigned.startswith("role:"):
            role = assigned.split("role:")[1]
            if st.session_state.role == role:
                branch_projects.append(p)
        elif assigned == st.session_state.username:
            branch_projects.append(p)
    today = date.today()
    current_time = datetime.now().time()
    active_projects = []
    for p in branch_projects:
        start_dt = datetime.strptime(p[6], "%m/%d/%Y").date()
        end_dt = datetime.strptime(p[7], "%m/%d/%Y").date()
        allowed_days = json.loads(p[3])
        allowed_start = datetime.strptime(p[4], "%H:%M").time()
        allowed_end = datetime.strptime(p[5], "%H:%M").time()
        if start_dt <= today <= end_dt and today.strftime("%A") in allowed_days:
            if allowed_start <= current_time <= allowed_end:
                active_projects.append(p)
    if not active_projects:
        st.info("No active projects available for submission at this time.")
        return
    selected_project = st.selectbox("Choose an Active Project", [p[0] for p in active_projects])
    selected = next(p for p in active_projects if p[0] == selected_project)
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
    st.write(f"Allowed submission window: {selected[4]} - {selected[5]}")
    st.write(f"Active from {selected[6]} to {selected[7]}")
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
            captured = st.camera_input(q["label"])
            if captured:
                responses[q["label"]] = captured.name
                st.image(captured)
        elif q["type"] == "Video":
            captured = st.camera_input(q["label"], label_visibility="visible")
            if captured:
                responses[q["label"]] = captured.name
                st.video(captured)
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
    c.execute("SELECT * FROM projects")
    all_projects = c.fetchall()
    branch_projects = []
    for p in all_projects:
        assigned = p[1]
        if assigned.startswith("role:"):
            role = assigned.split("role:")[1]
            if st.session_state.role == role:
                branch_projects.append(p)
        elif assigned == st.session_state.username:
            branch_projects.append(p)
    today = date.today()
    missed_projects = []
    for p in branch_projects:
        end_dt = datetime.strptime(p[7], "%m/%d/%Y").date()
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
        st.write(f"Submission Deadline: {p[7]}")
        st.write(f"Recurring Period: {p[8]}")
        st.markdown("---")

# --- Main ---
if not st.session_state.get("logged_in", False):
    login_page()
else:
    st.sidebar.markdown(f"👋 Logged in as: **{st.session_state.username}**")
    if st.sidebar.button("🚪 Logout"):
        logout()
    if st.session_state.role == "admin":
        if "admin_page" not in st.session_state:
            st.session_state.admin_page = "Home"
        menu = st.sidebar.radio("Admin Menu", ["Home", "Form Builder", "Assign Projects", "Projects Overview", "Users"])
        st.session_state.admin_page = menu
        if st.session_state.admin_page == "Home":
            admin_home()
        elif st.session_state.admin_page == "Form Builder":
            admin_form_builder()
        elif st.session_state.admin_page == "Assign Projects":
            admin_project_page()
        elif st.session_state.admin_page == "Projects Overview":
            admin_projects_overview()
        elif st.session_state.admin_page == "Users":
            admin_users_tab()
    else:
        branch_home()
