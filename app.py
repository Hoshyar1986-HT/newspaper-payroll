# ------------------------------------------------------------
# 🗞️ Delvero Payroll System - Wijk Rows with Slash Continuation
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
# Generate formatted data (Nov 1–13, 2025)
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
        weekday = current_day.strftime("%A")
        is_sunday = (current_day.weekday() == 6)

        for emp in employees:
            km = trip_km[emp]
            trip_cost = km * 0.16

            if is_sunday:
                rows.append({
                    "Date": current_day.strftime("%Y-%m-%d"),
                    "Day": weekday,
                    "Employee": emp,
                    "On/Off of Work": "Off",
                    "Wijk(s) Name": "-",
                    "Wijk Volume/Segment": "-",
                    "Wijk Price (€)": "-",
                    "Trip (KM)": km,
                    "Trip Cost (€)": f"€ {trip_cost:.2f}",
                    "Total Earn (€)": "€ 0.00"
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

            if not wijks:
                rows.append({
                    "Date": current_day.strftime("%Y-%m-%d"),
                    "Day": weekday,
                    "Employee": emp,
                    "On/Off of Work": "Off",
                    "Wijk(s) Name": "-",
                    "Wijk Volume/Segment": "-",
                    "Wijk Price (€)": "-",
                    "Trip (KM)": km,
                    "Trip Cost (€)": f"€ {trip_cost:.2f}",
                    "Total Earn (€)": "€ 0.00"
                })
                continue

            total_wijk_price = sum(price_map.get(segment_map.get(w, 3), 750) for w in wijks)
            total_earn = (total_wijk_price / 26) + trip_cost

            # Create rows for each wijk
            for j, w in enumerate(wijks):
                seg = segment_map.get(w, 3)
                price = price_map.get(seg, 750)

                rows.append({
                    "Date": current_day.strftime("%Y-%m-%d") if j == 0 else "/",
                    "Day": weekday if j == 0 else "/",
                    "Employee": emp if j == 0 else "/",
                    "On/Off of Work": "On" if j == 0 else "/",
                    "Wijk(s) Name": w,
                    "Wijk Volume/Segment": seg,
                    "Wijk Price (€)": f"€ {price:.2f}",
                    "Trip (KM)": km if j == 0 else "/",
                    "Trip Cost (€)": f"€ {trip_cost:.2f}" if j == 0 else "/",
                    "Total Earn (€)": f"€ {total_earn:.2f}" if j == 0 else "/"
                })

    return pd.DataFrame(rows)

# ------------------------------------------------------------
# Row colors
# ------------------------------------------------------------
def color_rows(row):
    if row["On/Off of Work"] == "On":
        return ["background-color: #b6f7b6"] * len(row)
    elif row["Day"] == "Sunday":
        return ["background-color: #fff5b6"] * len(row)
    else:
        return ["background-color: #f7b6b6"] * len(row)

# ------------------------------------------------------------
# User system
# ------------------------------------------------------------
users = {
    "Maryam": {"password": "1234", "role": "manager"},
    "Hossein": {"password": "1234", "role": "employee"},
    "Hoshyar": {"password": "1234", "role": "employee"},
    "Masoud": {"password": "1234", "role": "employee"}
}

# ------------------------------------------------------------
# Login screen
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
# Main app
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
        st.subheader("Daily Wijk Report with Continuation Marks")

        df = generate_detailed_data()

        with st.expander("🔍 Filter Options"):
            employees = df["Employee"].unique().tolist()
            selected_employees = st.multiselect("Select Employee(s):", employees, default=employees)
            min_date = pd.to_datetime(df["Date"].replace("/", pd.NA).dropna()).min().date()
            max_date = pd.to_datetime(df["Date"].replace("/", pd.NA).dropna()).max().date()
            start_date, end_date = st.date_input("Select Date Range:", [min_date, max_date])

        filtered_df = df[
            (df["Employee"].isin(selected_employees)) &
            (pd.to_datetime(df["Date"].replace("/", pd.NA), errors="coerce").dt.date >= start_date) &
            (pd.to_datetime(df["Date"].replace("/", pd.NA), errors="coerce").dt.date <= end_date)
        ]

        st.dataframe(
            filtered_df.style.apply(color_rows, axis=1),
            use_container_width=True,
            height=750
        )

        st.caption("🟩 On Duty 🟥 Off 🟨 Sunday (Holiday)")

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
