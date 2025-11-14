# ============================================================
# === 1. IMPORTS & PAGE SETUP ================================
# ============================================================

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import requests, json, hashlib


st.set_page_config(
    page_title="Delvero Payroll System",
    page_icon="🗞️",
    layout="wide"
)


# ============================================================
# === 2. SUPABASE CONFIG (REST API) ==========================
# ============================================================

SUPABASE_URL = "https://qggrtnyfgvlrmoopjdte.supabase.co"
SUPABASE_ANON_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFnZ3J0bnlmZ3Zscm1vb3BqZHRlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMxMTYxMjQsImV4cCI6MjA3ODY5MjEyNH0."
    "WCSXtc_l5aNndAOTagLW-LWQPePIWPlLNRkWx_MNacI"
)

SUPABASE_HEADERS = {
    "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type": "application/json",
}



# ============================================================
# === 3. DATABASE FUNCTIONS (REST API) =======================
# ============================================================

def db_insert(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    response = requests.post(url, headers=SUPABASE_HEADERS, data=json.dumps(data))
    return response.json()

def db_select(table, filters=""):
    url = f"{SUPABASE_URL}/rest/v1/{table}{filters}"
    response = requests.get(url, headers=SUPABASE_HEADERS)
    return response.json()

def db_delete(table, filter_query):
    url = f"{SUPABASE_URL}/rest/v1/{table}{filter_query}"
    response = requests.delete(url, headers=SUPABASE_HEADERS)
    return response.json()


# ============================================================
# === 4. AUTH HELPERS ========================================
# ============================================================

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(input_pw, stored_hash):
    return hash_password(input_pw) == stored_hash

def get_user_by_username(username):
    result = db_select("employees", f"?username=eq.{username}")
    return result[0] if result else None


# ============================================================
# === 5. LOGIN PAGE ==========================================
# ============================================================


if "logged_in" not in st.session_state:

    st.title("🗞️ Delvero Payroll Login")

    with st.form("login_form"):
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")

    if login_btn:

        user = get_user_by_username(username_input)

        if user and check_password(password_input, user["password"]):
            st.session_state.logged_in = True
            st.session_state.username = user["username"]
            st.session_state.role = user["role"]
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

    st.stop()



# ============================================================
# === 6. SIDEBAR MENU ========================================
# ============================================================

role = st.session_state.role
user = st.session_state.username

with st.sidebar:
    st.header(f"👋 Welcome, {user}")
    st.markdown("---")

    # ADMIN
    if role == "admin":
        menu = st.radio("Menu", [
            "🏠 Admin Dashboard",
            "➕ Add Manager",
            "📋 List Managers",
            "👥 Manager Tools",
            "📊 View All Payroll",
            "⚙ System Settings"
        ])

    # MANAGER
    elif role == "manager":
        menu = st.radio("Menu", [
            "📊 Dashboard",
            "➕ Add Employee",
            "📋 My Employees",
            "⚙ Settings"
        ])

    # EMPLOYEE
    else:
        menu = st.radio("Menu", [
            "📋 My Work",
            "📝 Submit Day Work",
            "⚙ Profile"
        ])

    st.markdown("---")

    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()
# ============================================================
# === 7. PAYROLL DATA GENERATOR (SIMULATION FOR NOW) =========
# ============================================================

def generate_payroll_data(start_date, end_date, selected_employee="All"):
    """Temporary simulation before real employee work logs are implemented."""

    date_list = pd.date_range(start=start_date, end=end_date)
    records = []

    # Segment counts
    wijk_segments = {
        "Chaam1": 3, "Chaam4": 4, "Galder1": 2,
        "Lexmond2": 3, "Rotterdam1": 3, "Rotterdam2": 3
    }

    wijk_prices = {2: 650, 3: 750, 4: 850}

    trip_km = {"Hossein": 120, "Hoshyar": 45, "Masoud": 60}

    for date in date_list:
        weekday = date.strftime("%A")

        if weekday == "Sunday":  
            employees = ["Hossein", "Hoshyar", "Masoud"]
            for emp in employees:
                if selected_employee != "All" and emp != selected_employee:
                    continue

                records.append({
                    "Date": date.date(),
                    "Day": weekday,
                    "Employee": emp,
                    "On/Off": "Off",
                    "Wijk(s) name": "-",
                    "Wijk Volume/Segment": "-",
                    "Wijk Price (€)": "-",
                    "Trip (KM)": "-",
                    "Trip Cost (€)": "-",
                    "Day Earn (€)": "-"
                })
            continue

        for emp in ["Hossein", "Hoshyar", "Masoud"]:

            if selected_employee != "All" and emp != selected_employee:
                continue

            wijks = []
            onoff = "On"

            # Hossein rules
            if emp == "Hossein":
                if date.day == 12:
                    wijks = []
                    onoff = "Off"
                else:
                    wijks = ["Chaam1", "Chaam4", "Galder1"]

            # Hoshyar rules
            elif emp == "Hoshyar":
                if date.day == 12:
                    wijks = ["Chaam1", "Chaam4", "Galder1"]
                elif date.day == 13:
                    wijks = ["Lexmond2"]
                else:
                    wijks = []
                    onoff = "Off"

            # Masoud always works except Sunday
            elif emp == "Masoud":
                wijks = ["Rotterdam1", "Rotterdam2"]

            if len(wijks) == 0:
                onoff = "Off"

            # segments
            segments = sum(wijk_segments.get(w, 3) for w in wijks) if wijks else 0

            # price per wijk
            total_price = 0
            for w in wijks:
                seg = wijk_segments.get(w, 3)
                total_price += wijk_prices.get(seg, 750)

            km = trip_km.get(emp, 0) if onoff == "On" else 0
            trip_cost = km * 0.16
            wijk_earn = total_price / 26 if onoff == "On" else 0
            day_earn = wijk_earn + trip_cost if onoff == "On" else 0

            records.append({
                "Date": date.date(),
                "Day": weekday,
                "Employee": emp,
                "On/Off": onoff,
                "Wijk(s) name": ", ".join(wijks) if wijks else "-",
                "Wijk Volume/Segment": segments if segments else "-",
                "Wijk Price (€)": total_price if total_price else "-",
                "Trip (KM)": km if km else "-",
                "Trip Cost (€)": f"€ {trip_cost:.2f}" if km else "-",
                "Day Earn (€)": f"€ {day_earn:.2f}" if day_earn else "-"
            })

    return pd.DataFrame(records)



# ============================================================
# === 8. TABLE COLORING ======================================
# ============================================================

def apply_table_colors(df):
    """Color Sundays red, Off days orange."""
    def color_row(row):
        if row["Day"] == "Sunday":
            return ["background-color:#ffcccc"] * len(row)
        if row["On/Off"] == "Off":
            return ["background-color:#ffe6cc"] * len(row)
        return [""] * len(row)
    return df.style.apply(color_row, axis=1)



# ============================================================
# === 9. MANAGER DASHBOARD (PAYROLL TABLE) ===================
# ============================================================

if role == "manager" and menu == "📊 Dashboard":

    st.title("📊 Payroll Dashboard")

    employees_list = ["All", "Hossein", "Hoshyar", "Masoud"]
    selected_emp = st.selectbox("Select Employee", employees_list)

    start_date = datetime(2025, 11, 1)
    end_date = datetime(2025, 11, 30)

    start, end = st.date_input(
        "Select Date Range", (start_date, end_date)
    )

    df = generate_payroll_data(start, end, selected_emp)

    st.dataframe(apply_table_colors(df), use_container_width=True)



# ============================================================
# === 10. ADMIN: VIEW ALL PAYROLL ============================
# ============================================================

if role == "admin" and menu == "📊 View All Payroll":

    st.title("📊 All Payroll Records (System-wide)")

    start_date = st.date_input("Start date", datetime(2025, 11, 1))
    end_date = st.date_input("End date", datetime(2025, 11, 30))

    df = generate_payroll_data(start_date, end_date, selected_employee="All")

    st.dataframe(apply_table_colors(df), use_container_width=True)



# ============================================================
# === 11. EMPLOYEE DASHBOARD ================================
# ============================================================

if role == "employee" and menu == "📋 My Work":

    st.title("📋 My Work Overview")

    employee_name = st.session_state.username

    st.info(f"Hello **{employee_name}**, here you will later see your real work logs.")

    st.write("This section will be updated when we add real work submission.")
# ============================================================
# === 12. MANAGER: ADD EMPLOYEE ===============================
# ============================================================

if role == "manager" and menu == "➕ Add Employee":

    st.title("➕ Add New Employee")

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

            result = db_insert("employees", {
                "firstname": firstname,
                "lastname": lastname,
                "address": address,
                "username": username_new,
                "password": hashed_pw,
                "role": "employee"
            })

            st.success(f"✅ Employee {firstname} {lastname} created successfully!")



# ============================================================
# === 13. MANAGER: VIEW EMPLOYEES =============================
# ============================================================

if role == "manager" and menu == "📋 My Employees":

    st.title("📋 My Employees")

    employees = db_select("employees", "?role=eq.employee")

    if not employees:
        st.info("No employees found yet.")
    else:
        df = pd.DataFrame(employees)[["firstname", "lastname", "username"]]
        st.dataframe(df, use_container_width=True)



# ============================================================
# === 14. ADMIN: ADD MANAGER =================================
# ============================================================

if role == "admin" and menu == "➕ Add Manager":

    st.title("➕ Add New Manager")

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

            result = db_insert("employees", {
                "firstname": firstname,
                "lastname": lastname,
                "address": address,
                "username": username_new,
                "password": hashed_pw,
                "role": "manager"
            })

            st.success(f"✅ Manager {firstname} {lastname} created successfully!")



# ============================================================
# === 15. ADMIN: LIST & DELETE MANAGERS =======================
# ============================================================

if role == "admin" and menu == "📋 List Managers":

    st.title("📋 All Managers")

    managers = db_select("employees", "?role=eq.manager")

    if not managers:
        st.info("No managers found.")
    else:
        df = pd.DataFrame(managers)[["firstname", "lastname", "username"]]
        st.dataframe(df, use_container_width=True)

        st.markdown("---")
        st.markdown("### 🗑 Delete Manager")

        usernames = [m["username"] for m in managers]
        selected = st.selectbox("Select Manager", usernames)
        delete_btn = st.button("Delete Manager")

        if delete_btn:

            del_result = db_delete("employees", f"?username=eq.{selected}")

            st.success(f"Manager '{selected}' deleted.")



# ============================================================
# === 16. EMPLOYEE: SUBMIT DAILY WORK =========================
# ============================================================

if role == "employee" and menu == "📝 Submit Day Work":

    st.title("📝 Submit Daily Work")

    st.info("This feature will be connected to real payroll soon.")

    with st.form("submit_work_form"):
        date_work = st.date_input("Date")
        wijk_name = st.text_input("Wijk Name")
        segments = st.number_input("Segments", min_value=1, max_value=10)
        trip_km = st.number_input("Trip KM", min_value=0, max_value=400)

        submit_btn = st.form_submit_button("Submit")

    if submit_btn:
        st.success("✔ Work submitted (simulation, not yet stored)")
# ============================================================
# === 17. SUMMARY BOX (FOR MANAGER & ADMIN) ==================
# ============================================================

def parse_euro(x):
    if isinstance(x, str) and "€" in x:
        try:
            return float(x.replace("€", "").strip())
        except:
            return 0
    return 0

def parse_num(x):
    try:
        return float(x)
    except:
        return 0


def render_summary(df):

    if df is None or df.empty:
        return

    total_day_earn = df["Day Earn (€)"].apply(parse_euro).sum()
    total_segments = df["Wijk Volume/Segment"].apply(parse_num).sum()
    total_km       = df["Trip (KM)"].apply(parse_num).sum()
    total_trip     = df["Trip Cost (€)"].apply(parse_euro).sum()

    st.markdown("### 📦 Summary Overview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Earn (€)", f"€ {total_day_earn:,.2f}")
    col2.metric("Total Segments", f"{total_segments:,.0f}")
    col3.metric("Total Trip (KM)", f"{total_km:,.0f} km")
    col4.metric("Total Trip Cost (€)", f"€ {total_trip:,.2f}")



# ============================================================
# === 18. MANAGER SUMMARY CALL ===============================
# ============================================================

if role == "manager" and menu == "📊 Dashboard":

    df_summary = df
    render_summary(df_summary)



# ============================================================
# === 19. ADMIN SUMMARY CALL (ALL PAYROLL) ===================
# ============================================================

if role == "admin" and menu == "📊 View All Payroll":

    df_summary = df
    render_summary(df_summary)



# ============================================================
# === 20. SYSTEM SETTINGS (ADMIN) =============================
# ============================================================

if role == "admin" and menu == "⚙ System Settings":

    st.title("⚙ System Settings")

    st.write("""
    Here you can manage advanced system-level options in the future:
    - Change admin password  
    - View audit logs  
    - Backup system  
    - Add new global configuration  
    """)



# ============================================================
# === 21. USER PROFILE (EMPLOYEE) ============================
# ============================================================

if role == "employee" and menu == "⚙ Profile":

    employee_username = st.session_state.username
    employee = get_user_by_username(employee_username)

    st.title("👤 My Profile")

    st.write(f"**First Name:** {employee['firstname']}")
    st.write(f"**Last Name:** {employee['lastname']}")
    st.write(f"**Username:** {employee['username']}")
    st.write(f"**Address:** {employee['address']}")
    st.write(f"**Role:** {employee['role']}")



# ============================================================
# === 22. GLOBAL CSS FOR MOBILE UI ===========================
# ============================================================

st.markdown(
    """
<style>

html, body, [class*="css"] {
    font-size: 15px !important;
}

/* Buttons */
.stButton > button {
    width: 100%;
    padding: 10px;
    font-size: 16px;
    border-radius: 10px;
}

/* Dataframe scroll smooth */
[data-testid="stDataFrame"] div {
    scrollbar-width: thin;
}

/* Sticky header area for filters */
.sticky-filter {
    position: sticky;
    top: 0;
    z-index: 999;
    background: #f8f9fa;
    padding: 10px;
    border-radius: 10px;
}

</style>
""",
    unsafe_allow_html=True
)



# ============================================================
# === 23. FOOTER =============================================
# ============================================================

st.markdown(
    """
<br><br>
<div style='text-align:center; color:gray; font-size:13px;'>
    Delvero Payroll System — Powered by Streamlit & Supabase  
</div>
""",
    unsafe_allow_html=True
)
