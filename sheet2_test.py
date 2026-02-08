import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Ubitmymoney", layout="wide")

# --- 2. LOGIC: ระบบจัดการฐานข้อมูลภายใน (ปรับให้รองรับ Cloud Path) ---
# ใช้คำสั่งนี้เพื่อให้โปรแกรมหาไฟล์ data.csv เจอในทุกสภาพแวดล้อม
current_dir = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(current_dir, "data.csv")

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            if not df.empty:
                # แก้ปัญหาการประมวลผลวันที่: แปลงและเรียงลำดับจากเก่าไปใหม่
                df['dt_temp'] = pd.to_datetime(df['วัน/เดือน/ปี'], format="%d/%m/%Y", dayfirst=True, errors='coerce')
                df = df.dropna(subset=['dt_temp']) # ลบแถวที่วันที่ผิดพลาดป้องกันกราฟพัง
                df = df.sort_values(by='dt_temp').reset_index(drop=True)
                df = df.drop(columns=['dt_temp'])
            return df
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการอ่านไฟล์: {e}")
            return pd.DataFrame(columns=['ที่อยู่อีเมล', 'วัน/เดือน/ปี', 'รายรับ', 'รายจ่าย'])
    else:
        df = pd.DataFrame(columns=['ที่อยู่อีเมล', 'วัน/เดือน/ปี', 'รายรับ', 'รายจ่าย'])
        df.to_csv(DB_FILE, index=False)
        return df

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- 3. ส่วนแสดงผลหลัก ---
st.sidebar.title("🔐 เข้าสู่ระบบ")
user_email = st.sidebar.text_input("กรอก Email ของคุณ:", placeholder="example@gmail.com").strip()

if not user_email:
    st.title("💰 Ubitmymoney")
    st.info("👈 กรุณากรอก Email ที่แถบด้านซ้ายเพื่อเข้าใช้งาน")
else:
    all_data = load_data()
    user_data = all_data[all_data['ที่อยู่อีเมล'] == user_email].copy()
    
    st.title(f"📊 รายงานสรุปของ: {user_email}")

    # --- 4. ฟอร์มบันทึกข้อมูล ---
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
                updated_all = pd.concat([all_data, new_row], ignore_index=True)
                save_data(updated_all)
                st.success("บันทึกข้อมูลแล้ว!")
                st.rerun()

    # --- 5. การประมวลผลกราฟและสถิติ ---
    if not user_data.empty:
        c1, c2, c3 = st.columns(3)
        total_inc = user_data['รายรับ'].sum()
        total_exp = user_data['รายจ่าย'].sum()
        c1.metric("รายรับรวม", f"{total_inc:,.2f} ฿")
        c2.metric("รายจ่ายรวม", f"{total_exp:,.2f} ฿")
        c3.metric("คงเหลือสุทธิ", f"{(total_inc - total_exp):,.2f} ฿")

        st.subheader("📈 แนวโน้มการเงิน")
        # ใช้มาร์กเกอร์และเส้นที่ชัดเจน
        fig = px.line(user_data, x='วัน/เดือน/ปี', y=['รายรับ', 'รายจ่าย'], 
                      markers=True, title="กราฟรายรับ-รายจ่าย")
        fig.update_xaxes(type='category') # บังคับให้เรียงตามลำดับข้อมูลที่เรา Sort ไว้
        st.plotly_chart(fig, use_container_width=True)

        # --- 6. รายการและการลบ ---
        st.subheader("📝 รายการทั้งหมด")
        for index, row in user_data.iterrows():
            col_t, col_b = st.columns([0.8, 0.2])
            col_t.text(f"📅 {row['วัน/เดือน/ปี']} | +{row['รายรับ']} | -{row['รายจ่าย']}")
            if col_b.button("🗑️ ลบ", key=f"del_{index}"):
                all_data = all_data.drop(index)
                save_data(all_data)
                st.rerun()
    else:
        st.warning("ยังไม่มีข้อมูลบันทึกในระบบ")
        # ส่วนการเลือกหมวดหมู่เพื่อแสดงกราฟแยก
all_categories = user_data['หมวดหมู่'].unique()
selected_cat = st.selectbox("เลือกหมวดหมู่ที่ต้องการดู:", all_categories)

# กรองข้อมูลตามหมวดหมู่ที่เลือก
filtered_data = user_data[user_data['หมวดหมู่'] == selected_cat]

# วาดกราฟแยกตามหมวดหมู่
fig = px.line(filtered_data, x='วัน/เดือน/ปี', y=['รายรับ', 'รายจ่าย'], 
              title=f"กราฟสรุปในหมวดหมู่: {selected_cat}", markers=True)
st.plotly_chart(fig, use_container_width=True)