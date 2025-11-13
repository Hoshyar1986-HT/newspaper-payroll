# ------------------------------------------------------------
# 📊 Delvero Payroll Dashboard - Streamlit App
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
    page_title="Delvero Payroll Dashboard",
    page_icon="🗞️",
    layout="wide"
)

st.title("🗞️ Delvero Payroll System")
st.subheader("Manager Dashboard – Daily Employee Overview (Nov 1–13, 2025)")

st.markdown("""
This dashboard shows the daily activity log of employees between **November 1–13, 2025**,  
based on actual recorded working days and holidays.  
Each row represents **one employee’s activity on a given day**.
""")

# ------------------------------------------------------------
# Generate daily data (Nov 1–13)
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
                # Hossein’s pattern
                if emp == "Hossein":
                    if current_day.day == 12:
                        status = "Off"
                        wijks = ""
                    else:
                        status = "On"
                        wijks = "Chaam1, Chaam4, Galder1"

                # Hoshyar’s pattern
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

                # Masoud’s pattern
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
# Generate and display data
# ------------------------------------------------------------
df = generate_daily_data()

# ------------------------------------------------------------
# Filter controls
# ------------------------------------------------------------
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

# ------------------------------------------------------------
# Color styling
# ------------------------------------------------------------
def color_rows(row):
    if row["Work Status"] == "On":
        return ["background-color: #b6f7b6"] * len(row)  # Light green
    elif row["Day"] == "Sunday":
        return ["background-color: #fff5b6"] * len(row)  # Light yellow
    else:
        return ["background-color: #f7b6b6"] * len(row)  # Light red

# ------------------------------------------------------------
# Display table
# ------------------------------------------------------------
st.dataframe(
    filtered_df.style.apply(color_rows, axis=1),
    use_container_width=True,
    height=700
)

# ------------------------------------------------------------
# Summary Section
# ------------------------------------------------------------
st.markdown("### 📊 Summary per Employee")

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

# ------------------------------------------------------------
# Legend and Style
# ------------------------------------------------------------
st.caption("🟩 On Duty 🟥 Off 🟨 Sunday (Holiday)")

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
