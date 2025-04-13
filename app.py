import streamlit as st
from datetime import datetime

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
        st.session_state.saved_form = {
            "form_name": form_name,
            "questions": questions,
            "created_at": datetime.now().strftime("%m/%d/%Y %H:%M")
        }
        st.success("✅ Form Saved!")
        st.write(st.session_state.saved_form)

# --- Main ---
if not st.session_state.logged_in:
    login_page()
else:
    if st.session_state.role == "admin":
        admin_form_builder()
    else:
        st.info("📋 Branch form filling will be implemented next.")

     
