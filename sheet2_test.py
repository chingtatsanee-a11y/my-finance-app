import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# --- 1. การตั้งค่าโครงสร้างเว็บ ---
st.set_page_config(page_title="Standalone Finance App", layout="wide")

# --- 2. LOGIC: ระบบจัดการไฟล์ข้อมูล (Database Logic) ---
DB_FILE = "data.csv"

def load_data():
    # ถ้ามีไฟล์อยู่แล้วให้อ่านไฟล์มาใช้ ถ้าไม่มีให้สร้างตารางเปล่าขึ้นมาใหม่
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
    else:
        df = pd.DataFrame(columns=['ที่อยู่อีเมล', 'วัน/เดือน/ปี', 'รายรับ', 'รายจ่าย'])
        df.to_csv(DB_FILE, index=False)
    return df

def save_data(new_df):
    # บันทึกข้อมูลทับลงในไฟล์ data.csv
    new_df.to_csv(DB_FILE, index=False)

# --- 3. ระบบระบุตัวตน (Login) ---
st.sidebar.title("🔐 เข้าสู่ระบบ")
user_email = st.sidebar.text_input("กรอก Email ของคุณ:").strip()

if user_email:
    # ดึงข้อมูลจากไฟล์ .csv
    all_data = load_data()
    
    # กรองข้อมูลเฉพาะของ User คนนั้น
    user_data = all_data[all_data['ที่อยู่อีเมล'] == user_email].copy()
    
    st.title(f"📊 รายงานสรุปของ: {user_email}")

    # --- 4. ส่วนของฟอร์มบันทึกข้อมูล (Add Logic) ---
    with st.expander("➕ บันทึกรายการใหม่"):
        with st.form("input_form", clear_on_submit=True):
            col_date, col_inc, col_exp = st.columns(3)
            d = col_date.date_input("วันที่", datetime.now())
            date_str = d.strftime("%d/%m/%Y")
            inc = col_inc.number_input("รายรับ (บาท)", min_value=0.0)
            exp = col_exp.number_input("รายจ่าย (บาท)", min_value=0.0)
            
            if st.form_submit_button("บันทึกข้อมูล"):
                # สร้างแถวใหม่
                new_row = pd.DataFrame([{
                    "ที่อยู่อีเมล": user_email,
                    "วัน/เดือน/ปี": date_str,
                    "รายรับ": inc,
                    "รายจ่าย": exp
                }])
                # รวมข้อมูลใหม่เข้ากับข้อมูลทั้งหมดแล้วบันทึกลงไฟล์
                updated_data = pd.concat([all_data, new_row], ignore_index=True)
                save_data(updated_data)
                
                st.success("บันทึกเรียบร้อย!")
                st.rerun() # รีเฟรชหน้าเว็บเพื่อให้กราฟอัปเดตทันที

    # --- 5. การประมวลผลและแสดงผล (Calculation Logic) ---
    if not user_data.empty:
        # คำนวณยอดเงิน
        inc_total = user_data['รายรับ'].sum()
        exp_total = user_data['รายจ่าย'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("รายรับสะสม", f"{inc_total:,.2f} ฿")
        c2.metric("รายจ่ายสะสม", f"{exp_total:,.2f} ฿")
        c3.metric("คงเหลือสุทธิ", f"{(inc_total - exp_total):,.2f} ฿")

        # กราฟเส้นแยกรายรับ-รายจ่าย
        st.subheader("📈 กราฟเส้นวิเคราะห์แนวโน้ม")
        fig = px.line(user_data, x='วัน/เดือน/ปี', y=['รายรับ', 'รายจ่าย'], 
                      markers=True, title=f"ประวัติการเงินของ {user_email}")
        st.plotly_chart(fig, use_container_width=True)
        
        # ตารางข้อมูล
        st.dataframe(user_data, use_container_width=True)
    else:
        st.info("👋 ยินดีต้อนรับ! คุณยังไม่มีข้อมูลในระบบ เริ่มบันทึกรายการแรกได้ที่ปุ่มด้านบนครับ")

else:
    st.title("💰 Ubiymymoney")
    st.info("👈 กรุณากรอก Email เพื่อเข้าถึงฐานข้อมูลส่วนตัวของคุณ")



