import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Ubitmymoney", layout="wide")

DB_FILE = "data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
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

# --- 2. ส่วนระบุตัวตน ---
st.sidebar.title("🔐 เข้าสู่ระบบ")
user_email = st.sidebar.text_input("กรอก Email ของคุณ:").strip()

if user_email:
    all_data = load_data()
    user_data = all_data[all_data['ที่อยู่อีเมล'] == user_email].copy()
    
    st.title(f"📊 รายงานสรุปของ: {user_email}")

    # --- 3. ยอดรวมสุทธิ (ภาพรวมทั้งหมด) ---
    if not user_data.empty:
        with st.container():
            st.subheader("🏦 ยอดรวมภาพรวม (ทุกหมวดหมู่)")
            c1, c2, c3 = st.columns(3)
            c1.metric("รายรับรวมทั้งหมด", f"{user_data['รายรับ'].sum():,.2f} ฿")
            c2.metric("รายจ่ายรวมทั้งหมด", f"{user_data['รายจ่าย'].sum():,.2f} ฿")
            c3.metric("คงเหลือสุทธิทั้งหมด", f"{(user_data['รายรับ'].sum() - user_data['รายจ่าย'].sum()):,.2f} ฿")
        st.divider()

    # --- 4. ฟอร์มบันทึกรายการ (พิมพ์หมวดหมู่เองได้) ---
    with st.expander("➕ บันทึกรายการใหม่"):
        with st.form("input_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            d = col1.date_input("วันที่", datetime.now())
            cat = col2.text_input("ระบุหมวดหมู่ (เช่น อาหาร, เดินทาง):").strip()
            
            col3, col4 = st.columns(2)
            inc = col3.number_input("รายรับ (บาท)", min_value=0.0, step=100.0)
            exp = col4.number_input("รายจ่าย (บาท)", min_value=0.0, step=100.0)
            
            if st.form_submit_button("บันทึกข้อมูล"):
                if not cat: cat = "ทั่วไป"
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

    # --- 5. ส่วนแยกตามหมวดหมู่ (Highlight) ---
    if not user_data.empty:
        st.subheader("📈 วิเคราะห์รายหมวดหมู่")
        user_categories = user_data['หมวดหมู่'].unique()
        selected_cat = st.selectbox("เลือกหมวดหมู่ที่ต้องการดูข้อมูลแยก:", user_categories)
        
        # กรองข้อมูลหมวดหมู่ที่เลือก
        cat_df = user_data[user_data['หมวดหมู่'] == selected_cat]
        
        # --- ยอดสรุปเฉพาะหมวดหมู่ที่เลือก ---
        st.info(f"💰 สรุปยอดเฉพาะหมวด: **{selected_cat}**")
        m1, m2, m3 = st.columns(3)
        cat_inc = cat_df['รายรับ'].sum()
        cat_exp = cat_df['รายจ่าย'].sum()
        m1.metric(f"รับ ({selected_cat})", f"{cat_inc:,.2f} ฿")
        m2.metric(f"จ่าย ({selected_cat})", f"{cat_exp:,.2f} ฿")
        m3.metric(f"คงเหลือ ({selected_cat})", f"{(cat_inc - cat_exp):,.2f} ฿")

        # วาดกราฟของหมวดหมู่ที่เลือก
        fig = px.line(cat_df, x='วัน/เดือน/ปี', y=['รายรับ', 'รายจ่าย'], 
                      markers=True, title=f"ประวัติการเงินหมวด: {selected_cat}")
        fig.update_xaxes(type='category')
        st.plotly_chart(fig, use_container_width=True)

        # --- 6. รายการทั้งหมดและปุ่มลบ ---
        st.subheader("📝 รายการข้อมูลทั้งหมดของคุณ")
        for index, row in user_data.iterrows():
            col_text, col_btn = st.columns([0.85, 0.15])
            with col_text:
                st.write(f"📅 **{row['วัน/เดือน/ปี']}** | 📂 {row['หมวดหมู่']} | ➕ รับ: {row['รายรับ']:,.2f} | ➖ จ่าย: {row['รายจ่าย']:,.2f}")
            
            if col_btn.button("🗑️ ลบ", key=f"del_{index}"):
                all_data = all_data.drop(index)
                save_data(all_data)
                st.rerun()
            st.divider()
    else:
        st.info("👈 เริ่มบันทึกข้อมูลแรกได้ที่เมนูด้านบนครับ")

else:
    st.title("💰 Ubitmymoney")
    st.info("👈 กรุณากรอก Email ที่แถบด้านซ้ายเพื่อเข้าสู่ระบบ")