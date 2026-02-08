import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# --- การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Ubitmymoney", layout="wide")

DB_FILE = "data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        # แก้ปัญหา KeyError: ตรวจสอบว่ามีคอลัมน์ 'หมวดหมู่' หรือยัง ถ้าไม่มีให้สร้างขึ้นมา
        if 'หมวดหมู่' not in df.columns:
            df['หมวดหมู่'] = 'ทั่วไป'
        
        if not df.empty:
            df['dt_temp'] = pd.to_datetime(df['วัน/เดือน/ปี'], format="%d/%m/%Y", dayfirst=True, errors='coerce')
            df = df.dropna(subset=['dt_temp']).sort_values(by='dt_temp').reset_index(drop=True)
            df = df.drop(columns=['dt_temp'])
        return df
    else:
        # สร้าง Header เริ่มต้นรวมหมวดหมู่เข้าไปด้วย
        df = pd.DataFrame(columns=['ที่อยู่อีเมล', 'วัน/เดือน/ปี', 'หมวดหมู่', 'รายรับ', 'รายจ่าย'])
        df.to_csv(DB_FILE, index=False)
        return df

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- ส่วน Login ---
st.sidebar.title("🔐 เข้าสู่ระบบ")
user_email = st.sidebar.text_input("กรอก Email ของคุณ:").strip()

if user_email:
    all_data = load_data()
    user_data = all_data[all_data['ที่อยู่อีเมล'] == user_email].copy()
    
    st.title(f"📊 รายงานของ: {user_email}")

    # --- ฟอร์มบันทึกข้อมูล (เพิ่มช่องเลือกหมวดหมู่) ---
    with st.expander("➕ บันทึกรายการใหม่"):
        with st.form("input_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            d = col1.date_input("วันที่", datetime.now())
            # ให้ผู้ใช้พิมพ์หรือเลือกหมวดหมู่
            cat = col2.selectbox("หมวดหมู่", ["อาหาร", "เดินทาง", "ที่พัก", "ช้อปปิ้ง", "อื่นๆ"])
            
            col3, col4 = st.columns(2)
            inc = col3.number_input("รายรับ (บาท)", min_value=0.0)
            exp = col4.number_input("รายจ่าย (บาท)", min_value=0.0)
            
            if st.form_submit_button("บันทึกข้อมูล"):
                new_row = pd.DataFrame([{
                    "ที่อยู่อีเมล": user_email,
                    "วัน/เดือน/ปี": d.strftime("%d/%m/%Y"),
                    "หมวดหมู่": cat,
                    "รายรับ": inc,
                    "รายจ่าย": exp
                }])
                updated_all = pd.concat([all_data, new_row], ignore_index=True)
                save_data(updated_all)
                st.success("บันทึกสำเร็จ!")
                st.rerun()

    # --- ส่วนการแยกกราฟตามหมวดหมู่ ---
    if not user_data.empty:
        st.subheader("📈 แยกกราฟตามหมวดหมู่")
        
        # ดึงรายชื่อหมวดหมู่ที่มีข้อมูลจริงมาสร้างตัวเลือก
        categories = user_data['หมวดหมู่'].unique()
        selected_cat = st.selectbox("เลือกหมวดหมู่ที่ต้องการดูข้อมูล:", categories)
        
        # กรองข้อมูลเฉพาะหมวดที่เลือก
        cat_df = user_data[user_data['หมวดหมู่'] == selected_cat]
        
        # วาดกราฟ
        fig = px.line(cat_df, x='วัน/เดือน/ปี', y=['รายรับ', 'รายจ่าย'], 
                      markers=True, title=f"แนวโน้มในหมวด: {selected_cat}")
        fig.update_xaxes(type='category')
        st.plotly_chart(fig, use_container_width=True)

        # รายการทั้งหมด
        st.subheader("📝 รายการทั้งหมด")
        for index, row in user_data.iterrows():
            st.write(f"📅 {row['วัน/เดือน/ปี']} | 📂 {row['หมวดหมู่']} | ➕ {row['รายรับ']} | ➖ {row['รายจ่าย']}")
            if st.button("ลบ", key=f"del_{index}"):
                all_data = all_data.drop(index)
                save_data(all_data)
                st.rerun()
    else:
        st.info("เริ่มบันทึกข้อมูลแรกเพื่อแสดงกราฟแยกหมวดหมู่")