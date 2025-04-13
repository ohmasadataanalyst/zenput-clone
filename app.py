import streamlit as st
from datetime import datetime, time

# --- Simulated user roles (in real app, use auth) ---
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "branch01": {"password": "b01pass", "role": "branch"},
    "branch02": {"password": "b02pass", "role": "branch"},
}

# --- Session State Init ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

if "saved_forms" not in st.session_state:
    st.session_state.saved_forms = []

if "projects" not in st.session_state:
    st.session_state.projects = []

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

# --- Admin Home Page ---
def admin_home():
    st.title("🏠 Admin Home")
    st.write("Welcome, admin. Choose an action below:")
    if st.button("➕ Create New Form"):
        st.session_state.admin_page = "Form Builder"
    if st.button("📁 Assign New Project"):
        st.session_state.admin_page = "Assign Projects"

# --- Admin Form Builder ---
def admin_form_builder():
    st.title("🛠️ Form Builder")
    st.write("Create a new checklist form")

    form_name = st.text_input("Form Name")
    num_fields = st.number_input("Number of Questions", 1, 20, 5)

    st.subheader("🧩 Define Questions")
    questions = []
    for i in range(int(num_fields)):
        q = {}
        q["label"] = st.text_input(f"Question {i+1} Text", key=f"label_{i}")
        q["type"] = st.selectbox(
            f"Question {i+1} Type",
            [
                "Text", "Yes/No", "Multiple Choice", "Number", "Checkbox", "Date/Time", "Rating", "Email", "Stopwatch",
                "Photo", "Signature", "Barcode", "Video", "Document",
                "Formula", "Location"
            ],
            key=f"type_{i}"
        )

        if q["type"] == "Multiple Choice":
            q["options"] = st.text_input(f"Options for Q{i+1} (comma-separated)", key=f"options_{i}").split(",")
        if q["type"] == "Rating":
            q["max_rating"] = st.slider(f"Max Rating for Q{i+1}", 1, 10, 5, key=f"rating_{i}")
        if q["type"] == "Formula":
            q["formula"] = st.text_input(f"Formula Expression for Q{i+1}", key=f"formula_{i}")

        questions.append(q)

    if st.button("Save Form"):
        new_form = {
            "form_name": form_name,
            "questions": questions,
            "created_at": datetime.now().strftime("%m/%d/%Y %H:%M")
        }
        st.session_state.saved_forms.append(new_form)
        st.success("✅ Form Saved!")
        st.write(new_form)

# --- Admin Project Assignment ---
def admin_project_page():
    st.title("📁 Assign Project")

    project_name = st.text_input("Project Name")
    available_forms = [f["form_name"] for f in st.session_state.saved_forms]
    form_choice = st.selectbox("Choose Form to Use", available_forms if available_forms else ["No forms yet"])
    submission_days = st.multiselect("Days of Submission", ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    submission_time = st.time_input("Submission Time", value=time(10, 0))

    if st.button("Assign Project"):
        new_project = {
            "project_name": project_name,
            "assigned_to": st.session_state.username,
            "form_used": form_choice,
            "days": submission_days,
            "time": submission_time.strftime("%H:%M")
        }
        st.session_state.projects.append(new_project)
        st.success("📌 Project Assigned!")
        st.write(new_project)

# --- Branch User Form Filling ---
def branch_user_page():
    st.title("📝 My Projects")

    my_projects = [p for p in st.session_state.projects if p["assigned_to"] == st.session_state.username]

    if not my_projects:
        st.info("No projects assigned to you yet.")
        return

    selected_project = st.selectbox("Choose a Project", [p["project_name"] for p in my_projects])
    selected = next(p for p in my_projects if p["project_name"] == selected_project)
    form = next((f for f in st.session_state.saved_forms if f["form_name"] == selected["form_used"]), None)

    if not form:
        st.error("Form not found!")
        return

    st.subheader(f"📋 Form: {form['form_name']}")
    st.write(f"Submit by {selected['time']} on {', '.join(selected['days'])}")

    responses = {}
    for q in form["questions"]:
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
            responses[q["label"]] = st.date_input(q["label"])
        elif q["type"] == "Rating":
            responses[q["label"]] = st.slider(q["label"], 1, q.get("max_rating", 5))
        elif q["type"] == "Email":
            responses[q["label"]] = st.text_input(q["label"], placeholder="example@email.com")
        elif q["type"] == "Formula":
            responses[q["label"]] = f"= {q.get('formula', '')}"
        else:
            responses[q["label"]] = f"[{q['type']}] field here"

    if st.button("Submit Form"):
        st.success("✅ Form submitted!")
        st.write(responses)

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
