# ------------------------------------------------------------
# 🗞️ Delvero Payroll System - Final Professional Version (Single Employee Filter)
# ------------------------------------------------------------

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ------------------------------------------------------------
# Page setup
# ------------------------------------------------------------
st.set_page_config(
    page_title="Delvero Payroll System",
    page_icon="🗞️",
    layout="wide"
)


# ------------------------------------------------------------
# Generate payroll data
# ------------------------------------------------------------
def generate_detailed_data():
    start_date = datetime(2025, 11, 1)
    end_date = datetime(2025, 11, 13)
    rows = []

    employees = ["Hossein", "Hoshyar", "Masoud"]

    segment_map = {"Chaam1": 3, "Chaam4": 4, "Galder1": 2}
    price_map = {2: 650, 3: 750, 4: 850}
    trip_km = {"Hossein": 120, "Hoshyar": 45, "Masoud": 60}

    for i in range((end_date - start_date).days + 1):
        current_day = start_date + timedelta(days=i)
        date_str = current_day.strftime("%Y-%m-%d")
        weekday = current_day.strftime("%A")
        is_sunday = current_day.weekday() == 6

        for emp in employees:
            km = trip_km[emp]
            trip_cost = km * 0.16

            # ------------ Sunday ------------
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

            # ------------ Determine Wijk(s) ------------
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

            # ------------ OFF (not Sunday) ------------
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

            # ------------ Calculate earnings ------------
            wijk_earn_list = []
            for w in wijks:
                seg = segment_map.get(w, 3)
                price = price_map.get(seg, 750)
                wijk_earn_list.append(price / 26)

            day_earn_total = sum(wijk_earn_list) + trip_cost

            # ------------ Add Wijk rows ------------
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
                    "Day Earn (€)": f"€ {day_earn_total:.2f}" if j == 0 else "-"
                })

    return pd.DataFrame(rows)


# ------------------------------------------------------------
# Row coloring
# ------------------------------------------------------------
def color_rows(row):

    if row["Day"] == "Sunday":
        return ["background-color: #ff9999"] * len(row)   # Red

    if row["On/Off of Work"] == "Off":
        return ["background-color: #ffcc99"] * len(row)   # Orange

    return ["background-color: white"] * len(row)


# ------------------------------------------------------------
# Users
# ------------------------------------------------------------
users = {
    "Maryam": {"password": "1234", "role": "manager"},
    "Hossein": {"password": "1234", "role": "employee"},
    "Hoshyar": {"password": "1234", "role": "employee"},
    "Masoud": {"password": "1234", "role": "employee"}
}


# ------------------------------------------------------------
# Login Page
# ------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.title("🗞️ Delvero Payroll Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        if username in users and users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = users[username]["role"]
            st.rerun()
        else:
            st.error("❌ Invalid username or password")


# ------------------------------------------------------------
# Main App
# ------------------------------------------------------------
if "logged_in" in st.session_state and st.session_state.logged_in:

    user = st.session_state.username
    role = st.session_state.role

    # ----------------------- Sidebar -----------------------
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


    # ------------------------------------------------------------
    # MANAGER DASHBOARD
    # ------------------------------------------------------------
    if role == "manager" and menu == "📊 Dashboard":

        st.title("📊 Manager Dashboard")
        df = generate_detailed_data()

        # ----------------------- FILTER BAR -----------------------
        st.markdown("""
        <div style="
            position:sticky;
            top:0;
            background:#f0f2f6;
            padding:15px;
            border-radius:10px;
            z-index:999;
        ">
        """, unsafe_allow_html=True)

        st.markdown("### 🔍 Filters")

        col1, col2, col3 = st.columns([1.2, 2, 1])

        # ------ Month Selector ------
        with col1:
            st.write("**Select Month**")
            month_option = st.selectbox(
                "Month",
                ["Whole Range", "November 2025"],
                index=0,
                label_visibility="collapsed"
            )

        # ------ Date Range ------
        with col2:
            st.write("**Select Date Range**")
            min_date = pd.to_datetime(df["Date_raw"]).min().date()
            max_date = pd.to_datetime(df["Date_raw"]).max().date()

            start_date, end_date = st.date_input(
                "Date Range:",
                [min_date, max_date],
                label_visibility="collapsed"
            )

        # ------ Employee Filter (Single Select) ------
        with col3:
            st.write("**Select Employee**")
            employees = df["Employee_raw"].unique().tolist()
            employee_selection = st.selectbox(
                "Employee",
                ["All"] + employees,
                index=0,
                label_visibility="collapsed"
            )

        st.markdown("</div>", unsafe_allow_html=True)

        # ----------------------- Apply Filters -----------------------

        if month_option == "November 2025":
            start_date = datetime(2025, 11, 1).date()
            end_date = datetime(2025, 11, 30).date()

        if employee_selection == "All":
            selected_employees = employees
        else:
            selected_employees = [employee_selection]

        mask = (
            df["Employee_raw"].isin(selected_employees) &
            (pd.to_datetime(df["Date_raw"]).dt.date >= start_date) &
            (pd.to_datetime(df["Date_raw"]).dt.date <= end_date)
        )

        display_df = df[mask].drop(columns=["Date_raw", "Employee_raw"])

        # ----------------------- Show Table -----------------------
        st.dataframe(
            display_df.style.apply(color_rows, axis=1),
            use_container_width=True,
            height=800
        )

        # ----------------------- TOTAL SUMMARY -----------------------
        st.markdown("---")
        st.subheader("💰 Total Earn (Selected Range)")

        # Extract Day Earn values
        day_earn_values = (
            display_df["Day Earn (€)"]
            .replace("-", None)
            .replace("", None)
            .dropna()
        )

        def parse_euro(x):
            return float(x.replace("€", "").strip())

        total_sum = day_earn_values.apply(parse_euro).sum()

        st.metric(
            label="Total Earn (€)",
            value=f"€ {total_sum:,.2f}"
        )

        st.caption("🔴 Sunday  |  🟧 Off  |  ⚪ Workday")


# ------------------------------------------------------------
# Global Styling
# ------------------------------------------------------------
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
