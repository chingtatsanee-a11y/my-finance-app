import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="UBITMYMONEY - Sunflower Edition", layout="wide", page_icon="🌻")

# --- 🎨 การตกแต่งธีมดอกทานตะวัน (Custom CSS) ---
st.markdown("""
    <style>
    /* เปลี่ยนสีพื้นหลัง Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFF9E3;
    }
    
    /* ปรับแต่งปุ่ม Save และปุ่มหลัก */
    div.stButton > button:first-child {
        background-color: #FFC107;
        color: #5D4037;
        border-radius: 20px;
        border: 2px solid #FFA000;
        font-weight: bold;
    }
    
    /* เอฟเฟกต์เมื่อวางเมาส์บนปุ่ม */
    div.stButton > button:first-child:hover {
        background-color: #FFD54F;
        border-color: #FFB300;
        color: #3E2723;
    }

    /* ปรับแต่ง Header และ Subheader */
    h1, h2, h3 {
        color: #5D4037 !important;
    }
    
    /* ปรับสี Metric */
    [data-testid="stMetricValue"] {
        color: #FB8C00;
    }
    
    /* เส้นคั่น */
    hr {
        border-top: 2px solid #FFD54F;
    }
    </style>
    """, unsafe_allow_html=True)

# ส่วนหัวของเว็บแบบมีดีไซน์
def sunflower_header():
    st.markdown("""
        <div style="background-color:#FFD54F; padding:20px; border-radius:15px; text-align:center; margin-bottom:20px;">
            <h1 style="color:#5D4037; margin:0;">🌻 Ubitmymoney 🌻</h1>
            <p style="color:#795548; font-size:1.2rem;">จัดการเงินของคุณให้สดใสเหมือนดอกทานตะวัน</p>
        </div>
    """, unsafe_allow_html=True)

# เรียกใช้ Header
sunflower_header()

# --- 2. ระบบแปลภาษา (คงเดิมจาก Code ของคุณ) ---
# ... (ใส่ Code ส่วนที่เหลือของคุณต่อจากตรงนี้ได้เลย)
DB_FILE = "data.csv"

# --- 2. ระบบแปลภาษาหมวดหมู่ (Custom Mapping) ---
# ระบบจะจำว่าถ้าพิมพ์คำซ้าย ให้แปลเป็นคำขวาเมื่อสลับภาษา
category_map = {
    "อาหาร": "Food",
    "เดินทาง": "Travel",
    "ที่พัก": "Housing",
    "ช้อปปิ้ง": "Shopping",
    "ทั่วไป": "General",
    "เงินเดือน": "Salary"
}
# สร้าง Mapping ขากลับ (English -> Thai)
inv_category_map = {v: k for k, v in category_map.items()}

languages = {
    "ไทย": {
        "login": "🔐 เข้าสู่ระบบ",
        "email_label": "กรอก Email ของคุณ:",
        "main_title": "📊 รายงานสรุปของ:",
        "total_overview": "🏦 ยอดรวมภาพรวม",
        "inc_total": "รายรับรวม",
        "exp_total": "รายจ่ายรวม",
        "bal_total": "คงเหลือสุทธิ",
        "new_entry": "➕ บันทึกรายการใหม่",
        "date": "วันที่",
        "category": "ระบุหมวดหมู่:",
        "income": "รายรับ (บาท)",
        "expense": "รายจ่าย (บาท)",
        "save": "บันทึกข้อมูล",
        "cat_analysis": "📈 วิเคราะห์รายหมวดหมู่",
        "select_cat": "เลือกหมวดหมู่ที่ต้องการดู:",
        "history": "📝 รายการทั้งหมด",
        "delete": "🗑️ ลบ"
    },
    "English": {
        "login": "🔐 Login",
        "email_label": "Enter your Email:",
        "main_title": "📊 Summary for:",
        "total_overview": "🏦 Overall Overview",
        "inc_total": "Total Income",
        "exp_total": "Total Expense",
        "bal_total": "Net Balance",
        "new_entry": "➕ Add New Entry",
        "date": "Date",
        "category": "Enter Category:",
        "income": "Income (฿)",
        "expense": "Expense (฿)",
        "save": "Save Data",
        "cat_analysis": "📈 Category Analysis",
        "select_cat": "Select category to view:",
        "history": "📝 Transaction History",
        "delete": "🗑️ Delete"
    }
}

