import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, datetime, timedelta

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title="Delvero Payroll",
    page_icon="🗞️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# Database connection
# -----------------------------
conn = sqlite3.connect('payroll.db', check_same_thread=False)
c = conn.cursor()

# -----------------------------
# Create tables if not exist
# -----------------------------
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT,
    manager_id INTEGER
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    date TEXT,
    wijk TEXT,
    segments INTEGER,
    note TEXT
)
''')
conn.commit()

# -----------------------------
# Initialize default users
# -----------------------------
def initialize_default_users():
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]
    if count == 0:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  ("Maryam", "1234", "manager"))
        conn.commit()
        c.execute("SELECT id FROM users WHERE username='Maryam'")
        manager_id = c.fetchone()[0]

        employees = ["Hoshyar", "Hossein", "Masoud"]
        for emp in employees:
            c.execute("INSERT INTO users (username, password, role, manager_id) VALUES (?, ?, ?, ?)",
                      (emp, "1234", "employee", manager_id))
        conn.commit()
        print("✅ Default users created.")
    else:
        print("ℹ️ Users already exist.")

initialize_default_users()

# -----------------------------
# Helper functions
# -----------------------------
def get_user_id(username):
    c.execute("SELECT id FROM users WHERE username=?", (username,))
    result = c.fetchone()
    return result[0] if result else None

def add_activity(user_id, day, wijk):
    c.execute('INSERT INTO activities (user_id, date, wijk, segments, note) VALUES (?, ?, ?, ?, ?)',
              (user_id, day, wijk, 1, ""))
    conn.commit()

def check_login(username, password):
    c.execute('SELECT id, role, manager_id FROM users WHERE username=? AND password=?',
              (username, password))
    return c.fetchone()

def get_all_activities_for_manager(manager_id):
    c.execute('''
        SELECT u.username, a.date, a.wijk, a.segments, a.note
        FROM activities a
        JOIN users u ON a.user_id = u.id
        WHERE u.manager_id=?
        ORDER BY date(a.date) ASC
    ''', (manager_id,))
    return c.fetchall()

# -----------------------------
# Seed sample data (1–13 Nov 2025)
# -----------------------------
def seed_sample_data():
    c.execute("SELECT COUNT(*) FROM activities")
    if c.fetchone()[0] > 0:
        print("ℹ️ Sample data already exists.")
        return

    hossein_id = get_user_id("Hossein")
    hoshyar_id = get_user_id("Hoshyar")
    masoud_id = get_user_id("Masoud")

    start_date = datetime(2025, 11, 1)
    end_date = datetime(2025, 11, 13)

    for i in range((end_date - start_date).days + 1):
        current_day = start_date + timedelta(days=i)
        weekday = current_day.weekday()
        if weekday == 6:  # Skip Sundays
            continue
        day_str = current_day.strftime("%Y-%m-%d")

        # Hossein
        if current_day.day != 12:
            for wijk in ["Chaam1", "Chaam4", "Galder1"]:
                add_activity(hossein_id, day_str, wijk)

        # Hoshyar
        if current_day.day == 12:
            for wijk in ["Chaam1", "Chaam4", "Galder1"]:
                add_activity(hoshyar_id, day_str, wijk)
        elif current_day.day == 13:
            add_activity(hoshyar_id, day_str, "Lexmond2")

        # Masoud
        for wijk in ["Rotterdam1", "Rotterdam2"]:
            add_activity(masoud_id, day_str, wijk)

    print("✅ Sample activities seeded for Nov 1–13, 2025.")

seed_sample_data()

# -----------------------------
# Login page
# -----------------------------
if "role" not in st.session_state:
    st.title("🗞️ Delvero Payroll Login")

    with st.form("login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        user = check_login(username, password)
        if user:
            st.session_state['user_id'] = user[0]
            st.session_state['role'] = user[1]
            st.session_state['manager_id'] = user[2]
            st.session_state['username'] = username
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

# -----------------------------
# Manager Dashboard
# -----------------------------
if 'role' in st.session_state and st.session_state['role'] == 'manager':
    st.title(f"📊 Manager Dashboard ({st.session_state['username']})")

    with st.sidebar:
        st.header("⚙️ Settings Menu")
        choice = st.radio("Select an option:", [
            "⬅️ Back to Dashboard",
            "👷 Manage Employees",
            "🗺️ Manage Wijk (coming soon)"
        ])

        st.divider()
        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.rerun()

    if choice == "⬅️ Back to Dashboard":
        st.subheader("📈 Employee Activity Report (Nov 1–13, 2025)")

        records = get_all_activities_for_manager(st.session_state['user_id'])
        if not records:
            st.info("No activities recorded yet.")
        else:
            df = pd.DataFrame(records, columns=["Employee", "Date", "Wijk", "Segments", "Note"])

            # --- Filter Panel ---
            with st.expander("🔍 Filter Options"):
                employees = df["Employee"].unique().tolist()
                selected_employees = st.multiselect("Select Employee(s):", employees, default=employees)

                wijks = df["Wijk"].unique().tolist()
                selected_wijks = st.multiselect("Select Wijk(s):", wijks, default=wijks)

                min_date = pd.to_datetime(df["Date"]).min().date()
                max_date = pd.to_datetime(df["Date"]).max().date()
                start_date, end_date = st.date_input("Select Date Range:", [min_date, max_date])

                exclude_sundays = st.checkbox("Exclude Sundays", value=True)

            # --- Apply Filters ---
            filtered_df = df.copy()
            filtered_df = filtered_df[filtered_df["Employee"].isin(selected_employees)]
            filtered_df = filtered_df[filtered_df["Wijk"].isin(selected_wijks)]
            filtered_df["Date"] = pd.to_datetime(filtered_df["Date"])
            filtered_df = filtered_df[(filtered_df["Date"].dt.date >= start_date) &
                                      (filtered_df["Date"].dt.date <= end_date)]

            if exclude_sundays:
                filtered_df["weekday"] = filtered_df["Date"].dt.weekday
                filtered_df = filtered_df[filtered_df["weekday"] != 6]
                filtered_df.drop(columns=["weekday"], inplace=True)

            # --- Display filtered results ---
            st.dataframe(filtered_df, use_container_width=True)

            # --- Summary Section ---
            st.markdown("### 📊 Summary per Employee")
            summary = (
                filtered_df.groupby("Employee")
                .agg(
                    total_days=("Date", "nunique"),
                    total_wijks=("Wijk", "count"),
                    total_segments=("Segments", "sum")
                )
                .reset_index()
            )
            st.dataframe(summary, use_container_width=True)

            # --- Download filtered data ---
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Download Filtered Data (CSV)",
                data=csv,
                file_name="filtered_activities.csv",
                mime="text/csv"
            )

    elif choice == "👷 Manage Employees":
        st.subheader("Employee Management (static data for now)")
        st.info("Employee management options will be available soon.")

    elif choice == "🗺️ Manage Wijk (coming soon)":
        st.info("Wijk rate management will be implemented in the next version.")

# -----------------------------
# Employee Dashboard
# -----------------------------
if 'role' in st.session_state and st.session_state['role'] == 'employee':
    st.title(f"👷 Employee Dashboard ({st.session_state['username']})")

    st.subheader("🗓️ Log Daily Activity")
    wijk = st.text_input("Wijk Name")
    segments = st.number_input("Number of Segments", min_value=0, value=0)
    note = st.text_area("Additional Notes (optional)")
    if st.button("Submit"):
        add_activity(st.session_state['user_id'], str(date.today()), wijk)
        st.success("✅ Activity recorded successfully!")

    st.subheader("📋 My Activity History")
    c.execute('SELECT date, wijk FROM activities WHERE user_id=? ORDER BY date DESC', (st.session_state['user_id'],))
    data = c.fetchall()
    if data:
        df = pd.DataFrame(data, columns=["Date", "Wijk"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No activities yet.")

    st.divider()
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

# -----------------------------
# Styling
# -----------------------------
st.markdown("""
<style>
html, body, [class*="css"] {
    font-size: 16px !important;
}
.stButton>button {
    width: 100%;
    font-size: 18px;
    padding: 0.75em 0;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)
