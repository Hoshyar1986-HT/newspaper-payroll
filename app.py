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
# === 2. SUPABASE CONNECTION =================================
# ============================================================

SUPABASE_URL = "https://qggrtnyfgvlrmoopjdte.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFnZ3J0bnlmZ3Zscm1vb3BqZHRlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMxMTYxMjQsImV4cCI6MjA3ODY5MjEyNH0.WCSXtc_l5aNndAOTagLW-LWQPePIWPlLNRkWx_MNacI"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


# ============================================================
# === 3. HELPER FUNCTIONS ====================================
# ============================================================

def hash_password(password: str):
    """Creates a SHA256 hash for a password."""
    return hashlib.sha256(password.encode()).hexdigest()


def check_password(input_password, stored_hash):
    return hash_password(input_password) == stored_hash


def add_employee_to_supabase(firstname, lastname, address, username, password):
    """Insert new employee into Supabase"""
    hashed = hash_password(password)
    data = {
        "firstname": firstname,
        "lastname": lastname,
        "address": address,
        "username": username,
        "password": hashed,
        "role": "employee"
    }
    return supabase.table("employees").insert(data).execute()


def get_employee_by_username(username):
    """Fetch user from Supabase"""
    result = supabase.table("employees").select("*").eq("username", username).execute()
    if result.data:
        return result.data[0]
    return None


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

if "logged_in" in st.session_state and st.session_state.logged_in:

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

