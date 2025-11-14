# ============================================================
# === 1. IMPORTS & PAGE SETUP ================================
# ============================================================

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from supabase import create_client, Client
import hashlib

st.set_page_config(
    page_title="Delvero Payroll System",
    page_icon="🗞️",
    layout="wide"
)


# ============================================================
# === 2. SUPABASE CONFIG (REST API) ==========================
# ============================================================

import requests
import json

SUPABASE_URL = "https://qggrtnyfgvlrmoopjdte.supabase.co"
SUPABASE_ANON_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFnZ3J0bnlmZ3Zscm1vb3BqZHRlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMxMTYxMjQsImV4cCI6MjA3ODY5MjEyNH0."
    "WCSXtc_l5aNndAOTagLW-LWQPePIWPlLNRkWx_MNacI"
)

SUPABASE_HEADERS = {
    "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type": "application/json"
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


def add_employee_to_supabase(firstname, lastname, address, username, password):
    hashed = hash_password(password)
    data = {
        "firstname": firstname,
        "lastname": lastname,
        "address": address,
        "username": username,
        "password": hashed,
        "role": "employee"
    }
    return db_insert("employees", data)


def get_employee_by_username(username):
    result = db_select("employees", f"?username=eq.{username}")
    return result[0] if result else None



# ============================================================
# === 4. LOGIN PAGE ==========================================
# ============================================================

if "logged_in" not in st.session_state:

    st.title("🗞️ Delvero Payroll Login")

    with st.form("login_form"):
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")

    if login_btn:
        user_record = get_employee_by_username(username_input)

        if user_record and check_password(password_input, user_record["password"]):
            st.session_state.logged_in = True
            st.session_state.username = user_record["username"]
            st.session_state.role = user_record["role"]
            st.rerun()
        else:
            st.error("❌ Invalid username or password")


# ============================================================
# === 5. SIDEBAR MENU ========================================
# ============================================================

if st.session_state.get("logged_in"):

    user = st.session_state.username
    role = st.session_state.role

    with st.sidebar:
        st.header(f"👋 Welcome, {user}")

        if role == "manager":
            menu = st.radio("Menu", ["📊 Dashboard", "➕ Add Employee", "⚙️ Settings"])
        else:
            menu = st.radio("Menu", ["📋 My Work", "⚙️ Profile"])

        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.rerun()


# ============================================================
# === 6. FILTER BAR (MANAGER DASHBOARD) ======================
# ============================================================

if st.session_state.get("role") == "manager" and menu == "📊 Dashboard":

    st.markdown("""
    <div style="position:sticky; top:0; background:#f0f2f6;
                 padding:18px; border-radius:10px; z-index:999;">
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1.6])

    with col1:
        st.markdown("#### 👤 Employee")
        employee_selector_placeholder = st.empty()

    with col2:
        st.markdown("#### 📅 Month")
        month_selector = st.selectbox(
            "",
            ["November 2025", "Whole Range"],
            label_visibility="collapsed"
        )

    with col3:
        st.markdown("#### 🗓️ Date Range")
        date_range_placeholder = st.empty()

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# === 7. PAYROLL DATA GENERATOR ===============================
# ============================================================

def generate_payroll_data(start_date, end_date, selected_employee):
    date_list = pd.date_range(start=start_date, end=end_date)
    records = []

    wijk_segments = {
        "Chaam1": 3, "Chaam4": 4, "Galder1": 2,
        "Lexmond2": 3, "Rotterdam1": 3, "Rotterdam2": 3
    }
    wijk_prices = {2: 650, 3: 750, 4: 850}

    trip_km = {"Hossein": 120, "Hoshyar": 45, "Masoud": 60}

    for date in date_list:

        weekday = date.strftime("%A")

        # Sunday Off
        if weekday == "Sunday":
            for emp in ["Hossein", "Hoshyar", "Masoud"]:
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

            onoff = "On"
            wijks = []

            # Logic
            if emp == "Hossein":
                if date.day == 12:
                    onoff = "Off"
                    wijks = []
                else:
                    wijks = ["Chaam1", "Chaam4", "Galder1"]

            elif emp == "Hoshyar":
                if date.day == 12:
                    wijks = ["Chaam1", "Chaam4", "Galder1"]
                elif date.day == 13:
                    wijks = ["Lexmond2"]
                else:
                    wijks = []
                    onoff = "Off"

            elif emp == "Masoud":
                wijks = ["Rotterdam1", "Rotterdam2"]

            if len(wijks) == 0:
                onoff = "Off"

            segments = sum(wijk_segments.get(w, 3) for w in wijks) if wijks else 0

            total_price = 0
            wijk_price_readable = []
            for w in wijks:
                seg = wijk_segments.get(w, 3)
                price = wijk_prices.get(seg, 750)
                total_price += price
                wijk_price_readable.append(f"{w} ({price}€)")

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
# === 8. TABLE FORMATTING ====================================
# ============================================================

def apply_table_colors(df):

    def color_row(row):
        if row["Day"] == "Sunday":
            return ["background-color:#ffcccc"] * len(row)
        elif row["On/Off"] == "Off":
            return ["background-color:#ffe6cc"] * len(row)
        return [""] * len(row)

    return df.style.apply(color_row, axis=1)


# ============================================================
# === 9. RENDER PAYROLL DATAFRAME ============================
# ============================================================

if st.session_state.get("role") == "manager" and menu == "📊 Dashboard":

    employees = ["All", "Hossein", "Hoshyar", "Masoud"]
    selected_emp = employee_selector_placeholder.selectbox("", employees)

    start_default = datetime(2025, 11, 1)
    end_default = datetime(2025, 11, 30)

    date_range = date_range_placeholder.date_input(
        "",
        value=(start_default, end_default),
        label_visibility="collapsed"
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
        df = generate_payroll_data(start_date, end_date, selected_emp)

        # Wrapper Function
        def render_dashboard_view(df):
            st.subheader("📊 Payroll Report")
            st.dataframe(apply_table_colors(df), use_container_width=True)
            st.session_state.current_df = df

        render_dashboard_view(df)


# ============================================================
# === 10. DASHBOARD MAIN VIEW WRAPPER ========================
# ============================================================

# Already handled inside render_dashboard_view()


# ============================================================
# === 11. SUMMARY BOX ========================================
# ============================================================

if st.session_state.get("role") == "manager" and menu == "📊 Dashboard":

    df = st.session_state.get("current_df")

    if df is not None:

        def parse_euro(x):
            try:
                return float(x.replace("€", "").strip())
            except:
                return 0

        def parse_num(x):
            try:
                return float(x)
            except:
                return 0

        total_day_earn = df["Day Earn (€)"].apply(parse_euro).sum()
        total_segments = df["Wijk Volume/Segment"].apply(parse_num).sum()
        total_km = df["Trip (KM)"].apply(parse_num).sum()
        total_trip_cost = df["Trip Cost (€)"].apply(parse_euro).sum()

        st.markdown("### 📦 Summary Overview")

        colA, colB, colC, colD = st.columns(4)
        colA.metric("Total Earn (€)", f"€ {total_day_earn:,.2f}")
        colB.metric("Total Segments", f"{total_segments:,.0f}")
        colC.metric("Total Trip (KM)", f"{total_km:,.0f} km")
        colD.metric("Total Trip Cost (€)", f"€ {total_trip_cost:,.2f}")


# ============================================================
# === 12. ADD EMPLOYEE PAGE ==================================
# ============================================================

if st.session_state.get("role") == "manager" and menu == "➕ Add Employee":

    st.title("➕ Add New Employee")

    with st.form("form_add_emp"):
        firstname = st.text_input("First Name")
        lastname = st.text_input("Last Name")
        address = st.text_input("Address")

        st.markdown("### 🔐 Login Credentials")
        username_new = st.text_input("Username")
        password_new = st.text_input("Password", type="password")

        submit_btn = st.form_submit_button("Add Employee")

    if submit_btn:

        if not firstname or not lastname or not username_new or not password_new:
            st.error("❌ All fields except Address are required.")
        else:
            response = add_employee_to_supabase(
                firstname, lastname, address,
                username_new, password_new
            )
            if response.data:
                st.success(f"✅ Employee {firstname} {lastname} added successfully!")
            else:
                st.error("❌ Failed to add employee.")


# ============================================================
# === 13. SETTINGS PAGE ======================================
# ============================================================

if st.session_state.get("role") == "manager" and menu == "⚙️ Settings":

    st.title("⚙️ Settings")

    st.markdown("""
    Settings will include later:
    - Edit Employee
    - Delete Employee
    - Manage Wijk Database
    - Change Manager Password
    """)


# ============================================================
# === 14. GLOBAL CSS =========================================
# ============================================================

st.markdown("""
<style>
html, body, [class*="css"] {
    font-size: 14px !important;
}
.stButton > button {
    width: 100%;
    font-size:16px;
    padding:8px 0;
    border-radius:10px;
}
</style>
""", unsafe_allow_html=True)
