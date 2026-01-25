import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="ระบบบันทึกและสรุปรายส่วนบุคคล", layout="wide")

# --- 2. ระบุ ID ของ Sheet ---
SHEET_ID = "1pbabW16fVD0d731BDvIHZpq_5z8vp0vGJTjEKt8jxkc"

# --- 3. ฟังก์ชันดึงข้อมูล ---
@st.cache_data(ttl=10) # รีเฟรชข้อมูลทุก 10 วินาทีเพื่อให้เห็นข้อมูลใหม่ที่เพิ่งกรอก
def load_data(sheet_id):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

# --- 4. ส่วนของ Sidebar (Login) ---
st.sidebar.title("🔐 เข้าสู่ระบบ")
user_email = st.sidebar.text_input("กรอก Email ของคุณ:", placeholder="example@gmail.com").strip()

if user_email:
    try:
        df_raw = load_data(SHEET_ID)
        email_col = 'ที่อยู่อีเมล'
        
        # ตรวจสอบว่ามี Email นี้ในระบบหรือไม่
        if user_email in df_raw[email_col].values:
            df_user = df_raw[df_raw[email_col] == user_email].copy()
            
            # แปลงค่าตัวเลข
            df_user['รายรับ'] = pd.to_numeric(df_user['รายรับ'], errors='coerce').fillna(0)
            df_user['รายจ่าย'] = pd.to_numeric(df_user['รายจ่าย'], errors='coerce').fillna(0)

            # --- 5. ส่วนของการแสดงผล (Dashboard) ---
            st.title(f"📊 รายงานสรุปของคุณ: {user_email}")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("รายรับเฉลี่ย", f"{df_user['รายรับ'].mean():,.2f} บาท")
            col2.metric("รายจ่ายเฉลี่ย", f"{df_user['รายจ่าย'].mean():,.2f} บาท")
            col3.metric("เงินคงเหลือรวม", f"{(df_user['รายรับ'].sum() - df_user['รายจ่าย'].sum()):,.2f} บาท")

            # กราฟเส้นส่วนตัว
            fig = px.line(df_user, x='วัน/เดือน/ปี', y=['รายรับ', 'รายจ่าย'],
                          markers=True, title="แนวโน้มรายรับ-รายจ่ายของคุณ")
            st.plotly_chart(fig, use_container_width=True)

            # --- 6. ส่วนของฟอร์มกรอกข้อมูล (เพิ่มข้อมูลใหม่) ---
            st.divider()
            st.subheader("📝 บันทึกรายรับ-รายจ่ายใหม่")
            with st.form("my_form", clear_on_submit=True):
                date_input = st.date_input("วันที่", datetime.now())
                income_input = st.number_input("จำนวนรายรับ (บาท)", min_value=0.0)
                expense_input = st.number_input("จำนวนรายจ่าย (บาท)", min_value=0.0)
                submit_button = st.form_submit_button("บันทึกข้อมูล")

                if submit_button:
                    st.info("💡 สำหรับการบันทึกข้อมูลเข้า Google Sheet อัตโนมัติ จำเป็นต้องใช้ระบบ Google Forms หรือ Google Apps Script ในการรับค่า (สามารถสอบถามวิธีทำต่อได้ครับ)")

        else:
            st.error(f"❌ ไม่พบข้อมูลสำหรับ Email: {user_email}")
            
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
else:
    st.title("💰 Ubitmymoney")
    st.warning("👈 กรุณาระบุ Email ที่แถบด้านซ้ายเพื่อดูข้อมูลของคุณ")