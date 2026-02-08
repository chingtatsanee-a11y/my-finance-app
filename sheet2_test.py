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
        # ตรวจสอบคอลัมน์หมวดหมู่เพื่อป้องกัน Error
        if 'หมวดหมู่' not in df.columns:
            df['หมวดหมู่'] = 'ทั่วไป'
        
        if not df.empty:
            df['dt_temp'] = pd.to_datetime(df['วัน/เดือน/ปี'], format="%d/%m/%Y", dayfirst=True, errors='coerce')
            df = df.dropna(subset=['dt_temp']).sort_values(by='dt_temp').reset_index(drop=True)
            df = df.drop(columns=['dt_temp'])
        return df
    else:
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

    # --- ฟอร์มบันทึกข้อมูล (เปลี่ยนเป็นช่องพิมพ์หมวดหมู่เอง) ---
    with st.expander("➕ บันทึกรายการใหม่"):
        with st.form("input_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            d = col1.date_input("วันที่", datetime.now())
            
            # เปลี่ยนจาก selectbox เป็น text_input เพื่อให้พิมพ์เองได้ตามใจชอบ
            cat = col2.text_input("ระบุหมวดหมู่ (เช่น ค่ากาแฟ, ของใช้, เงินเดือน):", placeholder="พิมพ์หมวดหมู่ที่นี่").strip()
            
            col3, col4 = st.columns(2)
            inc = col3.number_input("รายรับ (บาท)", min_value=0.0, step=100.0)
            exp = col4.number_input("รายจ่าย (บาท)", min_value=0.0, step=100.0)
            
            if st.form_submit_button("บันทึกข้อมูล"):
                if not cat: # ป้องกันกรณีลืมพิมพ์หมวดหมู่
                    cat = "ทั่วไป"
                
                new_row = pd.DataFrame([{
                    "ที่อยู่อีเมล": user_email,
                    "วัน/เดือน/ปี": d.strftime("%d/%m/%Y"),
                    "หมวดหมู่": cat,
                    "รายรับ": inc,
                    "รายจ่าย": exp
                }])
                updated_all = pd.concat([all_data, new_row], ignore_index=True)
                save_data(updated_all)
                st.success(f"บันทึกหมวดหมู่ '{cat}' เรียบร้อย!")
                st.rerun()

    # --- ส่วนการแสดงผลแยกกราฟ ---
    if not user_data.empty:
        st.subheader("📈 วิเคราะห์แยกตามหมวดหมู่ที่คุณสร้าง")
        
        # ดึงหมวดหมู่ทั้งหมดที่ผู้ใช้คนนี้เคยพิมพ์ไว้มาสร้างตัวเลือกในกราฟ
        user_categories = user_data['หมวดหมู่'].unique()
        selected_cat = st.selectbox("เลือกหมวดหมู่ที่ต้องการดูแนวโน้ม:", user_categories)
        
        # กรองข้อมูลและประมวลผลกราฟ
        cat_df = user_data[user_data['หมวดหมู่'] == selected_cat]
        
        fig = px.line(cat_df, x='วัน/เดือน/ปี', y=['รายรับ', 'รายจ่าย'], 
                      markers=True, title=f"ประวัติการเงินหมวด: {selected_cat}",
                      color_discrete_map={"รายรับ": "#2ECC71", "รายจ่าย": "#E74C3C"})
        
        fig.update_xaxes(type='category')
        st.plotly_chart(fig, use_container_width=True)

        # รายการตารางข้อมูล
        with st.expander("ดูรายการทั้งหมด"):
            st.dataframe(user_data[['วัน/เดือน/ปี', 'หมวดหมู่', 'รายรับ', 'รายจ่าย']], use_container_width=True)
    else:
        st.info("พิมพ์หมวดหมู่และบันทึกข้อมูลแรกเพื่อเริ่มสร้างกราฟส่วนตัว")

else:
    st.title("💰 Ubitmymoney")
    st.warning("👈 โปรดระบุ Email เพื่อดึงข้อมูลหมวดหมู่ส่วนตัวของคุณ")