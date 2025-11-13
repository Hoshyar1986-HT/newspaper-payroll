# ------------------------------------------------------------
# 🗞️ Delvero Payroll System - Full Version (Login + Dashboard)
# Author: (Your Name)
# Date: November 2025
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
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------------------------------------------------
# Generate static daily data (Nov 1–13, 2025)
# ------------------------------------------------------------
def generate_daily_data():
    start_date = datetime(2025, 11, 1)
    end_date = datetime(2025, 11, 13)
    all_rows = []

    employees = ["Hossein", "Hoshyar", "Masoud"]

    for i in range((end_date - start_date).days + 1):
        current_day = start_date + timedelta(days=i)
        weekday = current_day.strftime("%A")
        is_sunday = (current_day.weekday() == 6)

        for emp in employees:
            if is_sunday:
                status = "Off"
                wijks = ""
            else:
                # Hossein
                if emp == "Hossein":
                    if current_day.day == 12:
                        status = "Off"
                        wijks = ""
                    else:
                        status = "On"
                        wijks = "Chaam1, Chaam4, Galder1"

                # Hoshyar
                elif emp == "Hoshyar":
                    if current_day.day == 12:
                        status = "On"
                        wijks = "Chaam1, Chaam4, Galder1"
                    elif current_day.day == 13:
                        status = "On"
                        wijks = "Lexmond2"
                    else:
                        status = "Off"
                        wijks = ""

                # Masoud
                elif emp == "Masoud":
                    status = "On" if not is_sunday else "Off"
                    wijks = "Rotterdam1, Rotterdam2" if not is_sunday else ""

            all_rows.append({
                "Date": current_day.strftime("%Y-%m-%d"),
                "Day": weekday,
                "Employee": emp,
                "Work Status": status,
                "Wijk(s)": wijks
            })

    return pd.DataFrame(all_rows)

# ------------------------------------------------------------
# Dummy user database
# ------------------------------------------------------------
users = {
    "Maryam": {"password": "1234", "role": "manager"},
    "Hossein": {"password": "1234", "role": "employee"},
    "Hoshyar": {"password": "1234", "role": "employee"},
    "Masoud": {"password": "1234", "role": "employee"}
}

# ------------------------------------------------------------
# Helper: color rows for dataframe
# ------------------------------------------------------------
def color_rows(row):
    if row["Work Status"] == "On":
        return ["background-color: #b6f7b6"] * len(row)
    elif row["Day"] == "Sunday":
        return ["background-color: #fff5b6"] * len(row)
    else:
        return ["background-color: #f7b6b6"] * len(row)

# ------------------------------------------------------------
# LOGIN SCREEN
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
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

# ------------------------------------------------------------
# MAIN APP INTERFACE (after login)
# ------------------------------------------------------------
if "logged_in" in st.session_state and st.session_state.logged_in:
    user = st.session_state.username
    role = st.session_state.role

    # Sidebar
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

    # --------------------------------------------------------
    # Manager Dashboard
    # --------------------------------------------------------
    if role == "manager" and menu == "📊 Dashboard":
        st.title("📊 Manager Dashboard")
        st.subheader("Daily Employee Overview (Nov 1–13, 2025)")

        df = generate_daily_data()

        # Filters
        with st.expander("🔍 Filter Options"):
            employees = df["Employee"].unique().tolist()
            selected_employees = st.multiselect("Select Employee(s):", employees, default=employees)

            min_date = pd.to_datetime(df["Date"]).min().date()
            max_date = pd.to_datetime(df["Date"]).max().date()
            start_date, end_date = st.date_input("Select Date Range:", [min_date, max_date])

        # Apply filters
        filtered_df = df.copy()
        filtered_df["Date"] = pd.to_datetime(filtered_df["Date"])
        filtered_df = filtered_df[
            (filtered_df["Employee"].isin(selected_employees)) &
            (filtered_df["Date"].dt.date >= start_date) &
            (filtered_df["Date"].dt.date <= end_date)
        ]

        # Display table
        st.dataframe(
            filtered_df.style.apply(color_rows, axis=1),
            use_container_width=True,
            height=700
        )

        st.caption("🟩 On Duty 🟥 Off 🟨 Sunday (Holiday)")

        # Summary
        st.markdown("### 📈 Summary per Employee")
        summary = (
            filtered_df.groupby("Employee")
            .agg(
                Total_Work_Days=("Date", "nunique"),
                Total_On_Days=("Work Status", lambda x: (x == "On").sum()),
                Total_Off_Days=("Work Status", lambda x: (x == "Off").sum())
            )
            .reset_index()
        )
        st.dataframe(summary, use_container_width=True)

    # --------------------------------------------------------
    # Manager Settings Page
    # --------------------------------------------------------
    elif role == "manager" and menu == "⚙️ Settings":
        st.title("⚙️ Manager Settings")
        st.info("In future updates, you will be able to add/remove employees or define Wijk rates here.")

    # --------------------------------------------------------
    # Employee Dashboard (basic)
    # --------------------------------------------------------
    elif role == "employee" and menu == "📋 My Work":
        st.title(f"👷 Employee Dashboard – {user}")
        df = generate_daily_data()
        my_df = df[df["Employee"] == user]
        st.dataframe(
            my_df.style.apply(color_rows, axis=1),
            use_container_width=True,
            height=600
        )
        st.caption("🟩 On Duty 🟥 Off 🟨 Sunday (Holiday)")

    elif role == "employee" and menu == "⚙️ Profile":
        st.title("⚙️ Profile Settings")
        st.info("Profile editing and password management will be available soon.")

# ------------------------------------------------------------
# Styling
# ------------------------------------------------------------
st.markdown("""
<style>
html, body, [class*="css"] {
    font-size: 15px !important;
}
.stButton>button {
    width: 100%;
    font-size: 16px;
    padding: 0.6em 0;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)
