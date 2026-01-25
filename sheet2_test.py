import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Personal Finance Standalone", layout="wide")

# --- 2. LOGIC: การจัดการไฟล์ข้อมูล ---
DB_FILE = "data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
    else:
        # สร้างตารางเปล่าพร้อมชื่อคอลัมน์
        df = pd.DataFrame(columns=['ที่อยู่อีเมล', 'วัน/เดือน/ปี', 'รายรับ', 'รายจ่าย'])
        df.to_csv(DB_FILE, index=False)
    return df

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- 3. ระบบระบุตัวตน ---
st.sidebar.title("🔐 เข้าสู่ระบบ")
user_email = st.sidebar.text_input("กรอก Email ของคุณ:").strip()

if user_email:
    all_data = load_data()
    # กรองข้อมูลเฉพาะของ User (เพื่อนำไปใช้คำนวณและวาดกราฟ)
    user_data = all_data[all_data['ที่อยู่อีเมล'] == user_email].copy()
    
    st.title(f"📊 รายงานสรุปของ: {user_email}")

    # --- 4. LOGIC: การเพิ่มข้อมูล ---
    with st.expander("➕ บันทึกรายการใหม่"):
        with st.form("input_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            d = col1.date_input("วันที่", datetime.now())
            inc = col2.number_input("รายรับ (บาท)", min_value=0.0)
            exp = col3.number_input("รายจ่าย (บาท)", min_value=0.0)
            
            if st.form_submit_button("บันทึกข้อมูล"):
                new_row = pd.DataFrame([{
                    "ที่อยู่อีเมล": user_email,
                    "วัน/เดือน/ปี": d.strftime("%d/%m/%Y"),
                    "รายรับ": inc,
                    "รายจ่าย": exp
                }])
                updated_all = pd.concat([all_data, new_row], ignore_index=True)
                save_data(updated_all)
                st.success("บันทึกสำเร็จ!")
                st.rerun()

    # --- 5. LOGIC: การแสดงผลและการลบข้อมูล ---
    if not user_data.empty:
        # ส่วนสรุปยอดเงิน
        c1, c2, c3 = st.columns(3)
        c1.metric("รายรับรวม", f"{user_data['รายรับ'].sum():,.2f}")
        c2.metric("รายจ่ายรวม", f"{user_data['รายจ่าย'].sum():,.2f}")
        c3.metric("คงเหลือ", f"{(user_data['รายรับ'].sum() - user_data['รายจ่าย'].sum()):,.2f}")

        # กราฟเส้น
        fig = px.line(user_data, x='วัน/เดือน/ปี', y=['รายรับ', 'รายจ่าย'], markers=True)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📝 ประวัติและรายการข้อมูล")
        
        # --- 6. LOGIC: การลบข้อมูลทีละแถว ---
        # สร้าง Loop เพื่อแสดงข้อมูลแต่ละแถวพร้อมปุ่มลบ
        for index, row in user_data.iterrows():
            col_info, col_del = st.columns([0.9, 0.1])
            with col_info:
                st.text(f"📅 {row['วัน/เดือน/ปี']} | ➕ {row['รายรับ']} | ➖ {row['รายจ่าย']}")
            with col_del:
                # ใช้ Index ของ DataFrame ทั้งหมด (all_data) เป็นกุญแจในการลบ
                if st.button("🗑️", key=f"del_{index}"):
                    # ลบแถวที่ตรงกับ index นั้นออกจาก all_data
                    all_data = all_data.drop(index)
                    save_data(all_data)
                    st.warning("ลบรายการแล้ว")
                    st.rerun()
            st.divider()

    else:
        st.info("ยังไม่มีข้อมูลในระบบ")

else:
    st.title("💰 Ubitmymoney")
    st.info("👈 กรุณากรอก Email เพื่อเข้าใช้งาน")

