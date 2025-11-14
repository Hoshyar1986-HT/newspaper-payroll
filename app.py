# ==========================================
# ZONE #1 — IMPORTS & INITIAL CONFIG
# ==========================================
import streamlit as st
import pandas as pd
import requests
import hashlib
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Delvero Payroll System",
    layout="wide",
    initial_sidebar_state="expanded"
)
# ==========================================
# ZONE #2 — SUPABASE CONFIG
# ==========================================
SUPABASE_URL = "https://qggrtnyfgvlrmoopjdte.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFnZ3J0bnlmZ3Zscm1vb3BqZHRlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMxMTYxMjQsImV4cCI6MjA3ODY5MjEyNH0.WCSXtc_l5aNndAOTagLW-LWQPePIWPlLNRkWx_MNacI"
# ==========================================
# ZONE #3 — DATABASE HELPER FUNCTIONS (REST API)
# ==========================================

def db_select(table, query=""):
    url = f"{SUPABASE_URL}/rest/v1/{table}{query}"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    try:
        return response.json()
    except:
        return None


def db_insert(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    response = requests.post(url, headers=headers, json=data)

    if response.status_code >= 300:
        st.error("Supabase Error:")
        st.write(response.text)
        return None

    try:
        return response.json()
    except:
        return {"status": "created"}


def db_delete(table, query=""):
    url = f"{SUPABASE_URL}/rest/v1/{table}{query}"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json"
    }
    response = requests.delete(url, headers=headers)
    return response.status_code == 204
# ==========================================
# ZONE #4 — PASSWORD HASHING + GET USER
# ==========================================

def hash_password(password: str):
    password = password.strip()
    return hashlib.sha256(password.encode()).hexdigest()


def check_password(input_pw, stored_hash):
    return hash_password(input_pw) == stored_hash


def get_user_by_username(username):
    users = db_select("employees", f"?username=eq.{username}")
    if users and len(users) > 0:
        return users[0]
    return None
# ==========================================
# ZONE #5 — GLOBAL CSS (Mobile UI + Clean Style)
# ==========================================

st.markdown("""
<style>

html, body, [class*="css"] {
    font-size: 16px !important;
}

.stButton > button {
    width: 100%;
    padding: 12px;
    font-size: 17px;
    border-radius: 10px;
}

[data-testid="stDataFrame"] div {
    scrollbar-width: thin;
}

.sidebar-title {
    font-size: 24px !important;
    font-weight: 700 !important;
    padding: 10px 0 20px 0;
}

.sticky-filter {
    position: sticky;
    top: 0;
    z-index: 50;
    background: #ffffff;
    padding: 8px;
    border-radius: 10px;
    border: 1px solid #eee;
}

</style>
""", unsafe_allow_html=True)
# ==========================================
# ZONE #6 — LOGIN SYSTEM (ADMIN / MANAGER / EMPLOYEE)
# ==========================================

# Initialize session keys
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None

if "username" not in st.session_state:
    st.session_state.username = None

if "menu" not in st.session_state:
    st.session_state.menu = None


def logout():
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None
    st.session_state.menu = None
    st.experimental_rerun()


# -------------------------------
# LOGIN SCREEN
# -------------------------------
if not st.session_state.logged_in:

    st.title("🔐 Delvero Login")

    username_input = st.text_input("Username")
    password_input = st.text_input("Password", type="password")

    login_btn = st.button("Login")

    if login_btn:
        user = get_user_by_username(username_input)

        if user and check_password(password_input, user["password"]):
            st.session_state.logged_in = True
            st.session_state.role = user["role"]
            st.session_state.username = user["username"]
            st.session_state.menu = "dashboard"
            st.experimental_rerun()

        else:
            st.error("❌ Invalid username or password")

    st.stop()   # Prevents loading rest of app before login
# ==========================================
# ZONE #7 — SIDEBAR (MENU BY ROLE)
# ==========================================

st.sidebar.markdown(
    "<div class='sidebar-title'>📋 Menu</div>",
    unsafe_allow_html=True
)

role = st.session_state.role
username = st.session_state.username

# Display user info
st.sidebar.write(f"👤 **User:** {username}")
st.sidebar.write(f"🔑 **Role:** {role.capitalize()}")

st.sidebar.markdown("---")

# Role-based menu
if role == "admin":
    menu_options = [
        "📊 Dashboard",
        "➕ Add Manager",
        "📋 List Managers",
        "🧑‍💼 Add Employee",
        "📋 Employee List",
        "⚙ System Settings"
    ]

elif role == "manager":
    menu_options = [
        "📊 Dashboard",
        "➕ Add Employee",
        "📋 My Employees"
    ]

elif role == "employee":
    menu_options = [
        "📊 Dashboard",
    +   "📝 Submit Work",
        "⚙ Profile"
    ]

else:
    menu_options = ["📊 Dashboard"]

# Sidebar Selection
menu = st.sidebar.radio("Navigation", menu_options)
st.session_state.menu = menu

st.sidebar.markdown("---")
st.sidebar.button("🚪 Logout", on_click=logout)
# ==========================================
# ZONE #8 — ADMIN DASHBOARD
# ==========================================

