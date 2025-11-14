# ============================================================
# === 1. PAGE SETUP ==========================================
# ============================================================

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Delvero Payroll System",
    page_icon="🗞️",
    layout="wide"
)



# ============================================================
# === 2. USER DATABASE =======================================
# ============================================================

# 2.1 Static users (later upgradeable to database)
users = {
    "Maryam": {"password": "1234", "role": "manager"},
    "Hossein": {"password": "1234", "role": "employee"},
    "Hoshyar": {"password": "1234", "role": "employee"},
    "Masoud": {"password": "1234", "role": "employee"}
}



# ============================================================
# === 3. LOGIN PAGE ==========================================
# ============================================================

if "logged_in" not in st.session_state:

    # 3.1 Login form UI
    st.title("🗞️ Delvero Payroll Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_btn = st.form_submit_button("Login")

    # 3.2 Login validation
    if submit_btn:
        if username in users and users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = users[username]["role"]
            st.rerun()
        else:
            st.error("❌ Invalid username or password")



# ============================================================
# === 4. DASHBOARD FILTER BAR UI =============================
# ============================================================

if "logged_in" in st.session_state and st.session_state.logged_in:

    user = st.session_state.username
    role = st.session_state.role

    # Sidebar menu
    with st.sidebar:
        st.header(f"👋 Welcome, {user}")

        if role == "manager":
            menu = st.radio("Menu", ["📊 Dashboard", "⚙️ Settings"])
        else:
            menu = st.radio("Menu", ["📋 My Work", "⚙️ Profile"])

        st.divider()

        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.rerun()

    # Only manager uses filters
    if role == "manager" and menu == "📊 Dashboard":

        # Sticky filter bar container
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

        # 4.1 Employee filter
        col1, col2, col3 = st.columns([1, 1.2, 1.6])

        with col1:
            st.markdown("### 👤 Employee")
            employee_selector_placeholder = st.empty()  # Will be filled after the dataframe loads

        # 4.2 Month & Year filter
        with col2:
            st.markdown("### 📅 Month & Year")
            month_selector = st.selectbox(
                "",
                ["Whole Range", "November 2025"],
                index=0,
                label_visibility="collapsed"
            )

        # 4.3 Custom Date Range filter
        with col3:
            st.markdown("### 🗓️ Date Range")
            date_range_placeholder = st.empty()  # Will populate later

        st.markdown("</div>", unsafe_allow_html=True)
# ============================================================
# === 5. DATA GENERATION =====================================
# ============================================================

def generate_detailed_data():
    # 5.1 Base date range
    start_date = datetime(2025, 11, 1)
    end_date = datetime(2025, 11, 13)

    rows = []

    # 5.2 Employees
    employees = ["Hossein", "Hoshyar", "Masoud"]

    # 5.3 Wijk segments
    segment_map = {"Chaam1": 3, "Chaam4": 4, "Galder1": 2}

    # 5.4 Pricing rules
    price_map = {2: 650, 3: 750, 4: 850}

    # 5.5 Trip KM for each employee
    trip_km = {"Hossein": 120, "Hoshyar": 45, "Masoud": 60}

    # 5.6 Iterate through each day
    for i in range((end_date - start_date).days + 1):
        current_day = start_date + timedelta(days=i)
        date_str = current_day.strftime("%Y-%m-%d")
        weekday = current_day.strftime("%A")
        is_sunday = current_day.weekday() == 6

        # Generate rows for each employee
        for emp in employees:

            km = trip_km[emp]
            trip_cost = km * 0.16  # 16 cents per km

            # 5.7 Sunday = always OFF
            if is_sunday:
                rows.append({
                    "Date_raw": date_str,
                    "Employee_raw": emp,
                    "Date": date_str,
                    "Day": "Sunday",
                    "Employee": "",
                    "On/Off of Work": "Off",
                    "Wijk(s) Name": "",
                    "Wijk Volume/Segment": "",
                    "Wijk Price (€)": "",
                    "Wijk Earn (€)": "",
                    "Trip (KM)": "",
                    "Trip Cost (€)": "",
                    "Day Earn (€)": ""
                })
                continue

            # 5.8 Wijk assignments
            if emp == "Hossein":
                wijks = [] if current_day.day == 12 else ["Chaam1", "Chaam4", "Galder1"]

            elif emp == "Hoshyar":
                if current_day.day == 12:
                    wijks = ["Chaam1", "Chaam4", "Galder1"]
                elif current_day.day == 13:
                    wijks = ["Lexmond2"]
                else:
                    wijks = []

            elif emp == "Masoud":
                wijks = ["Rotterdam1", "Rotterdam2"]

            # 5.9 Non-Sunday OFF
            if not wijks:
                rows.append({
                    "Date_raw": date_str,
                    "Employee_raw": emp,
                    "Date": date_str,
                    "Day": weekday,
                    "Employee": emp,
                    "On/Off of Work": "Off",
                    "Wijk(s) Name": "",
                    "Wijk Volume/Segment": "",
                    "Wijk Price (€)": "",
                    "Wijk Earn (€)": "",
                    "Trip (KM)": "",
                    "Trip Cost (€)": "",
                    "Day Earn (€)": ""
                })
                continue

            # 5.10 Compute earnings per Wijk
            wijk_earn_list = []
            for w in wijks:
                seg = segment_map.get(w, 3)
                price = price_map.get(seg, 750)
                wijk_earn_list.append(price / 26)

            total_day_earn = sum(wijk_earn_list) + trip_cost

            # 5.11 Create row per Wijk
            for j, w in enumerate(wijks):
                seg = segment_map.get(w, 3)
                price = price_map.get(seg, 750)
                wijk_earn = price / 26

                rows.append({
                    "Date_raw": date_str,
                    "Employee_raw": emp,
                    "Date": date_str if j == 0 else "-",
                    "Day": weekday if j == 0 else "-",
                    "Employee": emp if j == 0 else "-",
                    "On/Off of Work": "On" if j == 0 else "-",
                    "Wijk(s) Name": w,
                    "Wijk Volume/Segment": seg,
                    "Wijk Price (€)": f"€ {price:.2f}",
                    "Wijk Earn (€)": f"€ {wijk_earn:.2f}",
                    "Trip (KM)": km if j == 0 else "-",
                    "Trip Cost (€)": f"€ {trip_cost:.2f}" if j == 0 else "-",
                    "Day Earn (€)": f"€ {total_day_earn:.2f}" if j == 0 else "-"
                })

    return pd.DataFrame(rows)



# ============================================================
# === 6. TABLE STYLE (Coloring) ===============================
# ============================================================

def color_rows(row):

    # 6.1 Sunday = red
    if row["Day"] == "Sunday":
        return ["background-color: #ff9999"] * len(row)

    # 6.2 Off days = orange
    if row["On/Off of Work"] == "Off":
        return ["background-color: #ffcc99"] * len(row)

    # 6.3 Otherwise white
    return ["background-color: white"] * len(row)



# ============================================================
# === 7. MANAGER DASHBOARD (FILTERS + TABLE) =================
# ============================================================

if role == "manager" and menu == "📊 Dashboard":

    st.title("📊 Manager Dashboard")

    # 7.1 Load payroll data
    df = generate_detailed_data()

    # 7.2 Fill employee selector (from section 4)
    employees = df["Employee_raw"].unique().tolist()
    employee_selection = employee_selector_placeholder.selectbox(
        "",
        ["All"] + employees,
        index=0,
        label_visibility="collapsed"
    )

    # 7.3 Fill date range (from section 4)
    min_date = pd.to_datetime(df["Date_raw"]).min().date()
    max_date = pd.to_datetime(df["Date_raw"]).max().date()

    start_date, end_date = date_range_placeholder.date_input(
        "",
        [min_date, max_date],
        label_visibility="collapsed"
    )

    # 7.4 Month override
    if month_selector == "November 2025":
        start_date = datetime(2025, 11, 1).date()
        end_date = datetime(2025, 11, 30).date()

    # 7.5 Filter by employee
    if employee_selection == "All":
        selected_employees = employees
    else:
        selected_employees = [employee_selection]

    # 7.6 Apply all filters
    mask = (
        df["Employee_raw"].isin(selected_employees) &
        (pd.to_datetime(df["Date_raw"]).dt.date >= start_date) &
        (pd.to_datetime(df["Date_raw"]).dt.date <= end_date)
    )

    display_df = df[mask].drop(columns=["Date_raw", "Employee_raw"])

    # 7.7 Display final table
    st.dataframe(
        display_df.style.apply(color_rows, axis=1),
        use_container_width=True,
        height=800
    )
# ============================================================
# === 8. SUMMARY CARD (Totals + UI) ==========================
# ============================================================

if role == "manager" and menu == "📊 Dashboard":

    st.markdown("---")
    st.markdown("## 📦 Summary Overview")

    # --------------------------------------------------------
    # 8.1 Safe parsers (no errors ever)
    # --------------------------------------------------------

    def parse_euro(x):
        """Safely convert '€ 123.45' to float."""
        if not isinstance(x, str):
            return None
        x = x.replace("€", "").replace(",", "").strip()
        if x in ["", "-", "none", "None", None]:
            return None
        try:
            return float(x)
        except:
            return None

    def parse_num(x):
        """Safely convert numeric strings or '-' to float."""
        try:
            return float(x)
        except:
            return None

    # --------------------------------------------------------
    # 8.2 SUM CALCULATIONS (Safe)
    # --------------------------------------------------------

    total_earn_sum = display_df["Day Earn (€)"].apply(parse_euro).dropna().sum()
    total_segments = display_df["Wijk Volume/Segment"].apply(parse_num).dropna().sum()
    total_km = display_df["Trip (KM)"].apply(parse_num).dropna().sum()
    total_trip_cost = display_df["Trip Cost (€)"].apply(parse_euro).dropna().sum()

    # --------------------------------------------------------
    # 8.3 SUMMARY CARD UI
    # --------------------------------------------------------

    st.markdown("""
    <style>
    .summary-card {
        padding: 20px;
        background-color: #ffffff;
        border-radius: 14px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #e6e6e6;
    }
    .summary-metric {
        text-align: center;
        padding: 10px;
    }
    .summary-label {
        font-size: 15px;
        color: #555;
    }
    .summary-value {
        font-size: 22px;
        font-weight: 700;
        margin-top: -5px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="summary-card">', unsafe_allow_html=True)

    colA, colB, colC, colD = st.columns(4)

    with colA:
        st.markdown(f"""
        <div class="summary-metric">
            <div class="summary-label">Total Earn (€)</div>
            <div class="summary-value">€ {total_earn_sum:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with colB:
        st.markdown(f"""
        <div class="summary-metric">
            <div class="summary-label">Total Segments</div>
            <div class="summary-value">{total_segments:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with colC:
        st.markdown(f"""
        <div class="summary-metric">
            <div class="summary-label">Total Trip (KM)</div>
            <div class="summary-value">{total_km:,.0f} km</div>
        </div>
        """, unsafe_allow_html=True)

    with colD:
        st.markdown(f"""
        <div class="summary-metric">
            <div class="summary-label">Total Trip Price (€)</div>
            <div class="summary-value">€ {total_trip_cost:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)



# ============================================================
# === 9. EMPLOYEE DASHBOARD (FUTURE EXPANSION) ===============
# ============================================================

if role == "employee" and menu == "📋 My Work":
    st.title("📋 My Work Summary")

    st.info("Employee dashboard will be developed later.")



# ============================================================
# === 10. GLOBAL STYLING (CSS) ===============================
# ============================================================

st.markdown("""
<style>
html, body, [class*="css"] {
    font-size: 14px !important;
}
.stButton>button {
    width: 100%;
    font-size: 16px;
    padding: 8px 0;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)