if role == "manager" and menu == "📊 Dashboard":

    st.markdown("""
    <div style="
        position:sticky;
        top:0;
        background:#f0f2f6;
        padding:18px;
        border-radius:10px;
        z-index:999;
        margin-bottom:10px;
    ">
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.1, 1.6])

    # Employee Selector Placeholder (will fill after DF load)
    with col1:
        st.markdown("#### 👤 Employee")
        employee_selector_placeholder = st.empty()

    # Month selector
    with col2:
        st.markdown("#### 📅 Month")
        month_selector = st.selectbox(
            "",
            ["November 2025", "Whole Range"],
            label_visibility="collapsed"
        )

    # Date range placeholder
    with col3:
        st.markdown("#### 🗓️ Date Range")
        date_range_placeholder = st.empty()

    st.markdown("</div>", unsafe_allow_html=True)
# ============================================================
# === 7. PAYROLL DATA GENERATOR (SIMULATED DATA) =============
# ============================================================

def generate_payroll_data(start_date, end_date, selected_employee):
    """Generate simulated payroll data based on your rules."""

    date_list = pd.date_range(start=start_date, end=end_date)

    records = []

    # Prices and segments for each wijk
    wijk_segments = {
        "Chaam1": 3, "Chaam4": 4, "Galder1": 2,
        "Lexmond2": 3,
        "Rotterdam1": 3, "Rotterdam2": 3
    }

    wijk_prices = {2: 650, 3: 750, 4: 850}

    # Trip km for each employee
    trip_km = {
        "Hossein": 120,
        "Hoshyar": 45,
        "Masoud": 60
    }

    for date in date_list:

        weekday = date.strftime("%A")

        # Skip Sundays
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

        # Payroll logic per employee
        for emp in ["Hossein", "Hoshyar", "Masoud"]:

            if selected_employee != "All" and emp != selected_employee:
                continue

            # Default: employee works
            onoff = "On"

            # Wijk assignments
            wijks = []

            # Hossein → 1 to 13 Nov except 12 Off
            if emp == "Hossein":
                if date.day == 12:
                    wijks = []
                    onoff = "Off"
                else:
                    wijks = ["Chaam1", "Chaam4", "Galder1"]

            # Hoshyar → off except 12 + 13
            elif emp == "Hoshyar":
                if date.day == 12:
                    wijks = ["Chaam1", "Chaam4", "Galder1"]
                elif date.day == 13:
                    wijks = ["Lexmond2"]
                else:
                    wijks = []
                    onoff = "Off"

            # Masoud → always works (except Sundays)
            elif emp == "Masoud":
                wijks = ["Rotterdam1", "Rotterdam2"]

            # WORKED WIKJS?
            if len(wijks) == 0:
                onoff = "Off"

            # Segment total
            segments = sum(wijk_segments.get(w, 3) for w in wijks) if wijks else 0

            # Price total
            wijk_earn_list = []
            total_wijk_price = 0

            for w in wijks:
                seg = wijk_segments.get(w, 3)
                price = wijk_prices.get(seg, 750)
                wijk_earn_list.append(f"{w} ({price}€)")
                total_wijk_price += price

            # Trip logic
            km = trip_km.get(emp, 0) if onoff == "On" else 0
            trip_cost = km * 0.16

            # Wijk Earn per day
            wijk_earn = total_wijk_price / 26 if onoff == "On" else 0

            # Total daily earn
            day_earn = wijk_earn + trip_cost if onoff == "On" else 0

            records.append({
                "Date": date.date(),
                "Day": weekday,
                "Employee": emp,
                "On/Off": onoff,
                "Wijk(s) name": ", ".join(wijks) if wijks else "-",
                "Wijk Volume/Segment": segments if segments else "-",
                "Wijk Price (€)": total_wijk_price if total_wijk_price else "-",
                "Trip (KM)": km if km else "-",
                "Trip Cost (€)": f"€ {trip_cost:.2f}" if km else "-",
                "Day Earn (€)": f"€ {day_earn:.2f}" if day_earn else "-"
            })

    return pd.DataFrame(records)


# ============================================================
# === 8. TABLE FORMATTING & COLORING =========================
# ============================================================

def apply_table_colors(df):
    """Color rows: Sunday red, Off orange."""
    def color_row(row):
        if row["Day"] == "Sunday":
            return ["background-color: #ffb3b3"] * len(row)
        elif row["On/Off"] == "Off":
            return ["background-color: #ffd9b3"] * len(row)
        return [""] * len(row)

    return df.style.apply(color_row, axis=1)


# ============================================================
# === 9. RENDER DASHBOARD TABLE ==============================
# ============================================================

if role == "manager" and menu == "📊 Dashboard":

    # Apply employee selector
    employees = ["All", "Hossein", "Hoshyar, ", "Masoud"]
    selected_emp = employee_selector_placeholder.selectbox("", employees)

    # Date range
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

        st.subheader("📊 Payroll Report")
        render_dashboard_view(df)

# ============================================================
# === 10. DASHBOARD DISPLAY WRAPPER ==========================
# ============================================================

def render_dashboard_view(df):
    """Main layout for payroll dashboard."""
    st.subheader("📊 Payroll Report")

    # Show table
    st.dataframe(apply_table_colors(df), use_container_width=True)

    # Store DF for summary
    st.session_state.current_df = df

# ============================================================
# === 11. SUMMARY BOX (TOTALS) ===============================
# ============================================================

if role == "manager" and menu == "📊 Dashboard":

    df = st.session_state.get("current_df", None)

    if df is not None:

        # Safe Parsers
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

        # Totals
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
# === 12. ADD EMPLOYEE PAGE (REAL SUPABASE) ==================
# ============================================================

if role == "manager" and menu == "➕ Add Employee":

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
            hashed_pw = hash_password(password_new)

            response = supabase.table("employees").insert({
                "firstname": firstname,
                "lastname": lastname,
                "address": address,
                "username": username_new,
                "password": hashed_pw,
                "role": "employee"
            }).execute()

            if response.data:
                st.success(f"✅ Employee **{firstname} {lastname}** added successfully!")
            else:
                st.error("❌ Failed to add employee.")


# ============================================================
# === 13. SETTINGS PAGE ======================================
# ============================================================

if role == "manager" and menu == "⚙️ Settings":

    st.title("⚙️ Settings")

    st.markdown("""
    Settings page will later include:
    - Edit Employee
    - Delete Employee
    - Create Wijk
    - Edit Wijk
    - Change Manager Password
    """)


# ============================================================
# === 14. GLOBAL CSS (UI Enhancements) =======================
# ============================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    font-size: 14px !important;
}

/* Button styling */
.stButton>button {
    width: 100%;
    font-size: 16px;
    padding: 8px 0;
    border-radius: 10px;
}

/* Sticky filter bar */
.filter-bar {
    position: sticky;
    top: 0;
    z-index: 1000;
}

</style>
""", unsafe_allow_html=True)
