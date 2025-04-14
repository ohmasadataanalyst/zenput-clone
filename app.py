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

# Create projects table with 9 columns
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

# Create user_hierarchy table with 8 columns
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

# --- Seed user hierarchy data if empty ---
def seed_user_hierarchy():
    c.execute("SELECT COUNT(*) FROM user_hierarchy")
    if c.fetchone()[0] == 0:
        # Replace the CSV data below with your full data if needed.
        csv_data = """First Name,Last Name,Role,Permission,Email,Phone,Date Joined
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
????,??????,Albawasiq,Manager,a.suliman@albawasiq.com,9.66545E+11,8/30/2023 16:09
Mohamed ezz,Ali,Albawasiq factory 2,Manager,m.ezz@albawasiq.com,9.66583E+11,12/21/2022 22:17
MAHER,ABOUELMAATY,Albawasiq Factory 3,Admin,m.abouelmaaty@albawasiq.com,9.66541E+11,10/22/2023 12:08
Omar,Haider,Albawasiq Quality inspectors,Submitter,o.haider@albawasiq.com,9.66556E+11,12/3/2023 9:10
Omar,Qasamallah,Albawasiq Quality inspectors,Submitter,o.qasamallah@albawasiq.com,9.66593E+11,12/3/2023 9:08
Albawasiq,Security,Albawasiq security,Submitter,security@albawasiq.com,9.66556E+11,12/24/2023 8:53
Allam,Mahmud,Area Manager,Manager,a.mahmud@aofgroup.com,9.66551E+11,1/24/2025 19:59
Ali,Esmaeel,Area Manager,Manager,a.suliman@aofgroup.com,9.66562E+11,10/20/2024 11:27
Sohel,Sohel,Area Manager,Manager,sohel@aofgroup.com,9.66595E+11,8/13/2024 13:40
Helal,Aldin,Area Manager,Manager,helal@aofgroup.com,9.66541E+11,8/13/2024 13:34
Robi,Alam,Area Manager,Manager,r.alam@aofgroup.com,9.66547E+11,1/23/2024 21:22
Khaled,Mohamed,Area Manager,Manager,k.abdulnaby@aofgroup.com,2.01156E+11,4/17/2023 12:53
sh,sh,Area Manager,Manager,it@shawarmaclassic.com,9.66559E+11,4/4/2023 10:30
Aseel,Abdullah,Area Manager,Manager,a.banafe@aofgroup.com,9.665E+11,1/17/2023 14:31
Sujan,Poudel,Area Manager,Manager,s.poudel@aofgroup.com,9.66596E+11,11/17/2022 11:14
Mohammed,Emad,Area Manager,Manager,m.emad@aofgroup.com,9.66596E+11,9/11/2022 13:38
Mohamed,El haoudar,Area Manager,Manager,m.alhuaydar@aofgroup.com,9.66581E+11,7/17/2022 12:02
Islam,Mostafa,Area manager 2,Manager,i.mostafa@aofgroup.com,9.66565E+11,6/5/2023 13:40
Subash,Poudal,Area Manager5,Submitter,subash@shawarmaclassic.com,9.66548E+11,12/10/2023 3:17
CCTV,Department,Checking,Manager,cctvdep@aofgroup.com,9.66515E+11,12/9/2024 11:21
Ahmed,Alminshawi,Checking,Manager,a.alminshawi@aofgroup.com,9.66512E+11,12/8/2024 13:06
M.,Faizan,Checking,Manager,m.faizan@aofgroup.com,9.66599E+11,10/22/2024 23:39
Tolen,Alhamdan,Checking,Manager,t.alhamdan@aofgroup.com,9.66533E+11,10/14/2024 12:05
Seham,Alfunaysan,Checking,Manager,s.alfunaysan@aofgroup.com,9.66555E+11,10/14/2024 12:01
Mukhtar,Ali,Checking,Manager,m.ali@aofgroup.com,9.66597E+11,7/14/2024 14:30
Hassan,Farouq,Checking,Manager,h.farouq@aofgroup.com,9.66591E+11,4/27/2024 12:49
Lena,Alorafe,Checking,Manager,lena@aofgroup.com,9.66558E+11,2/24/2024 13:32
Ahmed,Khaled,Checking,Manager,a.khaled@aofgroup.com,2.01061E+11,2/17/2024 14:13
Omar,Salahaddin,Checking,Manager,o.salahaddin@aofgroup.com,2.01122E+11,1/11/2024 9:21
????,?????,Checking,Manager,m.alsaned@shawarmaclassic.com,9.66597E+11,9/27/2023 10:43
customers,service,Customer service,Manager,wecare@aofgroup.com,9.66556E+11,4/21/2024 1:58
Abdulmalik,Alghanmi,Customer service,Manager,a.alghanmi@aofgroup.com,9.66537E+11,12/14/2022 11:03
mohamed,abdullah,Development Manager,Admin,m.abdullah@aofgroup.com,9.66549E+11,11/7/2022 8:24
Mahmoud,Mostafa,Fianance,Manager,m.mostafa@aofgroup.com,2.01127E+11,4/13/2023 16:25
Garatis Alnarjis,QB02,Garatees supervisor,Submitter,shawarmagaratisb02@gmail.com,9.66535E+11,8/21/2024 12:48
Garatis As Suwaidi,QB01,Garatees supervisor,Submitter,shawarmagaratisb01@gmail.com,9.66596E+11,7/23/2024 15:50
Mohab,Abdulmughni,HR,Manager,m.abdulmughni@aofgroup.com,9.66504E+11,8/21/2024 12:37
Tarique,Khan,HR,Manager,t.khan@aofgroup.com,9.66546E+11,10/29/2023 12:14
???????,???????,HR,Manager,a.hammad@aofgroup.com,9.6655E+11,1/10/2023 10:49
Ali,Alanzi,HR,Submitter,a.alanzi@shawarmaclassic.com,9.66551E+11,10/17/2022 10:59
????,?????,HR,Manager,m.aldamaeen@aofgroup.com,9.66537E+11,10/12/2022 15:25
Lubda khaleej,LB02,Lubda Supervisor,Manager,b02@lubdasa.com,9.66595E+11,4/2/2024 13:13
Lubda aqiq,LB01,Lubda Supervisor,Manager,a.alghanimi@lubdasa.com,9.66583E+11,11/27/2022 13:21
Ahmed,Nasr,Maintenance Role,Manager,a.nasr@aofgroup.com,9.66593E+11,1/7/2024 14:35
wagd,yousif,Maintenance Role,Manager,w.yousif@aofgroup.com,9.66531E+11,12/25/2023 23:48
????,???????,Maintenance Role,Manager,w.alhanani@aofgroup.com,9.66594E+11,12/24/2023 12:40
Ahmed,OMARA,Operation Manager,Admin,a.omara@aofgroup.com,9.66544E+11,7/7/2022 11:17
Hassan,Alwusaibie,Quality Inspectors,Manager,h.alwusaibie@aofgroup.com,9.66559E+11,2/13/2025 20:59
Ahmed,Abdelhamid,Quality Inspectors,Manager,a.ahmed@aofgroup.com,9.66548E+11,9/17/2024 13:22
Abdullah,Alamri,Quality Inspectors,Manager,a.alamri@aofgroup.com,9.66598E+11,5/19/2024 12:58
SAIF,Al,Quality Inspectors,Manager,s.albraiki@aofgroup.com,9.66054E+12,1/29/2024 21:55
Abdulrheem,Quality inspector,Quality Inspectors,Manager,abdulrheem@shawarmaclassic.com,9.66556E+11,12/3/2023 9:04
Osama,Albawasiq,Quality Inspectors,Manager,b.s.c@shawarmaclassic.com,9.6656E+11,6/18/2023 11:49
Yasser,Yasser,Quality Inspectors,Submitter,albawasiqsecur@gmail.com,9.66536E+11,2/28/2023 15:35
????,????,Quality Inspectors,Manager,e.hamwi@shawarmaclassic.com,9.66592E+11,11/27/2022 14:07
ShawarmaClassicCCTV,CCTV,Quality Inspectors,Submitter,shawarmaclassiccctv9@gmail.com,9.66555E+11,11/21/2022 20:40
URURUH,B34,Restaurant Supervisor,Submitter,aloruba@aofgroup.com,9.66557E+11,11/23/2024 14:37
HIRJED,B33,Restaurant Supervisor,Submitter,marwa2jed@gmail.com,9.66555E+11,10/20/2024 14:25
FAYJED,B32,Restaurant Supervisor,Submitter,faihaje@gmail.com,9.66535E+11,9/24/2024 14:27
ANRUH,B31,Restaurant Supervisor,Submitter,classicanas@gmail.com,9.66539E+11,8/15/2024 13:06
QADRUH,B30,Restaurant Supervisor,Submitter,sclassicqadruh@gmail.com,9.66599E+11,12/23/2023 14:54
MAJED,B28,Restaurant Supervisor,Submitter,sclassicmajed@gmail.com,9.66597E+11,11/25/2023 18:16
SARUH,B27,Restaurant Supervisor,Submitter,shawarmaclassicb27@gmail.com,9.66553E+11,7/31/2023 16:55
HAJED,B26,Restaurant Supervisor,Submitter,shawarmaclassicb26@gmail.com,9.66596E+11,6/26/2023 9:22
LBRUH,B07,Restaurant Supervisor,Submitter,shawarmaclassicb07@gmail.com,9.66555E+11,6/17/2023 21:31
RWAHS,B25,Restaurant Supervisor,Submitter,shawarmaclassicb25@gmail.com,9.66599E+11,6/10/2023 14:43
SFJED,B24,Restaurant Supervisor,Submitter,shawarmaclassicb24@gmail.com,9.66593E+11,4/9/2023 12:24
SLAHS,B23,Restaurant Supervisor,Submitter,shawarmaclassicb23@gmail.com,9.66556E+11,2/19/2023 9:07
OBJED,B22,Restaurant Supervisor,Submitter,shawarmaclassicb22@gmail.com,9.66599E+11,2/1/2023 12:34
TKRUH,B18,Restaurant Supervisor,Submitter,shawarmaclassicb18@outlook.com,,9/6/2022 2:21
MURUH,B19,Restaurant Supervisor,Submitter,shawarmaclassicb19@outlook.com,,9/6/2022 2:21
KRRUH,B21,Restaurant Supervisor,Submitter,shawarmaclassicb21@gmail.com,,9/6/2022 2:21
NRRUH,B11,Restaurant Supervisor,Submitter,shawarmaclassicB11@gmail.com,,9/6/2022 2:21
TWRUH,B12,Restaurant Supervisor,Submitter,shawarmaclassicb12@gmail.com,,9/6/2022 2:21
RBRUH,B14,Restaurant Supervisor,Submitter,shawarmaB14@gmail.com,,9/6/2022 2:21
NDRUH,B15,Restaurant Supervisor,Submitter,shawarmaclassicb15@gmail.com,,9/6/2022 2:21
BDRUH,B16,Restaurant Supervisor,Submitter,shawarmaclassicb16@gmail.com,,9/6/2022 2:21
QRRUH,B17,Restaurant Supervisor,Submitter,Shawarmaclassicb17@outlook.com,,9/6/2022 2:21
NSRUH,B04,Restaurant Supervisor,Submitter,shawarmaclassicb04@gmail.com,,9/6/2022 2:21
RAWRUH,B05,Restaurant Supervisor,Submitter,shawarmaclassicB33@gmail.com,,9/6/2022 2:21
DARUH,B06,Restaurant Supervisor,Submitter,shawarmaclassicB6@gmail.com,,9/6/2022 2:21
SWRUH,B08,Restaurant Supervisor,Submitter,shawarmaclassicB8@gmail.com,,9/6/2022 2:21
AZRUH,B09,Restaurant Supervisor,Submitter,shawarmaclassicB9@gmail.com,,9/6/2022 2:21
SHRUH,B10,Restaurant Supervisor,Submitter,shawarmaclassicB10@gmail.com,,9/6/2022 2:21
KHRUH,B02,Restaurant Supervisor,Submitter,shawarmaclassick@gmail.com,,9/6/2022 2:21
GHRUH,B03,Restaurant Supervisor,Submitter,shawarmaclassicb03@gmail.com,,9/6/2022 2:21
AQRUH,B13,Restaurant Supervisor,Submitter,shawarmab13@gmail.com,9.66555E+11,9/28/2022 18:21
NURUH,B01,Restaurant Supervisor,Submitter,shawarmaclassicn@gmail.com,9.66583E+11,7/7/2022 9:55
First Name,Last Name,Role,Permission,Email,Phone,Date Joined
Mohanad,Alshthly,Sales Man Team,Manager,cashvan@albawasiq.com,9.66556E+11,1/9/2025 14:01
H.,Alsamani,Sales Man Team,Manager,h.alsamani@albawasiq.com,9.66512E+11,9/30/2024 13:41
M.,Hashim,Sales Man Team,Manager,m.hashim@albawasiq.com,9.66594E+11,9/30/2024 13:28
Alsadeq,Alsadeq,Submitter,Submitter,shc.accommodation@gmail.com,9.66557E+11,1/23/2023 14:36
Abdulaziz,Alsalem,Submitter,Admin,a.alsalem@aofgroup.com,9.6655E+11,7/16/2022 15:15
Naim,Trainer,Trainers,Manager,trainer2@aofgroup.com,9.66555E+11,10/8/2024 13:22
Ananda,Trainer,Trainers,Manager,Trainer@aofgroup.com,9.66555E+11,10/6/2024 13:08
Twesste - ??????,TW01,Twestee supervisor,Submitter,twessteb01@gmail.com,9.66596E+11,2/5/2023 9:20
Mohd Rashid,Padhan,WH role,Manager,m.rashid@aofgroup.com,9.66559E+11,12/23/2023 14:56

"""
        df = pd.read_csv(io.StringIO(csv_data))
        # Generate username by concatenating first and last names (lowercase, no spaces)
        df["username"] = (df["First Name"].str.lower() + df["Last Name"].str.lower()).str.replace(" ", "")
        for _, row in df.iterrows():
            c.execute("INSERT INTO user_hierarchy VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (
                row["First Name"], row["Last Name"], row["Role"], row["Permission"],
                row["Email"], row["Phone"], row["Date Joined"], row["username"]
            ))
        conn.commit()

seed_user_hierarchy()

# --- Build USERS dictionary automatically from DB for seeded users ---
def build_users_dict():
    c.execute("SELECT username, role FROM user_hierarchy")
    rows = c.fetchall()
    users_dict = {}
    for username, role in rows:
        # Assign a default password "pass" to each seeded user
        users_dict[username] = {"password": "pass", "role": role}
    # Ensure admin is present with known credentials
    users_dict["admin"] = {"password": "admin123", "role": "admin"}
    # Also add some explicit branch supervisors if not already present:
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
