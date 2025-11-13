import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# -----------------------------
# تنظیمات صفحه
# -----------------------------
st.set_page_config(
    page_title="Delvero Payroll",
    page_icon="🗞️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# اتصال به دیتابیس
# -----------------------------
conn = sqlite3.connect('payroll.db', check_same_thread=False)
c = conn.cursor()

# -----------------------------
# ایجاد جداول در صورت عدم وجود
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
# افزودن داده‌های اولیه (Maryam و نیروهایش)
# -----------------------------
def initialize_default_users():
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]
    if count == 0:
        # افزودن کارفرما Maryam
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  ("Maryam", "1234", "manager"))
        conn.commit()

        # گرفتن ID کارفرما
        c.execute("SELECT id FROM users WHERE username='Maryam'")
        manager_id = c.fetchone()[0]

        # افزودن نیروها
        employees = ["Hoshyar", "Hossein", "Masoud"]
        for emp in employees:
            c.execute("INSERT INTO users (username, password, role, manager_id) VALUES (?, ?, ?, ?)",
                      (emp, "1234", "employee", manager_id))
        conn.commit()
        print("✅ Default users added.")
    else:
        print("ℹ️ Users already exist.")

initialize_default_users()

# -----------------------------
# توابع دیتابیس
# -----------------------------
def check_login(username, password):
    c.execute('SELECT id, role, manager_id FROM users WHERE username=? AND password=?',
              (username, password))
    return c.fetchone()

def add_user(username, password, role, manager_id=None):
    try:
        c.execute('INSERT INTO users (username, password, role, manager_id) VALUES (?, ?, ?, ?)',
                  (username, password, role, manager_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def add_activity(user_id, wijk, segments, note):
    c.execute('INSERT INTO activities (user_id, date, wijk, segments, note) VALUES (?, ?, ?, ?, ?)',
              (user_id, str(date.today()), wijk, segments, note))
    conn.commit()

def get_activities_by_user(user_id):
    c.execute('SELECT date, wijk, segments, note FROM activities WHERE user_id=? ORDER BY date DESC', (user_id,))
    return c.fetchall()

def get_employees_by_manager(manager_id):
    c.execute('SELECT id, username FROM users WHERE manager_id=?', (manager_id,))
    return c.fetchall()

def get_all_activities_for_manager(manager_id):
    c.execute('''
        SELECT u.username, a.date, a.wijk, a.segments, a.note
        FROM activities a
        JOIN users u ON a.user_id = u.id
        WHERE u.manager_id=?
        ORDER BY a.date DESC
    ''', (manager_id,))
    return c.fetchall()

# -----------------------------
# صفحه ورود (فقط اگر هنوز وارد نشده)
# -----------------------------
if "role" not in st.session_state:
    st.title("🗞️ Delvero Payroll Login")

    with st.form("login"):
        username = st.text_input("نام کاربری")
        password = st.text_input("رمز عبور", type="password")
        submitted = st.form_submit_button("ورود")

    if submitted:
        user = check_login(username, password)
        if user:
            st.session_state['user_id'] = user[0]
            st.session_state['role'] = user[1]
            st.session_state['manager_id'] = user[2]
            st.session_state['username'] = username
            st.rerun()
        else:
            st.error("❌ نام کاربری یا رمز عبور اشتباه است")

# -----------------------------
# پنل کارفرما
# -----------------------------
if 'role' in st.session_state and st.session_state['role'] == 'manager':
    # نوار بالای داشبورد
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title(f"📊 داشبورد کارفرما ({st.session_state['username']})")
    with col2:
        if st.button("⚙️ تنظیمات"):
            st.session_state["show_settings"] = not st.session_state.get("show_settings", False)

    # اگر تنظیمات باز باشد
    if st.session_state.get("show_settings", False):
        st.subheader("⚙️ تنظیمات مدیریتی")

        # مدیریت نیروها
        st.markdown("### 👷 مدیریت نیروها")
        with st.form("add_emp"):
            emp_username = st.text_input("نام کاربری نیرو")
            emp_password = st.text_input("رمز عبور نیرو", type="password")
            add_btn = st.form_submit_button("افزودن")
            if add_btn:
                success = add_user(emp_username, emp_password, "employee", st.session_state['user_id'])
                if success:
                    st.success(f"✅ کاربر '{emp_username}' افزوده شد")
                else:
                    st.error("❌ این نام کاربری قبلاً وجود دارد")

        # نمایش نیروها
        st.markdown("### 📋 لیست نیروها")
        employees = get_employees_by_manager(st.session_state['user_id'])
        if employees:
            st.dataframe(pd.DataFrame(employees, columns=["id", "نام کاربری"]), use_container_width=True)
        else:
            st.info("هیچ نیرویی ثبت نشده است")

        # بخش تعریف Wijk (فعلاً آماده برای نسخه بعد)
        st.divider()
        st.markdown("### 🗺️ تعریف Wijk‌ها (در نسخه بعدی فعال می‌شود)")

    else:
        # وقتی تنظیمات بسته است → فقط گزارش کار
        st.subheader("📈 گزارش عملکرد نیروها")
        records = get_all_activities_for_manager(st.session_state['user_id'])
        if records:
            df = pd.DataFrame(records, columns=["نیرو", "تاریخ", "Wijk", "Segments", "یادداشت"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("هیچ فعالیتی ثبت نشده است.")

    st.divider()
    if st.button("🚪 خروج"):
        st.session_state.clear()
        st.rerun()

# -----------------------------
# پنل نیرو
# -----------------------------
if 'role' in st.session_state and st.session_state['role'] == 'employee':
    st.title(f"👷 داشبورد نیرو ({st.session_state['username']})")

    st.subheader("🗓️ ثبت فعالیت روزانه")
    wijk = st.text_input("نام Wijk")
    segments = st.number_input("تعداد Segment", min_value=0, value=0)
    note = st.text_area("توضیحات (اختیاری)")
    if st.button("ثبت فعالیت"):
        add_activity(st.session_state['user_id'], wijk, segments, note)
        st.success("✅ فعالیت ثبت شد")

    st.subheader("📋 تاریخچه فعالیت‌های من")
    data = get_activities_by_user(st.session_state['user_id'])
    if data:
        df = pd.DataFrame(data, columns=["تاریخ", "Wijk", "Segments", "یادداشت"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("هیچ فعالیتی ثبت نشده است.")

    st.divider()
    if st.button("🚪 خروج"):
        st.session_state.clear()
        st.rerun()

# -----------------------------
# استایل مخصوص موبایل
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
