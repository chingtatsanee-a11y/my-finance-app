import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Ubitmymoney", layout="wide")

DB_FILE = "data.csv"

# --- 2. ระบบสลับภาษา (Dictionary) ---
languages = {
    "ไทย": {
        "login": "🔐 เข้าสู่ระบบ",
        "email_label": "กรอก Email ของคุณ:",
        "main_title": "📊 รายงานสรุปของ:",
        "total_overview": "🏦 ยอดรวมภาพรวม (ทุกหมวดหมู่)",
        "inc_total": "รายรับรวมทั้งหมด",
        "exp_total": "รายจ่ายรวมทั้งหมด",
        "bal_total": "คงเหลือสุทธิทั้งหมด",
        "new_entry": "➕ บันทึกรายการใหม่",
        "date": "วันที่",
        "category": "ระบุหมวดหมู่ (เช่น อาหาร, เดินทาง):",
        "income": "รายรับ (บาท)",
        "expense": "รายจ่าย (บาท)",
        "save": "บันทึกข้อมูล",
        "cat_analysis": "📈 วิเคราะห์รายหมวดหมู่",
        "select_cat": "เลือกหมวดหมู่ที่ต้องการดูข้อมูลแยก:",
        "cat_summary": "💰 สรุปยอดเฉพาะหมวด:",
        "history": "📝 รายการข้อมูลทั้งหมดของคุณ",
        "delete": "🗑️ ลบ"
    },
    "English": {
        "login": "🔐 Login",
        "email_label": "Enter your Email:",
        "main_title": "📊 Summary Report for:",
        "total_overview": "🏦 Overall Summary (All Categories)",
        "inc_total": "Total Income",
        "exp_total": "Total Expense",
        "bal_total": "Net Balance",
        "new_entry": "➕ Add New Entry",
        "date": "Date",
        "category": "Category (e.g., Food, Travel):",
        "income": "Income (Baht)",
        "expense": "Expense (Baht)",
        "save": "Save Data",
        "cat_analysis": "📈 Category Analysis",
        "select_cat": "Select category to view data:",
        "cat_summary": "💰 Summary for Category:",
        "history": "📝 Your Transaction History",
        "delete": "🗑️ Delete"
    }
}

# ส่วนเลือกภาษาที่ Sidebar
lang_choice = st.sidebar.selectbox("🌐 ภาษา / Language", ["ไทย", "English"])
text = languages[lang_choice]

# --- 3. LOGIC: จัดการข้อมูล ---
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

# --- 4. หน้าจอหลัก ---
st.sidebar.divider()
st.sidebar.title(text["login"])
user_email = st.sidebar.text_input(text["email_label"]).strip()

if user_email:
    all_data = load_data()
    user_data = all_data[all_data['ที่อยู่อีเมล'] == user_email].copy()
    
    st.title(f"{text['main_title']} {user_email}")

    # ยอดรวมภาพรวม
    if not user_data.empty:
        st.subheader(text["total_overview"])
        c1, c2, c3 = st.columns(3)
        total_inc = user_data['รายรับ'].sum()
        total_exp = user_data['รายจ่าย'].sum()
        c1.metric(text["inc_total"], f"{total_inc:,.2f} ฿")
        c2.metric(text["exp_total"], f"{total_exp:,.2f} ฿")
        c3.metric(text["bal_total"], f"{(total_inc - total_exp):,.2f} ฿")
        st.divider()

    # ฟอร์มบันทึกรายการ
    with st.expander(text["new_entry"]):
        with st.form("input_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            d = col1.date_input(text["date"], datetime.now())
            cat = col2.text_input(text["category"]).strip()
            
            col3, col4 = st.columns(2)
            inc = col3.number_input(text["income"], min_value=0.0, step=100.0)
            exp = col4.number_input(text["expense"], min_value=0.0, step=100.0)
            
            if st.form_submit_button(text["save"]):
                if not cat: cat = "General" if lang_choice == "English" else "ทั่วไป"
                new_row = pd.DataFrame([{
                    "ที่อยู่อีเมล": user_email,
                    "วัน/เดือน/ปี": d.strftime("%d/%m/%Y"),
                    "หมวดหมู่": cat,
                    "รายรับ": inc,
                    "รายจ่าย": exp
                }])
                updated_all = pd.concat([all_data, new_row], ignore_index=True)
                save_data(updated_all)
                st.rerun()

    # ส่วนวิเคราะห์รายหมวดหมู่
    if not user_data.empty:
        st.subheader(text["cat_analysis"])
        user_cats = user_data['หมวดหมู่'].unique()
        selected_cat = st.selectbox(text["select_cat"], user_cats)
        
        cat_df = user_data[user_data['หมวดหมู่'] == selected_cat]
        
        # ยอดสรุปเฉพาะหมวด
        st.info(f"{text['cat_summary']} **{selected_cat}**")
        m1, m2, m3 = st.columns(3)
        cat_inc, cat_exp = cat_df['รายรับ'].sum(), cat_df['รายจ่าย'].sum()
        m1.metric(f"{text['income']} ({selected_cat})", f"{cat_inc:,.2f} ฿")
        m2.metric(f"{text['expense']} ({selected_cat})", f"{cat_exp:,.2f} ฿")
        m3.metric(f"{text['bal_total']} ({selected_cat})", f"{(cat_inc - cat_exp):,.2f} ฿")

        fig = px.line(cat_df, x='วัน/เดือน/ปี', y=['รายรับ', 'รายจ่าย'], 
                      markers=True, title=f"{selected_cat} History")
        fig.update_xaxes(type='category')
        st.plotly_chart(fig, use_container_width=True)

        # รายการย้อนหลังและปุ่มลบ
        st.subheader(text["history"])
        for index, row in user_data.iterrows():
            col_text, col_btn = st.columns([0.85, 0.15])
            with col_text:
                st.write(f"📅 **{row['วัน/เดือน/ปี']}** | 📂 {row['หมวดหมู่']} | ➕ {row['รายรับ']:,.2f} | ➖ {row['รายจ่าย']:,.2f}")
            if col_btn.button(text["delete"], key=f"del_{index}"):
                all_data = all_data.drop(index)
                save_data(all_data)
                st.rerun()
            st.divider()
else:
    st.title("💰 UBITMYMONEY")
    st.info("👈 Please Login / กรุณาเข้าสู่ระบบ")