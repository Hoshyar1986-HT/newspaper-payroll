# ------------------------------------------------------------
# 🗞️ Delvero Payroll System - Multi-Wijk, Day Earn & Total Earn
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
# Generate realistic payroll data (Nov 1–13, 2025)
# ------------------------------------------------------------
def generate_detailed_data():
    start_date = datetime(2025, 11, 1)
    end_date = datetime(2025, 11, 13)
    rows = []

    employees = ["Hossein", "Hoshyar", "Masoud"]

    # Wijk segment mapping and trip settings
    segment_map = {"Chaam1": 3, "Chaam4": 4, "Galder1": 2}
    price_map = {2: 650, 3: 750, 4: 850}
    trip_km = {"Hossein": 120, "Hoshyar": 45, "Masoud": 60}

    for i in range((end_date - start_date).days + 1):
        current_day = start_date + timedelta(days=i)
        weekday = current_day.strftime("%A")
        is_sunday = (current_day.weekday() == 6)
        date_str = current_day.strftime("%Y-%m-%d")

        for emp in employees:
            km = trip_km[emp]
            trip_cost = km * 0.16

            # Sundays → off (no wijks)
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
        "Trip (KM)": "",
        "Trip Cost (€)": "",
        "Day Earn (€)": "",
        "Total Earn (€)": ""
                })
                continue

            # Determine Wijk(s)
            if emp == "Hossein":
                if current_day.day == 12:
                    wijks = []
                else:
                    wijks = ["Chaam1", "Chaam4", "Galder1"]
            elif emp == "Hoshyar":
                if current_day.day == 12:
                    wijks = ["Chaam1", "Chaam4", "Galder1"]
                elif current_day.day == 13:
                    wijks = ["Lexmond2"]
                else:
                    wijks = []
            elif emp == "Masoud":
                wijks = ["Rotterdam1", "Rotterdam2"]

            # No work that day
            if not wijks:
                rows.append({
                    "Date_raw": date_str,
                    "Employee_raw": emp,
                    "Date": date_str,
                    "Day": weekday,
                    "Employee": emp,
                    "On/Off of Work": "Off",
                    "Wijk(s) Name": "-",
                    "Wijk Volume/Segment": "-",
                    "Wijk Price (€)": "-",
                    "Trip (KM)": km,
                    "Trip Cost (€)": f"€ {trip_cost:.2f}",
                    "Day Earn (€)": "€ 0.00",
                    "Total Earn (€)": "€ 0.00"
                })
                continue

            # Calculate daily earnings (for all wijks of that day)
            total_wijk_price = sum(price_map.get(segment_map.get(w, 3), 750) for w in wijks)
            day_earn = total_wijk_price / 26
            total_earn = day_earn + trip_cost

            # One row per wijk (display), but raw date/employee always stored
            for j, w in enumerate(wijks):
                seg = segment_map.get(w, 3)
                price = price_map.get(seg, 750)

                rows.append({
                    "Date_raw": date_str,
                    "Employee_raw": emp,
                    "Date": date_str if j == 0 else "/",
                    "Day": weekday if j == 0 else "/",
                    "Employee": emp if j == 0 else "/",
                    "On/Off of Work": "On" if j == 0 else "/",
                    "Wijk(s) Name": w,
                    "Wijk Volume/Segment": seg,
                    "Wijk Price (€)": f"€ {price:.2f}",
                    "Trip (KM)": km if j == 0 else "/",
                    "Trip Cost (€)": f"€ {trip_cost:.2f}" if j == 0 else "/",
                    "Day Earn (€)": f"€ {day_earn:.2f}" if j == 0 else "/",
                    "Total Earn (€)": f"€ {total_earn:.2f}" if j == 0 else "/"
                })

    df = pd.DataFrame(rows)
    return df

# ------------------------------------------------------------
# Row colors
# ------------------------------------------------------------
def color_rows(row):
    # Sunday rows (regardless of wijk)
    if row["Day"] == "Sunday":
        return ["background-color: #ff9999"] * len(row)  # red
    
    # Off rows that are NOT Sunday
    if row["On/Off of Work"] == "Off":
        return ["background-color: #ffcc99"] * len(row)  # orange

    # All other rows (On days)
    return ["background-color: white"] * len(row)


# ------------------------------------------------------------
# User login data
# ------------------------------------------------------------
users = {
    "Maryam": {"password": "1234", "role": "manager"},
    "Hossein": {"password": "1234", "role": "employee"},
    "Hoshyar": {"password": "1234", "role": "employee"},
    "Masoud": {"password": "1234", "role": "employee"}
}

# ------------------------------------------------------------
# Login interface
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
# Main app content
# ------------------------------------------------------------
if "logged_in" in st.session_state and st.session_state.logged_in:
    user = st.session_state.username
    role = st.session_state.role

    with st.sidebar:
        st.header(f"👋 Welcome, {user}")
        if role == "manager":
            menu = st.radio("Select section:", ["📊 Dashboard", "⚙️ Settings"])
        else:
            menu = st.radio("Select section:", ["📋 My Work", "⚙️ Profile"])
        st.divider()
        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.rerun()

    # ----------------------------
    # Manager Dashboard
    # ----------------------------
    if role == "manager" and menu == "📊 Dashboard":
        st.title("📊 Manager Dashboard")
        st.subheader("Multi-Wijk Daily Payroll Report (Nov 1–13, 2025)")

        df = generate_detailed_data()

        # Filter options based on RAW columns (no '/')
        with st.expander("🔍 Filter Options"):
            employees = sorted(df["Employee_raw"].unique().tolist())
            selected_employees = st.multiselect("Select Employee(s):", employees, default=employees)

            min_date = pd.to_datetime(df["Date_raw"]).min().date()
            max_date = pd.to_datetime(df["Date_raw"]).max().date()
            start_date, end_date = st.date_input("Select Date Range:", [min_date, max_date])

        # Apply filters using RAW data
        mask = (
            df["Employee_raw"].isin(selected_employees) &
            (pd.to_datetime(df["Date_raw"]).dt.date >= start_date) &
            (pd.to_datetime(df["Date_raw"]).dt.date <= end_date)
        )
        filtered_df = df[mask].copy()

        # For display, we don't need the raw columns
        display_df = filtered_df.drop(columns=["Date_raw", "Employee_raw"])

        st.dataframe(
            display_df.style.apply(color_rows, axis=1),
            use_container_width=True,
            height=800
        )

        st.caption("🟩 On Duty 🟥 Off 🟨 Sunday (Holiday)")

    # (دیگر منوها مثل Settings / My Work را فعلاً ساده نگه می‌گذاریم)
# ------------------------------------------------------------
# Styling
# ------------------------------------------------------------
st.markdown("""
<style>
html, body, [class*="css"] {
    font-size: 14px !important;
}
.stButton>button {
    width: 100%;
    font-size: 16px;
    padding: 0.6em 0;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)
