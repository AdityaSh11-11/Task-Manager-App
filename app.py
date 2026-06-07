import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import hashlib
from datetime import datetime, date, time

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Smart Task Manager", layout="wide")

# ================= THEME =================
st.markdown("""
<style>

/* MAIN BACKGROUND */
.stApp {
    background-color: #014A43;
    color: white;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: black;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* BUTTONS */
.stButton button {
    background-color: ;
    color: white;
    border-radius: 8px;
    border: none;
    font-weight: 600;
}

.stButton button:hover {
    background-color: #22c55e;
}

/* INPUTS */
input, textarea {
    background-color:  !important;
    color: white !important;
    border: 1px solid black !important;
}

/* SELECT BOX */
.stSelectbox div {
    background-color:  !important;
    color: white !important;
}

/* METRICS */
[data-testid="stMetricValue"] {
    color: #22c55e !important;
}

/* FOOTER */
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: #0b0f1a;
    color: white;
    text-align: center;
    padding: 12px;
    font-size: 14px;
    border-top: 1px solid #333;
    z-index: 9999;
}

.main .block-container {
    padding-bottom: 80px;
}

</style>
""", unsafe_allow_html=True)

# ================= SESSION STATE =================
if "users" not in st.session_state:
    st.session_state.users = {}

if "auth" not in st.session_state:
    st.session_state.auth = False

if "user" not in st.session_state:
    st.session_state.user = ""

if "tasks" not in st.session_state:
    st.session_state.tasks = {}

# ================= SECURITY =================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ================= LOGIN =================
def login_page():
    st.title("Login")

    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login"):
        if username in st.session_state.users and \
           st.session_state.users[username] == hash_password(password):

            st.session_state.auth = True
            st.session_state.user = username

            if username not in st.session_state.tasks:
                st.session_state.tasks[username] = []

            st.success("Login Successful")
            st.rerun()

        else:
            st.error("Invalid Credentials")

# ================= SIGNUP =================
def signup_page():
    st.title("Signup")

    username = st.text_input("Create Username", key="signup_user")
    password = st.text_input("Create Password", type="password", key="signup_pass")

    if st.button("Signup"):
        if username.strip() == "":
            st.error("Username cannot be empty")

        elif username in st.session_state.users:
            st.error("User already exists")

        else:
            st.session_state.users[username] = hash_password(password)
            st.session_state.tasks[username] = []
            st.success("Account created! Now login")

# ================= AUTH GATE =================
if not st.session_state.auth:
    menu = st.sidebar.selectbox("Menu", ["Login", "Signup"])

    if menu == "Login":
        login_page()
    else:
        signup_page()

    st.stop()

# ================= USER DATA =================
user = st.session_state.user
tasks = st.session_state.tasks[user]

# ================= SIDEBAR =================
st.sidebar.title("Smart Task Manager")

st.sidebar.write(f"Logged in as: **{user}**")

if st.sidebar.button("Logout"):
    st.session_state.auth = False
    st.session_state.user = ""
    st.rerun()

page = st.sidebar.radio(
    "Navigate",
    ["Add Task", "Tasks Overview", "Analytics", "Delete Tasks"]
)

# ================= ADD TASK =================
if page == "Add Task":
    st.title("Add Task")

    task = st.text_input("Task Name")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    deadline = st.date_input("Deadline", value=date.today())
    reminder_time = st.time_input("Reminder Time")

    if st.button("Add Task"):
        if task.strip():

            tasks.append({
                "task": task,
                "priority": priority,
                "status": "Pending",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "deadline": f"{deadline} {reminder_time}",
                "reminder": f"{deadline} {reminder_time}"
            })

            st.session_state.tasks[user] = tasks
            st.success("Task Added Successfully")

        else:
            st.error("Task cannot be empty")

# ================= VIEW TASKS =================
elif page == "Tasks Overview":
    st.title("Tasks Overview")

    if not tasks:
        st.info("No tasks available.")
    else:

        df = pd.DataFrame(tasks)

        # ================= FILTERS =================
        col1, col2 = st.columns(2)

        with col1:
            status_filter = st.selectbox(
                "Filter by Status",
                ["All", "Pending", "Completed"]
            )

        with col2:
            priority_filter = st.selectbox(
                "Filter by Priority",
                ["All", "Low", "Medium", "High"]
            )

        # ================= APPLY FILTERS =================
        filtered_df = df.copy()

        if status_filter != "All":
            filtered_df = filtered_df[filtered_df["status"] == status_filter]

        if priority_filter != "All":
            filtered_df = filtered_df[filtered_df["priority"] == priority_filter]


        # ================= CALENDAR STYLE TABLE =================
        st.dataframe(
            filtered_df[["task", "priority", "status", "created_at", "deadline"]],
            use_container_width=True
        )

        # ================= TASK CARDS =================
        st.subheader("")

        for i, t in filtered_df.iterrows():

            col1, col2, col3, col4 = st.columns([4, 2, 2, 2])

            with col1:
                st.markdown(f"**{t['task']}**")

            with col2:
                st.write(f"{t['priority']}")

            with col3:
                st.write(f"{t['status']}")

            with col4:
                if st.button("✔ Complete", key=f"done_{i}"):
                    df.loc[i, "status"] = "Completed"
                    st.session_state.tasks[user] = df.to_dict("records")
                    st.rerun()

        # ================= DOWNLOAD =================
        st.download_button(
            "Download Tasks",
            df.to_csv(index=False),
            file_name="tasks.csv"
        )
# ================= ANALYTICS =================
elif page == "Analytics":
    st.title("Productivity Dashboard")

    if not tasks:
        st.info("No data available")
    else:
        df = pd.DataFrame(tasks)

        total = len(df)
        completed = len(df[df["status"] == "Completed"])
        pending = total - completed

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Tasks", total)
        col2.metric("Completed", completed)
        col3.metric("Pending", pending)

        # PIE CHART
        fig, ax = plt.subplots()
        ax.pie(
            [completed, pending],
            labels=["Completed", "Pending"],
            autopct="%1.1f%%",
            colors=["#22c55e", "#ef4444"]
        )
        st.pyplot(fig)

        # BAR CHART
        fig, ax = plt.subplots()
        df["priority"].value_counts().plot(kind="bar", ax=ax)
        st.pyplot(fig)

        # SCORE
        score = (completed / total) * 100 if total > 0 else 0
        st.metric("Productivity Score", f"{score:.2f}%")

# ================= DELETE TASKS =================
elif page == "Delete Tasks":
    st.title("🗑 Delete All Tasks")

    if st.button("Clear All Tasks"):
        st.session_state.tasks[user] = []
        st.success("All tasks deleted!")
        st.rerun()

# ================= FOOTER =================
st.markdown("""
<div class="footer">
    Smart Task Manager | Developed by Aditya Sharma | © 2026 All Rights Reserved
</div>
""", unsafe_allow_html=True)