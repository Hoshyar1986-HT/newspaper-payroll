# ==========================================
# ZONE 1 — IMPORTS & INITIAL CONFIG
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
# ZONE 2 — SUPABASE CONFIG
# ==========================================
SUPABASE_URL = "https://qggrtnyfgvlrmoopjdte.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFnZ3J0bnlmZ3Zscm1vb3BqZHRlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMxMTYxMjQsImV4cCI6MjA3ODY5MjEyNH0.WCSXtc_l5aNndAOTagLW-LWQPePIWPlLNRkWx_MNacI"
# ==========================================
# ZONE 3 — DATABASE HELPER FUNCTIONS
# ==========================================
def db_select(table, query=""):
    url = f"{SUPABASE_URL}/rest/v1/{table}{query}"
    headers = {"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}
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
        st.error("Supabase Insert Error:")
        st.write(response.text)
        return None
    try:
        return response.json()
    except:
        return {"status": "created"}

def db_update(table, query, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}{query}"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code >= 300:
        st.error("Supabase Update Error:")
        st.write(response.text)
        return None
    return response.json()

def db_delete(table, query):
    url = f"{SUPABASE_URL}/rest/v1/{table}{query}"
    headers = {"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"}
    response = requests.delete(url, headers=headers)
    return response.status_code in [200, 204]
# ==========================================
# ZONE 4 — AUTHENTICATION HELPERS
# ==========================================
def hash_password(password):
    return hashlib.sha256(password.strip().encode()).hexdigest()

def check_password(input_pw, stored_hash):
    return hash_password(input_pw) == stored_hash

def get_user_by_username(username):
    users = db_select("employees", f"?username=eq.{username}")
    if users and isinstance(users, list) and len(users) > 0:
        return users[0]
    return None
# ==========================================
# ZONE 5 — GLOBAL CSS
# ==========================================
st.markdown("""
<style>
html, body, [class*="css"] { font-size: 16px !important; }
.stButton > button { width: 100%; padding: 12px; font-size: 17px; border-radius: 10px; }
.sidebar-title { font-size: 24px !important; font-weight: 700 !important; padding: 10px 0 20px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<script>
window.addEventListener('message', (event) => {
    if (event.data.event === 'open_payroll') {
        const newUrl = window.location.href.split('?')[0] + '?payroll=' + event.data.user;
        window.location.href = newUrl;
    }
});
</script>
""", unsafe_allow_html=True)

# ==========================================
# ZONE 6 — NEW MOBILE-FRIENDLY LOGIN SCREEN
# ==========================================

# Session init
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None

# Modern CSS for responsive centered login form
st.markdown("""
<style>

body {
    background: #f7f8fc !important;
}

.login-container {
    max-width: 420px;
    margin: auto;
    margin-top: 7vh;
    background: white;
    padding: 35px 30px;
    border-radius: 18px;
    box-shadow: 0px 8px 22px rgba(0,0,0,0.08);
}

.login-title {
    text-align: center;
    font-size: 32px;
    font-weight: 800;
    margin-bottom: 25px;
}

@media (max-width: 600px) {
    .login-container {
        margin-top: 3vh;
        padding: 28px 22px;
        border-radius: 16px;
    }
    .login-title {
        font-size: 26px;
    }
}

/* Make input fields modern */
.login-form .stTextInput>div>div>input {
    padding: 14px;
    border-radius: 10px;
    font-size: 16px;
}

/* Login button */
.stButton>button {
    width: 100%;
    background: #3F51B5;
    color: white;
    padding: 14px 0px;
    font-size: 18px;
    border-radius: 12px;
    border: none;
    margin-top: 15px;
}

.stButton>button:hover {
    background: #303f9f;
}

</style>
""", unsafe_allow_html=True)


def do_login():
    username = st.session_state.login_user
    password = st.session_state.login_pass

    user = get_user_by_username(username)

    if user and check_password(password, user["password"]):
        st.session_state.logged_in = True
        st.session_state.username = user["username"]
        st.session_state.role = user["role"]
    else:
        st.session_state.login_error = "❌ Invalid username or password"

# If not logged in → show login screen
if not st.session_state.logged_in:

    st.markdown("<div class='login-container'>", unsafe_allow_html=True)

    st.markdown(
        "<h2 class='login-title'>🔐 Delvero Login</h2>",
        unsafe_allow_html=True
    )

    # Modern login form
    with st.container():
        st.text_input("Username", key="login_user")
        st.text_input("Password", type="password", key="login_pass")

        if "login_error" in st.session_state:
            st.error(st.session_state.login_error)

        st.button("Login", on_click=do_login)

    st.markdown("</div>", unsafe_allow_html=True)

    st.stop()
def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None

# ==========================================
# ZONE 7 — SIDEBAR & NAVIGATION (FINAL FIX)
# ==========================================

# redirect flag
if "redirecting" not in st.session_state:
    st.session_state.redirecting = False

role = st.session_state.role
username = st.session_state.username

st.sidebar.markdown("<div class='sidebar-title'>📋 Menu</div>", unsafe_allow_html=True)
st.sidebar.write(f"👤 **{username}**")
st.sidebar.write(f"🔑 **{role.capitalize()}**")
st.sidebar.markdown("---")

# Role-based menu
if role == "admin":
    menu_options = [
        "📊 Admin Dashboard",
        "➕ Add Manager",
        "📋 Managers",
        "🧑‍💼 Add Employee",
        "👥 Employees",
        "🗂 Wijk Management",
        "📊 Payroll",
        "⚙ Settings",
    ]

elif role == "manager":
    menu_options = [
        "📊 Manager Dashboard",
        "🧑‍💼 Add Employee",
        "🗂 Wijk Management",
        "📝 Approvals",
        "📊 Payroll"
    ]

elif role == "employee":
    menu_options = [
        "📊 Employee Dashboard",
        "📝 Submit Work",
        "📋 My Work",
        "💰 My Earnings",
        "👤 Profile"
    ]

else:
    st.error("Role not recognized.")
    st.stop()

selected_menu = st.sidebar.radio("Navigation", menu_options)

# 🔥 FINAL LOGIC
if st.session_state.redirecting:
    # redirect happened → do NOT override
    menu = st.session_state.menu
else:
    # user clicked in sidebar → update menu
    st.session_state.menu = selected_menu
    menu = selected_menu

# logout button
st.sidebar.markdown("---")
st.sidebar.button("🚪 Logout", on_click=logout)
# ==========================================
# ZONE 8 — ADMIN DASHBOARD
# ==========================================
if role == "admin" and menu == "📊 Admin Dashboard":
    st.title("📊 Admin Dashboard")

    managers = db_select("employees", "?role=eq.manager") or []
    employees = db_select("employees", "?role=eq.employee") or []
    wijks = db_select("wijk") or []
    pending_logs = db_select("work_logs", "?status=eq.pending") or []

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Managers", len(managers))
    col2.metric("Employees", len(employees))
    col3.metric("Wijks", len(wijks))
    col4.metric("Pending Approvals", len(pending_logs))

    st.markdown("### System Overview")
    st.info("A full analytics dashboard will be added in version 1.2.0.")
# ==========================================
# ZONE 9 — MANAGER DASHBOARD (UPDATED — CLICKABLE EMPLOYEES)
# ==========================================

if role == "manager" and menu == "📊 Manager Dashboard":
    st.title("📊 Manager Dashboard")

    my_emps = db_select("employees", f"?manager_username=eq.{username}") or []
    pending_logs = db_select("work_logs", f"?manager_username=eq.{username}&status=eq.pending") or []
    approved_logs = db_select("work_logs", f"?manager_username=eq.{username}&status=eq.approved") or []

    col1, col2, col3 = st.columns(3)
    col1.metric("My Employees", len(my_emps))
    col2.metric("Pending Approvals", len(pending_logs))
    col3.metric("Approved Logs", len(approved_logs))

    st.markdown("### 👥 My Team")

    if not my_emps:
        st.info("You don't have employees yet.")
        st.stop()

    # تبدیل لیست به DataFrame
    df = pd.DataFrame(my_emps)[["firstname", "lastname", "username"]]
    df["Full Name"] = df["firstname"] + " " + df["lastname"]
    df = df[["Full Name", "username"]]

    # نمایش لینک به جای سطر کلیک‌پذیر
    st.markdown("#### Click on an employee to open Payroll")

    for idx, row in df.iterrows():
        full = row["Full Name"]
        user = row["username"]

        # لینک ساخته می‌شود → روی آن کلیک = رفتن به Payroll
        link = f"""
        <a href="#" onclick="window.parent.postMessage({{'event':'open_payroll','user':'{user}'}}, '*')" 
           style="font-size:18px; display:block; padding:8px 4px;">
           👤 {full}
        </a>
        """
        st.markdown(link, unsafe_allow_html=True)

    # دریافت پیام کلیک
    clicked_user = st.experimental_get_query_params().get("open_payroll", None)

# ==========================================
# ZONE 10 — ADD MANAGER (ADMIN) — FINAL NON-RERUN VERSION
# ==========================================

if role == "admin" and menu == "➕ Add Manager":

    st.title("➕ Add New Manager")

    if "manager_created" not in st.session_state:
        st.session_state.manager_created = False

    if st.session_state.manager_created:
        st.success("Manager created successfully!")
        st.header("📋 Managers")

        managers = db_select("employees", "?role=eq.manager")

        if managers:
            df = pd.DataFrame(managers)[["firstname", "lastname", "username"]]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No managers found.")
        st.stop()

    with st.form("form_add_manager"):
        fn = st.text_input("First Name")
        ln = st.text_input("Last Name")
        addr = st.text_input("Address")
        uname = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        submit = st.form_submit_button("Create Manager")

    if submit:
        if not fn or not ln or not uname or not pw:
            st.error("❌ All fields are required.")
            st.stop()

        hashed = hash_password(pw)
        result = db_insert("employees", {
            "firstname": fn,
            "lastname": ln,
            "address": addr,
            "username": uname,
            "password": hashed,
            "role": "manager"
        })

        if result is None:
            st.error("❌ Failed to create manager.")
            st.stop()

        st.session_state.manager_created = True
        st.success(f"Manager '{uname}' created successfully!")
        st.stop()
# ==========================================
# ZONE 11 — MANAGERS LIST (VIEW / DELETE / EDIT)
# ==========================================
if role == "admin" and menu == "📋 Managers":

    st.title("📋 All Managers")

    managers = db_select("employees", "?role=eq.manager") or []

    if not managers:
        st.info("No managers found.")
    else:
        df = pd.DataFrame(managers)[["firstname", "lastname", "username", "address"]]
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("🗑 Delete Manager")

        usernames = [m["username"] for m in managers]
        selected = st.selectbox("Select Manager", usernames)
        delete_btn = st.button("Delete Manager")

        if delete_btn:
            db_delete("employees", f"?username=eq.{selected}")
            st.success(f"Manager '{selected}' deleted.")
            st.stop()
# ==========================================
# ZONE 12 — ADD EMPLOYEE (ADMIN & MANAGER)
# ==========================================
if menu == "🧑‍💼 Add Employee" and role in ["admin", "manager"]:

    st.title("🧑‍💼 Add New Employee")

    # --------------- Manager selection ---------------
    if role == "admin":
        managers = db_select("employees", "?role=eq.manager") or []
        manager_usernames = [m["username"] for m in managers]
        selected_manager = st.selectbox("Assign Employee To Manager", manager_usernames)
    else:
        selected_manager = username  # manager assigns to themselves

    # --------------- Employee Form ---------------
    with st.form("form_add_employee"):
        fn = st.text_input("First Name")
        ln = st.text_input("Last Name")
        addr = st.text_input("Address")
        uname = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        submit = st.form_submit_button("Create Employee")

    if submit:
        if not fn or not ln or not uname or not pw:
            st.error("❌ Required fields missing.")
        else:
            hashed = hash_password(pw)
            db_insert("employees", {
                "firstname": fn,
                "lastname": ln,
                "address": addr,
                "username": uname,
                "password": hashed,
                "role": "employee",
                "manager_username": selected_manager
            })
            st.success(f"Employee '{uname}' created under manager '{selected_manager}'.")
            st.stop()
# ==========================================
# ZONE 13 — EMPLOYEE LIST (ADMIN + MANAGER)
# ==========================================

if menu == "👥 Employees" and role in ["admin", "manager"]:

    st.title("👥 Employee List")

    if role == "admin":
        employees = db_select("employees", "?role=eq.employee") or []
    else:
        employees = db_select("employees", f"?role=eq.employee&manager_username=eq.{username}") or []

    if not employees:
        st.info("No employees found.")
    else:
        df = pd.DataFrame(employees)[["firstname", "lastname", "username", "manager_username"]]
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("🗑 Delete Employee")

        usernames = [e["username"] for e in employees]
        selected = st.selectbox("Select Employee", usernames)
        delete_btn = st.button("Delete Employee")

        if delete_btn:
            db_delete("employees", f"?username=eq.{selected}")
            st.success(f"Employee '{selected}' deleted.")
            st.stop()
# ==========================================
# ZONE 14 — WIJK MANAGEMENT (ADMIN + MANAGER)
# ==========================================

if menu == "🗂 Wijk Management" and role in ["admin", "manager"]:

    st.title("🗂 Wijk Management")

    with st.form("add_wijk_form"):
        wijk_name = st.text_input("Wijk Name")
        depot = st.text_input("Depot")
        segments = st.number_input("Segments", min_value=1, max_value=10)
        base_price = st.number_input("Base Price (€)", min_value=0.0)
        submit = st.form_submit_button("Create Wijk")

    if submit:
        db_insert("wijk", {
            "wijk_name": wijk_name,
            "depot": depot,
            "segments": segments,
            "base_price": base_price,
            "created_by": username
        })
        st.success("Wijk added successfully!")
        st.stop()

    st.markdown("---")
    st.subheader("📋 Existing Wijks")

    wijks = db_select("wijk") or []
    if wijks:
        df = pd.DataFrame(wijks)[["wijk_name", "depot", "segments", "base_price", "created_by"]]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No wijks created yet.")
# ==========================================
# ZONE 15 — EMPLOYEE: SUBMIT WORK
# ==========================================

if role == "employee" and menu == "📝 Submit Work":

    st.title("📝 Submit Daily Work")

    today = datetime.today().date()
    wijks_data = db_select("wijk") or []
    wijk_names = sorted([w["wijk_name"] for w in wijks_data]) if wijks_data else []

    with st.form("submit_work_form"):
        work_date = st.date_input("Date", value=today)
        st.markdown("#### Enter Wijk(s) You Delivered Today")
        wijk_inputs = []
        for i in range(3):
            wijk_col = st.text_input(f"Wijk #{i+1}", key=f"wijk_input_{i}")
            depot_col = st.text_input(f"Depot for Wijk #{i+1}", key=f"depot_input_{i}")
            wijk_inputs.append((wijk_col.strip(), depot_col.strip()))

        trip_km = st.number_input("Total Trip KM", min_value=0, max_value=300)
        notes = st.text_area("Notes (optional)")
        submit = st.form_submit_button("Submit Work")

    if submit:
        emp = db_select("employees", f"?username=eq.{username}")
        if emp and isinstance(emp, list) and len(emp) > 0:
            manager_username = emp[0].get("manager_username")
        else:
            st.error("Manager not found for this user.")
            st.stop()

        success = False
        for wijk_name, depot in wijk_inputs:
            if not wijk_name:
                continue
            matched = next((w for w in wijks_data if w["wijk_name"] == wijk_name), None)
            final_depot = matched["depot"] if matched else depot

            db_insert("work_logs", {
                "employee_username": username,
                "manager_username": manager_username,
                "date": str(work_date),
                "wijk_name": wijk_name,
                "depot": final_depot,
                "trip_km": trip_km,
                "segments": None,
                "status": "pending",
                "price_final": None,
                "earn_final": None,
                "notes": notes,
                "created_at": datetime.now().isoformat()
            })
            success = True

        if success:
            st.success("✅ Work log(s) submitted successfully!")
            st.experimental_rerun()
        else:
            st.warning("⚠ No wijk entries provided.")
# ==========================================
# ZONE 16 — LOAD PAYROLL DATA
# ==========================================

def load_payroll(username_filter=None, manager_filter=None, start_date=None, end_date=None):
    query = "?select=username,date,trip_km,wijk,status,segments,manager_username"
    if username_filter:
        query += f"&username=eq.{username_filter}"
    if manager_filter:
        query += f"&manager_username=eq.{manager_filter}"
    if start_date:
        query += f"&date=gte.{start_date}"
    if end_date:
        query += f"&date=lte.{end_date}"
    logs = db_select("work_logs", query)
    if not logs or logs == [{}]:
        return pd.DataFrame()
    if isinstance(logs, dict):
        logs = [logs]
    logs = [x for x in logs if isinstance(x, dict) and x]
    if not logs:
        return pd.DataFrame()
    df = pd.DataFrame(logs)
    required = ["username", "date", "wijk", "segments", "trip_km", "status", "manager_username"]
    for c in required:
        if c not in df.columns:
            df[c] = None
    df["date"] = pd.to_datetime(df["date"])
    df["Day"] = df["date"].dt.day_name()
    df["segments"] = pd.to_numeric(df["segments"], errors="coerce").fillna(0)
    df["trip_km"] = pd.to_numeric(df["trip_km"], errors="coerce").fillna(0)
    wijk_table = db_select("wijk") or []
    wijk_price_map = {w["wijk_name"]: w.get("base_price", 0) for w in wijk_table}
    def compute_price(wijk_name, segments):
        if wijk_name in wijk_price_map:
            return wijk_price_map[wijk_name]
        if segments == 2: return 650
        if segments == 3: return 750
        if segments == 4: return 850
        return 500 + 100 * segments
    df["Wijk Price (€)"] = df.apply(lambda r: compute_price(r["wijk"], r["segments"]), axis=1)
    df["Trip Cost (€)"] = df["trip_km"] * 0.16
    df["Wijk Earn (€)"] = df["Wijk Price (€)"] / 26
    df["Day Earn (€)"] = df["Wijk Earn (€)"] + df["Trip Cost (€)"]
    return df
# ==========================================
# ZONE 17 — MANAGER APPROVALS
# ==========================================

if role == "manager" and menu == "📝 Approvals":
    st.title("📝 Approvals — Pending Work Logs")
    pending = db_select("work_logs", f"?manager_username=eq.{username}&status=eq.pending") or []
    if not pending:
        st.info("No pending approvals.")
        st.stop()
    df = pd.DataFrame(pending)[["username", "date", "wijk", "trip_km", "segments"]]
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown("---")
    st.subheader("Select a log to approve:")
    options = [f"{p['username']} — {p['date']} — {p['wijk']}" for p in pending]
    selected = st.selectbox("Pending Logs", options)
    approve_btn = st.button("Approve")
    reject_btn = st.button("Reject")
    chosen = pending[options.index(selected)]
    if approve_btn:
        db_update("work_logs", f"?id=eq.{chosen['id']}", {"status": "approved"})
        st.success("Approved!")
        st.stop()
    if reject_btn:
        db_update("work_logs", f"?id=eq.{chosen['id']}", {"status": "rejected"})
        st.warning("Rejected.")
        st.stop()
# ==========================================
# ZONE 18 — PAYROLL DASHBOARD (UPDATED FULL VERSION)
# ==========================================

if menu == "📊 Payroll" and role in ["admin", "manager"]:
    st.title("📊 Payroll Dashboard")

    # Load employees based on role
    if role == "admin":
        emps = db_select("employees", "?role=eq.employee") or []
    else:
        emps = db_select("employees", f"?role=eq.employee&manager_username=eq.{username}") or []

    emp_list = ["All"] + [e["username"] for e in emps]

    # NEW: Check if redirected from Manager Dashboard
    params = st.experimental_get_query_params()

    if "payroll" in params:
        selected_user = params["payroll"][0]
    else:
        selected_user = "All"  # default (no selectbox)

    # Date filters
    start_date = st.date_input("📅 Start Date", datetime.now() - timedelta(days=30))
    end_date   = st.date_input("📅 End Date", datetime.now())

    # Load filtered payroll data
    df = load_payroll(
        username_filter=None if selected_user == "All" else selected_user,
        manager_filter=None if role == "admin" else username,
        start_date=start_date,
        end_date=end_date
    )

    if df.empty:
        st.info("No data available for this selection.")
        st.stop()

    # Clean display
    view_df = df[[
        "date", "Day", "username", "wijk",
        "segments", "trip_km", "Wijk Price (€)",
        "Trip Cost (€)", "Wijk Earn (€)", "Day Earn (€)", "status"
    ]]

    st.dataframe(view_df, use_container_width=True)

    st.markdown("---")
    st.subheader("Summary")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Earn (€)", f"€ {view_df['Day Earn (€)'].sum():,.2f}")
    col2.metric("Total Segments", view_df["segments"].sum())
    col3.metric("Total KM", view_df["trip_km"].sum())
    col4.metric("Total Trip Cost (€)", f"€ {view_df['Trip Cost (€)'].sum():,.2f}")

# ==========================================
# ZONE 19 — EMPLOYEE EARNINGS
# ==========================================
if role == "employee" and menu == "💰 My Earnings":

    st.title("💰 My Earnings")

    df = load_payroll(
        username_filter=username,
        start_date=datetime.now().replace(day=1),
        end_date=datetime.now()
    )

    if df.empty:
        st.info("No earnings yet.")
        st.stop()

    st.dataframe(df[[
        "date", "Day", "wijk", "segments",
        "Wijk Earn (€)", "Trip Cost (€)", "Day Earn (€)", "status"
    ]], use_container_width=True)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Earn (€)", f"€ {df['Day Earn (€)'].sum():,.2f}")
    col2.metric("Total KM", df["trip_km"].sum())
    col3.metric("Approved Days", len(df[df["status"] == "approved"]))


# ==========================================
# ZONE 20 — FOOTER
# ==========================================
st.markdown("""
<br><br>
<center style='color:gray; font-size:13px;'>
Delvero Payroll System — Version 1.1.0 — Powered by Streamlit & Supabase
</center>
""", unsafe_allow_html=True)
