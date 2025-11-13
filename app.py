import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title="Delvero Payroll",
    page_icon="🗞️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# Database connection
# -----------------------------
conn = sqlite3.connect('payroll.db', check_same_thread=False)
c = conn.cursor()

# -----------------------------
# Create tables if not exist
# -----------------------------
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT,
    manager_id INTEGER
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    date TEXT,
    wijk TEXT,
    segments INTEGER,
    note TEXT
)
''')
conn.commit()

# -----------------------------
# Initialize default users (Maryam + employees)
# -----------------------------
def initialize_default_users():
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]
    if count == 0:
        # Add main manager
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  ("Maryam", "1234", "manager"))
        conn.commit()

        # Get manager ID
        c.execute("SELECT id FROM users WHERE username='Maryam'")
        manager_id = c.fetchone()[0]

        # Add employees
        employees = ["Hoshyar", "Hossein", "Masoud"]
        for emp in employees:
            c.execute("INSERT INTO users (username, password, role, manager_id) VALUES (?, ?, ?, ?)",
                      (emp, "1234", "employee", manager_id))
        conn.commit()
        print("✅ Default users created.")
    else:
        print("ℹ️ Users already exist.")

initialize_default_users()

# -----------------------------
# Database helper functions
# -----------------------------
def check_login(username, password):
    c.execute('SELECT id, role, manager_id FROM users WHERE username=? AND password=?',
              (username, password))
    return c.fetchone()

def add_user(username, password, role, manager_id=None):
    try:
        c.execute('INSERT INTO users (username, password, role, manager_id) VALUES (?, ?, ?, ?)',
                  (username, password, role, manager_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def add_activity(user_id, wijk, segments, note):
    c.execute('INSERT INTO activities (user_id, date, wijk, segments, note) VALUES (?, ?, ?, ?, ?)',
              (user_id, str(date.today()), wijk, segments, note))
    conn.commit()

def get_activities_by_user(user_id):
    c.execute('SELECT date, wijk, segments, note FROM activities WHERE user_id=? ORDER BY date DESC', (user_id,))
    return c.fetchall()

def get_employees_by_manager(manager_id):
    c.execute('SELECT id, username FROM users WHERE manager_id=?', (manager_id,))
    return c.fetchall()

def get_all_activities_for_manager(manager_id):
    c.execute('''
        SELECT u.username, a.date, a.wijk, a.segments, a.note
        FROM activities a
        JOIN users u ON a.user_id = u.id
        WHERE u.manager_id=?
        ORDER BY a.date DESC
    ''', (manager_id,))
    return c.fetchall()

# -----------------------------
# Login page (only if not logged in)
# -----------------------------
if "role" not in st.session_state:
    st.title("🗞️ Delvero Payroll Login")

    with st.form("login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        user = check_login(username, password)
        if user:
            st.session_state['user_id'] = user[0]
            st.session_state['role'] = user[1]
            st.session_state['manager_id'] = user[2]
            st.session_state['username'] = username
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

# -----------------------------
# Manager dashboard with sidebar menu
# -----------------------------
if 'role' in st.session_state and st.session_state['role'] == 'manager':
    st.title(f"📊 Manager Dashboard ({st.session_state['username']})")

    # Sidebar menu
    with st.sidebar:
        st.header("⚙️ Settings Menu")
        choice = st.radio("Choose an option:", [
            "⬅️ Back to Dashboard",
            "👷 Manage Employees",
            "🗺️ Manage Wijk (coming soon)"
        ])

        st.divider()
        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.rerun()

    # Dashboard main content
    if choice == "⬅️ Back to Dashboard":
        st.subheader("📈 Employee Work Report")
        records = get_all_activities_for_manager(st.session_state['user_id'])
        if records:
            df = pd.DataFrame(records, columns=["Employee", "Date", "Wijk", "Segments", "Note"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No activities recorded yet.")

    elif choice == "👷 Manage Employees":
        st.subheader("➕ Add New Employee")
        with st.form("add_emp"):
            emp_username = st.text_input("Employee Username")
            emp_password = st.text_input("Password", type="password")
            add_btn = st.form_submit_button("Add Employee")
            if add_btn:
                success = add_user(emp_username, emp_password, "employee", st.session_state['user_id'])
                if success:
                    st.success(f"✅ Employee '{emp_username}' has been added.")
                else:
                    st.error("❌ This username already exists.")

        st.subheader("📋 Employee List")
        employees = get_employees_by_manager(st.session_state['user_id'])
        if employees:
            st.dataframe(pd.DataFrame(employees, columns=["ID", "Username"]), use_container_width=True)
        else:
            st.info("No employees found.")

    elif choice == "🗺️ Manage Wijk (coming soon)":
        st.info("📍 This section will allow adding Wijk regions with payment rates.")

# -----------------------------
# Employee dashboard
# -----------------------------
if 'role' in st.session_state and st.session_state['role'] == 'employee':
    st.title(f"👷 Employee Dashboard ({st.session_state['username']})")

    st.subheader("🗓️ Log Daily Activity")
    wijk = st.text_input("Wijk Name")
    segments = st.number_input("Number of Segments", min_value=0, value=0)
    note = st.text_area("Additional Notes (optional)")
    if st.button("Submit"):
        add_activity(st.session_state['user_id'], wijk, segments, note)
        st.success("✅ Activity recorded successfully!")

    st.subheader("📋 My Activity History")
    data = get_activities_by_user(st.session_state['user_id'])
    if data:
        df = pd.DataFrame(data, columns=["Date", "Wijk", "Segments", "Note"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No activities yet.")

    st.divider()
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

# -----------------------------
# Mobile-friendly styling
# -----------------------------
st.markdown("""
<style>
html, body, [class*="css"] {
    font-size: 16px !important;
}
.stButton>button {
    width: 100%;
    font-size: 18px;
    padding: 0.75em 0;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)
