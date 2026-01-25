import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Standalone Finance Dashboard", layout="wide")

# --- 2. LOGIC: ระบบจัดการฐานข้อมูลภายใน ---
DB_FILE = "data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        
        # LOGIC สำคัญ: จัดการวันที่ให้เรียงลำดับถูกต้อง
        # แปลงข้อความวันที่ให้เป็นรูปแบบ Datetime เพื่อใช้ในการเรียงลำดับ
        df['dt_temp'] = pd.to_datetime(df['วัน/เดือน/ปี'], format="%d/%m/%Y", dayfirst=True)
        
        # เรียงข้อมูลตามวันที่จากน้อยไปมาก (เก่าไปใหม่)
        df = df.sort_values(by='dt_temp').reset_index(drop=True)
        
        # ลบคอลัมน์ชั่วคราวออก
        df = df.drop(columns=['dt_temp'])
        return df
    else:
        # สร้างตารางเปล่าหากยังไม่มีไฟล์
        df = pd.DataFrame(columns=['ที่อยู่อีเมล', 'วัน/เดือน/ปี', 'รายรับ', 'รายจ่าย'])
        df.to_csv(DB_FILE, index=False)
        return df

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- 3. ระบบระบุตัวตน (Login) ---
st.sidebar.title("🔐 เข้าสู่ระบบ")
user_email = st.sidebar.text_input("กรอก Email ของคุณ:", placeholder="example@gmail.com").strip()

if user_email:
    all_data = load_data()
    # กรองข้อมูลเฉพาะของ User ที่ Login
    user_data = all_data[all_data['ที่อยู่อีเมล'] == user_email].copy()
    
    st.title(f"📊 รายงานสรุปของ: {user_email}")

    # --- 4. LOGIC: การเพิ่มข้อมูลใหม่ (ป้องกันการ Reset ค่า) ---
    with st.expander("➕ บันทึกรายการใหม่"):
        with st.form("input_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            d = col1.date_input("วันที่", datetime.now())
            inc = col2.number_input("รายรับ (บาท)", min_value=0.0, step=100.0)
            exp = col3.number_input("รายจ่าย (บาท)", min_value=0.0, step=100.0)
            
            if st.form_submit_button("บันทึกข้อมูล"):
                new_row = pd.DataFrame([{
                    "ที่อยู่อีเมล": user_email,
                    "วัน/เดือน/ปี": d.strftime("%d/%m/%Y"),
                    "รายรับ": inc,
                    "รายจ่าย": exp
                }])
                # รวมข้อมูลและบันทึก
                updated_all = pd.concat([all_data, new_row], ignore_index=True)
                save_data(updated_all)
                st.success("✅ บันทึกข้อมูลเรียบร้อย!")
                st.rerun()

    # --- 5. การประมวลผลและแสดงผลกราฟ ---
    if not user_data.empty:
        # ส่วนสรุปยอดเงิน
        c1, c2, c3 = st.columns(3)
        total_inc = user_data['รายรับ'].sum()
        total_exp = user_data['รายจ่าย'].sum()
        c1.metric("รายรับรวม", f"{total_inc:,.2f} ฿")
        c2.metric("รายจ่ายรวม", f"{total_exp:,.2f} ฿")
        c3.metric("คงเหลือสุทธิ", f"{(total_inc - total_exp):,.2f} ฿")

        # กราฟเส้นที่เรียงวันที่ถูกต้องแล้ว (ซ้ายไปขวา)
        st.subheader("📈 แนวโน้มการเงินส่วนบุคคล")
        fig = px.line(user_data, x='วัน/เดือน/ปี', y=['รายรับ', 'รายจ่าย'], 
                      markers=True, title=f"ประวัติการเงินของ {user_email}")
        
        # ปรับแต่งให้แกน X เรียงตามลำดับข้อมูลที่ Sort มาแล้ว
        fig.update_xaxes(type='category') 
        st.plotly_chart(fig, use_container_width=True)

        # --- 6. LOGIC: การลบข้อมูล ---
        st.subheader("📝 รายการข้อมูลของคุณ")
        for index, row in user_data.iterrows():
            col_text, col_btn = st.columns([0.85, 0.15])
            col_text.text(f"📅 {row['วัน/เดือน/ปี']} | ➕ {row['รายรับ']:,.2f} | ➖ {row['รายจ่าย']:,.2f}")
            if col_btn.button("🗑️ ลบ", key=f"del_{index}"):
                all_data = all_data.drop(index)
                save_data(all_data)
                st.rerun()
            st.divider()

    else:
        st.info("👋 ยังไม่มีข้อมูลในระบบ เริ่มบันทึกรายการแรกได้ที่ปุ่มด้านบนครับ")

else:
    st.title("💰 Ubitmymoney")
    st.info("👈 กรุณากรอก Email เพื่อเข้าถึงฐานข้อมูลส่วนตัวของคุณ")