lang_choice = st.sidebar.selectbox("🌐 Language", ["ไทย", "English"])
text = languages[lang_choice]

# --- 3. ฟังก์ชันแปลชื่อหมวดหมู่แบบ Real-time ---
def translate_cat(cat_name, target_lang):
    if target_lang == "English":
        return category_map.get(cat_name, cat_name) # ถ้าไม่มีในดิกให้ใช้คำเดิม
    else:
        return inv_category_map.get(cat_name, cat_name)

# --- 4. LOGIC: จัดการข้อมูล ---
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

# --- 5. การแสดงผลหน้าเว็บ ---
st.sidebar.divider()
user_email = st.sidebar.text_input(text["email_label"]).strip()

if user_email:
    all_data = load_data()
    user_data = all_data[all_data['ที่อยู่อีเมล'] == user_email].copy()

    # แปลชื่อหมวดหมู่ใน Dataframe ทั้งหมดแบบ Real-time ก่อนแสดงผล
    user_data['หมวดหมู่_display'] = user_data['หมวดหมู่'].apply(lambda x: translate_cat(x, lang_choice))

    st.title(f"{text['main_title']} {user_email}")

    # ยอดรวม Metrics
    if not user_data.empty:
        st.subheader(text["total_overview"])
        c1, c2, c3 = st.columns(3)
        t_inc, t_exp = user_data['รายรับ'].sum(), user_data['รายจ่าย'].sum()
        c1.metric(text["inc_total"], f"{t_inc:,.2f} ฿")
        c2.metric(text["exp_total"], f"{t_exp:,.2f} ฿")
        c3.metric(text["bal_total"], f"{(t_inc - t_exp):,.2f} ฿")

    # ฟอร์มบันทึกรายการ
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
                # บันทึกลง CSV เป็นภาษาไทยเสมอเพื่อเป็นมาตรฐานในการเก็บข้อมูล
                save_cat = inv_category_map.get(cat_input, cat_input)
                new_row = pd.DataFrame([{"ที่อยู่อีเมล": user_email, "วัน/เดือน/ปี": d.strftime("%d/%m/%Y"), 
                                         "หมวดหมู่": save_cat, "รายรับ": inc, "รายจ่าย": exp}])
                updated_all = pd.concat([all_data, new_row], ignore_index=True)
                save_data(updated_all)
                st.rerun()

    # กราฟแยกหมวดหมู่
    if not user_data.empty:
        st.subheader(text["cat_analysis"])
        unique_cats = user_data['หมวดหมู่_display'].unique()
        selected_cat_dis = st.selectbox(text["select_cat"], unique_cats)
        
        # กรองข้อมูลจากชื่อที่แสดงผล
        cat_df = user_data[user_data['หมวดหมู่_display'] == selected_cat_dis]
        
        # ยอดสรุปเฉพาะหมวด
        m1, m2, m3 = st.columns(3)
        c_inc, c_exp = cat_df['รายรับ'].sum(), cat_df['รายจ่าย'].sum()
        m1.metric(f"{text['income']} ({selected_cat_dis})", f"{c_inc:,.2f} ฿")
        m2.metric(f"{text['expense']} ({selected_cat_dis})", f"{c_exp:,.2f} ฿")
        m3.metric(f"{text['bal_total']} ({selected_cat_dis})", f"{(c_inc - c_exp):,.2f} ฿")

        fig = px.line(cat_df, x='วัน/เดือน/ปี', y=['รายรับ', 'รายจ่าย'], markers=True, title=selected_cat_dis)
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
    st.title("💰 UBITMYMONEY")
    st.info("👈 Login to continue / กรุณาเข้าสู่ระบบ")