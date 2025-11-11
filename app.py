import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Newspaper Payroll", page_icon="🗞️", layout="wide")
st.title("🗞️ Newspaper Payroll – Data Entry")

st.markdown("""
در این برنامه می‌توانید اطلاعات نیروها، ویک‌ها، برنامه کاری و تعطیلات را وارد کنید.
سپس با زدن دکمه **محاسبه حقوق**، حقوق هر نیرو بر اساس روزهای کاری محاسبه می‌شود.
""")

# --- Form 1: Users ---
st.header("1️⃣ کاربران (Users)")
st.markdown("برای افزودن یا حذف نیرو، جدول زیر را ویرایش کنید:")

users_df = st.data_editor(
    pd.DataFrame([{"user_id": "USER1", "name": "Ali"}]),
    num_rows="dynamic",
    use_container_width=True,
)

# --- Form 2: Wijks ---
st.header("2️⃣ ویک‌ها (Wijks)")
st.markdown("هر ویک می‌تواند نرخ ثابت یا نرخ بر اساس سگمنت داشته باشد:")

wijk_df = st.data_editor(
    pd.DataFrame([
        {"wijk": "Rijen3", "price_type": "flat", "flat_daily_price": 50, "segments": 4, "segment_prices": ""},
        {"wijk": "Baarle 5", "price_type": "by_segment", "flat_daily_price": "", "segments": 3, "segment_prices": "[12,10,8]"},
    ]),
    num_rows="dynamic",
    use_container_width=True,
)

# --- Form 3: Schedule ---
st.header("3️⃣ برنامه کاری (Schedule)")
st.markdown("برای هر نیرو بازه تاریخی و ویک مربوطه را وارد کنید:")

schedule_df = st.data_editor(
    pd.DataFrame([
        {"user_id": "USER1", "start_date": "2025-11-06", "end_date": "2025-11-10", "wijk": "Rijen3"},
        {"user_id": "USER1", "start_date": "2025-11-11", "end_date": "2025-11-23", "wijk": "Baarle 5"},
    ]),
    num_rows="dynamic",
    use_container_width=True,
)

# --- Form 4: Holidays ---
st.header("4️⃣ تعطیلات (Holidays)")
st.markdown("در صورت وجود تعطیلات رسمی، تاریخ آن‌ها را اضافه کنید:")

holidays_df = st.data_editor(
    pd.DataFrame([{"date": ""}]),
    num_rows="dynamic",
    use_container_width=True,
)

# --- Form 5: Month/Year ---
st.header("5️⃣ انتخاب ماه و سال محاسبه")
col1, col2 = st.columns(2)
with col1:
    year = st.number_input("سال", min_value=2020, max_value=2100, value=2025)
with col2:
    month = st.number_input("ماه", min_value=1, max_value=12, value=11)

st.markdown("---")
if st.button("📊 محاسبه حقوق (فعلاً آزمایشی)"):
    st.success(f"داده‌ها ثبت شدند برای ماه {year}-{month:02d}. در مرحله بعد محاسبه افزوده می‌شود.")
    st.write("**Users:**", users_df)
    st.write("**Wijks:**", wijk_df)
    st.write("**Schedule:**", schedule_df)
    st.write("**Holidays:**", holidays_df)