if role == "admin" and menu == "📊 Dashboard":
    st.title("📊 Admin Dashboard")
    st.write("Overview of all managers, employees, and payroll analytics will go here.")
# ==========================================
# ZONE #9 — MANAGER DASHBOARD
# ==========================================

if role == "manager" and menu == "📊 Dashboard":
    st.title("📊 Manager Dashboard")
    st.write("Here you will see your employees’ performance and payroll data.")
# ==========================================
# ZONE #10 — EMPLOYEE DASHBOARD
# ==========================================

if role == "employee" and menu == "📊 Dashboard":
    st.title("📊 Employee Dashboard")
    st.write("Submit work and see your recent activity here.")
# ============================
# ZONE 11 — ADD MANAGER (ADMIN ONLY)
# ============================

if role == "admin" and menu == "➕ Add Manager":

    st.title("➕ Add New Manager")

    if "manager_created" not in st.session_state:
        st.session_state.manager_created = False

    with st.form("form_add_manager"):
        firstname = st.text_input("First Name")
        lastname = st.text_input("Last Name")
        address = st.text_input("Address")
        username_new = st.text_input("Username")
        password_new = st.text_input("Password", type="password")
        submit_btn = st.form_submit_button("Create Manager")

    if submit_btn:
        if not firstname or not lastname or not username_new or not password_new:
            st.error("❌ All fields except Address are required.")

        else:
            hashed_pw = hash_password(password_new)
            db_insert("employees", {
                "firstname": firstname,
                "lastname": lastname,
                "address": address,
                "username": username_new,
                "password": hashed_pw,
                "role": "manager"
            })

            st.success(f"Manager {firstname} {lastname} created successfully!")
            st.session_state.manager_created = True

    if st.session_state.manager_created:
        st.session_state.manager_created = False
        st.session_state.menu = "📋 List Managers"
        st.experimental_rerun()
# ============================
# ZONE 12 — LIST MANAGERS
# ============================

if role == "admin" and menu == "📋 List Managers":

    st.title("📋 All Managers")

    managers = db_select("employees", "?role=eq.manager")

    if not managers:
        st.info("No managers found.")
    else:
        df = pd.DataFrame(managers)[["firstname", "lastname", "username"]]
        st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("🗑 Delete Manager")

    if "delete_manager_flag" not in st.session_state:
        st.session_state.delete_manager_flag = False

    if managers:
        usernames = [m["username"] for m in managers]
        selected = st.selectbox("Select Manager", usernames)
        delete_btn = st.button("Delete Manager")

        if delete_btn:
            db_delete("employees", f"?username=eq.{selected}")
            st.success(f"Manager '{selected}' deleted.")
            st.session_state.delete_manager_flag = True

    if st.session_state.delete_manager_flag:
        st.session_state.delete_manager_flag = False
        st.experimental_rerun()
# ============================
# ZONE 13 — ADD EMPLOYEE
# ============================

if menu == "➕ Add Employee" and role in ["admin", "manager"]:

    st.title("➕ Add Employee")

    if "employee_created" not in st.session_state:
        st.session_state.employee_created = False

    with st.form("form_add_employee"):
        firstname = st.text_input("First Name")
        lastname = st.text_input("Last Name")
        address = st.text_input("Address")
        username_new = st.text_input("Username")
        password_new = st.text_input("Password", type="password")
        submit_btn = st.form_submit_button("Create Employee")

    if submit_btn:
        if not firstname or not lastname or not username_new or not password_new:
            st.error("❌ All fields except Address are required.")

        else:
            hashed_pw = hash_password(password_new)
            db_insert("employees", {
                "firstname": firstname,
                "lastname": lastname,
                "address": address,
                "username": username_new,
                "password": hashed_pw,
                "role": "employee"
            })

            st.success(f"Employee {firstname} {lastname} created successfully!")
            st.session_state.employee_created = True

    if st.session_state.employee_created:
        st.session_state.employee_created = False
        st.session_state.menu = "📋 Employee List"
        st.experimental_rerun()
# ============================
# ZONE 14 — LIST EMPLOYEES
# ============================

if menu == "📋 Employee List" and role in ["admin", "manager"]:

    st.title("📋 Employee List")

    employees = db_select("employees", "?role=eq.employee")

    if not employees:
        st.info("No employees found.")
    else:
        df = pd.DataFrame(employees)[["firstname", "lastname", "username"]]
        st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("🗑 Delete Employee")

    if "delete_employee_flag" not in st.session_state:
        st.session_state.delete_employee_flag = False

    if employees:
        usernames = [u["username"] for u in employees]
        selected = st.selectbox("Select Employee", usernames)
        delete_btn = st.button("Delete Employee")

        if delete_btn:
            db_delete("employees", f"?username=eq.{selected}")
            st.success(f"Employee '{selected}' deleted.")
            st.session_state.delete_employee_flag = True

    if st.session_state.delete_employee_flag:
        st.session_state.delete_employee_flag = False
        st.experimental_rerun()
# ============================
# ZONE 15 — EMPLOYEE: SUBMIT WORK
# ============================

