import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# --- 1. การตั้งค่าหน้าเว็บและธีม ---
st.set_page_config(page_title="Ubitmymoney 🌻", layout="wide")

# ตกแต่งส่วนหัวด้วยรูปดอกทานตะวัน
st.image("https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?q=80&w=2000&auto=format&fit=crop", 
         caption="🌻 Welcome to Ubitmymoney - Your Personal Financial Sunshine 🌻", use_container_width=True)

DB_FILE = "data.csv"

# --- 2. ระบบสลับภาษาและแปลหมวดหมู่แบบ Real-time ---
# Mapping สำหรับแปลหมวดหมู่ที่พิมพ์เอง
category_map = {
    "อาหาร": "Food", "เดินทาง": "Travel", "ที่พัก": "Housing",
    "ช้อปปิ้ง": "Shopping", "ทั่วไป": "General", "เงินเดือน": "Salary"
}
inv_category_map = {v: k for k, v in category_map.items()}

languages = {
    "ไทย": {
        "login": "🔐 เข้าสู่ระบบ",
        "email_label": "กรอก Email ของคุณ:",
        "main_title": "📊 รายงานสรุปของ:",
        "total_overview": "🏦 ยอดรวมภาพรวม (ทุกหมวดหมู่)",
        "inc_total": "รายรับรวม 🟢",
        "exp_total": "รายจ่ายรวม 🔴",
        "bal_total": "คงเหลือสุทธิ 💰",
        "new_entry": "🌻 บันทึกรายการใหม่",
        "date": "วันที่",
        "category": "ระบุหมวดหมู่ (พิมพ์เองได้):",
        "income": "รายรับ (฿)",
        "expense": "รายจ่าย (฿)",
        "save": "บันทึกข้อมูล 🌻",
        "cat_analysis": "📈 วิเคราะห์รายหมวดหมู่",
        "select_cat": "เลือกหมวดหมู่ที่ต้องการดู:",
        "cat_summary": "💰 ยอดสรุปหมวด:",
        "history": "📝 รายการทั้งหมดของคุณ",
        "delete": "🗑️ ลบ"
    },
    "English": {
        "login": "🔐 Login",
        "email_label": "Enter your Email:",
        "main_title": "📊 Summary for:",
        "total_overview": "🏦 Overall Overview",
        "inc_total": "Total Income 🟢",
        "exp_total": "Total Expense 🔴",
        "bal_total": "Net Balance 💰",
        "new_entry": "🌻 Add New Entry",
        "date": "Date",
        "category": "Enter Category:",
        "income": "Income (฿)",
        "expense": "Expense (฿)",
        "save": "Save Data 🌻",
        "cat_analysis": "📈 Category Analysis",
        "select_cat": "Select category to view:",
        "cat_summary": "💰 Summary for:",
        "history": "📝 Transaction History",
        "delete": "🗑️ Delete"
    }
}

lang_choice = st.sidebar.selectbox("🌐 Language / ภาษา", ["ไทย", "English"])
text = languages[lang_choice]

# ฟังก์ชันแปลชื่อหมวดหมู่
def translate_cat(cat_name, target_lang):
    if target_lang == "English":
        return category_map.get(cat_name, cat_name)
    else:
        return inv_category_map.get(cat_name, cat_name)

# --- 3. การจัดการข้อมูล ---
def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        if 'หมวดหมู่' not in df.columns: df['หมวดหมู่'] = 'ทั่วไป'
        if not df.empty:
            df['dt_temp'] = pd.to_datetime(df['วัน/เดือน/ปี'], format="%d/%m/%Y", dayfirst=True, errors='coerce')
            df = df.dropna(subset=['dt_temp']).sort_values(by='dt_temp').reset_index(drop=True)
            df = df.drop(columns=['dt_temp'])
        return df
    return pd.DataFrame(columns=['ที่อยู่อีเมล', 'วัน/เดือน/ปี', 'หมวดหมู่', 'รายรับ', 'รายจ่าย'])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- 4. หน้าจอหลัก ---
st.sidebar.divider()
st.sidebar.title(text["login"])
user_email = st.sidebar.text_input(text["email_label"]).strip()

