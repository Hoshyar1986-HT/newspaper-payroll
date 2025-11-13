# ------------------------------------------------------------
# 🗞️ Delvero Payroll System - Realistic Daily Table (with €)
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
# Generate realistic daily data (Nov 1–13, 2025)
# ------------------------------------------------------------
def generate_realistic_data():
    start_date = datetime(2025, 11, 1)
    end_date = datetime(2025, 11, 13)
    all_rows = []

    employees = ["Hossein", "Hoshyar", "Masoud"]

    # Wijk segment mapping
    segment_map = {"Chaam1": 3, "Chaam4": 4, "Galder1": 2}
    # Trip km per person
    trip_km = {"Hossein": 120, "Hoshyar": 45, "Masoud": 60}

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

            # Calculate values
            if status == "On":
                wijk_list = [w.strip() for w in wijks.split(",") if w.strip()]
                volumes = []
                prices = []
                for w in wijk_list:
                    seg = segment_map.get(w, 3)
                    volumes.append(seg)
                    if seg == 2:
                        prices.append(650)
                    elif seg == 3:
                        prices.append(750)
                    elif seg == 4:
                        prices.append(850)

                total_wijk_price = sum(prices)
                km = trip_km[emp]
                trip_cost = km * 0.16
                day_earn = (total_wijk_price / 26) + trip_cost

            else:
                wijk_list = []
                volumes = []
                prices = []
                total_wijk_price = 0
                km = trip_km[emp]
                trip_cost = km * 0.16
                day_earn = 0

            all_rows.append({
                "Date": current_day.strftime("%Y-%m-%d"),
                "Day": weekday,
                "Employee": emp,
                "On/Off of Work": status,
                "Wijk(s) Name": ", ".join(wijk_list) if wijk_list else "",
                "Wijk Volume/Segment": ", ".join(str(v) for v in volumes) if volumes else "",
                "Wijk Price (€)": ", ".join([f"€ {p:.2f}" for p in prices]) if prices else "",
                "Trip (KM)": km,
                "Trip Cost (€)": f"€ {trip_cost:.2f}",
                "Day Earn (€)": f"€ {day_earn:.2f}"
            })

    return pd.DataFrame(all_rows)

# ------------------------------------------------------------
# Color styling for rows
# ------------------------------------------------------------
def color_rows(row):
    if row["On/Off of Work"] == "On":
        return ["background-color: #b6f7b6"] * len(row)  # Green
    elif row["Day"] == "Sunday":
        return ["background-color: #fff5b6"] * len(row)  # Yellow
    else:
        return ["background-color: #f7b6b6"] * len(row)  # Red

# ------------------------------------------------------------
# Login section
# ------------------------------------------------------------
users = {
    "Maryam": {"password": "1234", "role": "manager"},
    "Hossein": {"password": "1234", "role": "employee"},
    "Hoshyar": {"password": "1234", "role": "employee"},
    "Masoud": {"password": "1234", "role": "employee"}
}

if "logged_in" not in st.session_state:
    st.title("🗞️ Delvero Payroll Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")

    if login_btn:
        if username in users and users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = users[username]["role"]
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

# ------------------------------------------------------------
# Main App (after login)
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
        st.subheader("Daily Payroll Overview (Nov 1–13, 2025)")

        df = generate_realistic_data()

        # Filter section
        with st.expander("🔍 Filter Options"):
            employees = df["Employee"].unique().tolist()
            selected_employees = st.multiselect("Select Employee(s):", employees, default=employees)
            min_date = pd.to_datetime(df["Date"]).min().date()
            max_date = pd.to_datetime(df["Date"]).max().date()
            start_date, end_date = st.date_input("Select Date Range:", [min_date, max_date])

        filtered_df = df.copy()
        filtered_df["Date"] = pd.to_datetime(filtered_df["Date"])
        filtered_df = filtered_df[
            (filtered_df["Employee"].isin(selected_employees)) &
            (filtered_df["Date"].dt.date >= start_date) &
            (filtered_df["Date"].dt.date <= end_date)
        ]

        st.dataframe(
            filtered_df.style.apply(color_rows, axis=1),
            use_container_width=True,
            height=750
        )

        st.caption("🟩 On Duty 🟥 Off 🟨 Sunday (Holiday)")

    elif role == "manager" and menu == "⚙️ Settings":
        st.title("⚙️ Manager Settings")
        st.info("You can manage employees or Wijk rates here in future versions.")

    # ----------------------------
    # Employee Dashboard
    # ----------------------------
    elif role == "employee" and menu == "📋 My Work":
        st.title(f"👷 Employee Dashboard – {user}")
        df = generate_realistic_data()
        my_df = df[df["Employee"] == user]
        st.dataframe(my_df.style.apply(color_rows, axis=1), use_container_width=True, height=650)
        st.caption("🟩 On Duty 🟥 Off 🟨 Sunday (Holiday)")

    elif role == "employee" and menu == "⚙️ Profile":
        st.title("⚙️ Profile Settings")
        st.info("Profile editing and password change options coming soon.")

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