if role == "employee" and menu == "📝 Submit Work":

    st.title("📝 Submit Daily Work")

    if "work_submitted" not in st.session_state:
        st.session_state.work_submitted = False

    with st.form("submit_work_form"):
        work_date = st.date_input("Date")
        wijk_name = st.text_input("Wijk Name (e.g. Chaam1)")
        segments  = st.number_input("Segments", min_value=1, max_value=10)
        trip_km   = st.number_input("Trip KM", min_value=0, max_value=400)
        submit_btn = st.form_submit_button("Submit Work")

    if submit_btn:
        db_insert("work_logs", {
            "username": st.session_state.username,
            "date": str(work_date),
            "wijk": wijk_name,
            "segments": segments,
            "trip_km": trip_km
        })

        st.success("Work submitted successfully!")
        st.session_state.work_submitted = True

    if st.session_state.work_submitted:
        st.session_state.work_submitted = False
        st.experimental_rerun()
# ==========================================
# ZONE #16 — LOAD PAYROLL DATA (FINAL + FIXED)
# ==========================================

def load_payroll(username_filter=None, start_date=None, end_date=None):

    # Build query
    query = "?select=username,date,wijk,segments,trip_km"

    if username_filter:
        query += f"&username=eq.{username_filter}"

    if start_date:
        query += f"&date=gte.{start_date}"

    if end_date:
        query += f"&date=lte.{end_date}"

    # Fetch data from Supabase
    logs = db_select("work_logs", query)

    # ---- SAFETY CHECK (very important) ----
    # Supabase may return: None, [], or [{}]
    if not logs or logs == [{}]:
        return pd.DataFrame()

    # Convert to DataFrame
    df = pd.DataFrame(logs)

    # Ensure required columns exist
    required_cols = ["username", "date", "wijk", "segments", "trip_km"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = None

    # Convert date to weekday
    df["Day"] = pd.to_datetime(df["date"]).dt.day_name()

    # ---- Wijk Price Based on Segments ----
    def wijk_price(seg):
        if seg == 2: return 650
        if seg == 3: return 750
        if seg == 4: return 850
        # fallback if someone enters 1 or >4
        return 500 + 100 * int(seg)

    df["Wijk Price (€)"] = df["segments"].astype(float).apply(wijk_price)

    # ---- Trip Cost ----
    df["Trip Cost (€)"] = df["trip_km"].astype(float) * 0.16

    # ---- Daily Earnings ----
    df["Wijk Earn (€)"] = df["Wijk Price (€)"] / 26
    df["Day Earn (€)"]  = df["Wijk Earn (€)"] + df["Trip Cost (€)"]

    return df
# ==========================================
# ZONE #17 — PAYROLL DASHBOARD (ADMIN + MANAGER)
# ==========================================

if menu == "📊 Dashboard" and role in ["admin", "manager"]:

    st.title("📊 Payroll Dashboard")

    # ---- Filters ----
    employees = db_select("employees", "?role=eq.employee")
    employee_names = ["All"] + [e["username"] for e in employees]

    selected_user = st.selectbox("Select Employee", employee_names)
    start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
    end_date   = st.date_input("End Date", datetime.now())

    # ---- Load Data ----
    df = load_payroll(
        None if selected_user == "All" else selected_user,
        start_date,
        end_date
    )

    if df.empty:
        st.info("No payroll data found for this date range.")
        st.stop()

    payroll_df = df[[
        "date", "Day", "username", "wijk", "segments",
        "Wijk Price (€)", "trip_km", "Trip Cost (€)",
        "Wijk Earn (€)", "Day Earn (€)"
    ]]

    # ---- Coloring ----
    styled_df = payroll_df.style.apply(color_rows, axis=1)
    st.dataframe(styled_df, use_container_width=True)

    st.markdown("---")
# ==========================================
# ZONE #18 — SUMMARY BOX
# ==========================================

    total_earn       = payroll_df["Day Earn (€)"].sum()
    total_segments   = payroll_df["segments"].sum()
    total_trip_km    = payroll_df["trip_km"].sum()
    total_trip_cost  = payroll_df["Trip Cost (€)"].sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Earn (€)", f"€ {total_earn:,.2f}")
    col2.metric("Total Segments", total_segments)
    col3.metric("Total Trip (KM)", total_trip_km)
    col4.metric("Total Trip Cost (€)", f"€ {total_trip_cost:,.2f}")
# ==========================================
# ZONE #19 — TABLE COLORING RULES
# ==========================================

def color_rows(row):

    # Sunday → RED
    if row["Day"] == "Sunday":
        return ["background-color: #ffcccc"] * len(row)

    # OFF DAY → No wijk or 0 segments
    if (row["wijk"] == "") or (row["segments"] == 0):
        return ["background-color: #ffe5cc"] * len(row)

    # Normal day → white
    return ["background-color: white"] * len(row)
# ==========================================
# ZONE #20 — FOOTER
# ==========================================

st.markdown("""
<br><br>
<center style='color:gray; font-size:13px;'>
Delvero Payroll System — Powered by Streamlit & Supabase
</center>
""", unsafe_allow_html=True)