if user_email:
    all_data = load_data()
    user_data = all_data[all_data['ที่อยู่อีเมล'] == user_email].copy()
    
    # แปลหมวดหมู่แบบ Real-time
    user_data['หมวดหมู่_display'] = user_data['หมวดหมู่'].apply(lambda x: translate_cat(x, lang_choice))

    st.title(f"{text['main_title']} {user_email}")

    # ยอดรวมภาพรวม
    if not user_data.empty:
        st.subheader(text["total_overview"])
        c1, c2, c3 = st.columns(3)
        t_inc, t_exp = user_data['รายรับ'].sum(), user_data['รายจ่าย'].sum()
        c1.metric(text["inc_total"], f"{t_inc:,.2f} ฿")
        c2.metric(text["exp_total"], f"{t_exp:,.2f} ฿")
        c3.metric(text["bal_total"], f"{(t_inc - t_exp):,.2f} ฿")
        st.divider()

    # ฟอร์มบันทึกรายการ (พิมพ์หมวดหมู่เอง)
    with st.expander(text["new_entry"]):
        with st.form("input_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            d = col1.date_input(text["date"], datetime.now())
            cat_input = col2.text_input(text["category"]).strip()
            
            col3, col4 = st.columns(2)
            inc = col3.number_input(text["income"], min_value=0.0)
            exp = col4.number_input(text["expense"], min_value=0.0)
            
            if st.form_submit_button(text["save"]):
                if not cat_input: cat_input = "ทั่วไป"
                # บันทึกเป็นภาษาไทยเพื่อความเป็นมาตรฐาน
                final_cat = inv_category_map.get(cat_input, cat_input) if lang_choice == "English" else cat_input
                new_row = pd.DataFrame([{"ที่อยู่อีเมล": user_email, "วัน/เดือน/ปี": d.strftime("%d/%m/%Y"), 
                                         "หมวดหมู่": final_cat, "รายรับ": inc, "รายจ่าย": exp}])
                updated_all = pd.concat([all_data, new_row], ignore_index=True)
                save_data(updated_all)
                st.rerun()

    # วิเคราะห์รายหมวดหมู่พร้อมยอดแยก
    if not user_data.empty:
        st.subheader(text["cat_analysis"])
        unique_cats = user_data['หมวดหมู่_display'].unique()
        selected_dis = st.selectbox(text["select_cat"], unique_cats)
        
        cat_df = user_data[user_data['หมวดหมู่_display'] == selected_dis]
        
        # ยอดสรุปเฉพาะหมวด
        st.info(f"🌻 {text['cat_summary']} **{selected_dis}**")
        m1, m2, m3 = st.columns(3)
        c_inc, c_exp = cat_df['รายรับ'].sum(), cat_df['รายจ่าย'].sum()
        m1.metric(f"➕ {selected_dis}", f"{c_inc:,.2f} ฿")
        m2.metric(f"➖ {selected_dis}", f"{c_exp:,.2f} ฿")
        m3.metric(f"💰 {selected_dis}", f"{(c_inc - c_exp):,.2f} ฿")

        fig = px.line(cat_df, x='วัน/เดือน/ปี', y=['รายรับ', 'รายจ่าย'], markers=True, 
                      title=f"🌻 {selected_dis}", color_discrete_map={"รายรับ": "#2ECC71", "รายจ่าย": "#E74C3C"})
        fig.update_xaxes(type='category')
        st.plotly_chart(fig, use_container_width=True)

        # รายการย้อนหลังและปุ่มลบ
        st.subheader(text["history"])
        for index, row in user_data.iterrows():
            col_t, col_b = st.columns([0.85, 0.15])
            with col_t:
                st.write(f"📅 **{row['วัน/เดือน/ปี']}** | 📂 {row['หมวดหมู่_display']} | ➕ {row['รายรับ']:,.2f} | ➖ {row['รายจ่าย']:,.2f}")
            if col_b.button(text["delete"], key=f"del_{index}"):
                all_data = all_data.drop(index)
                save_data(all_data)
                st.rerun()
            st.divider()
else:
    st.title("💰 Ubitmymoney 🌻")
    st.info("👈 Please enter Email / กรุณาเข้าสู่ระบบ")