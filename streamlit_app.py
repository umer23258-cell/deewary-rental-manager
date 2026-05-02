import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# --- 1. SUPABASE SETUP ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. PAGE CONFIG (Sidebar ko hamesha khula rakhne ke liye) ---
st.set_page_config(
    page_title="Deewary Property Manager", 
    layout="wide", 
    page_icon="🏢",
    initial_sidebar_state="expanded" # Is se mobile par sidebar bar bar gayab nahi hogi
)

# Mobile & Sidebar UI Fixes
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* Mobile par sidebar ka arrow button waps lane ke liye */
    .st-emotion-cache-zq5wmm { display: block !important; } 
    
    .login-box {
        background-color: #1E1E1E; 
        padding: 25px; 
        border-radius: 15px; 
        border: 1px solid #FF4B4B;
        margin-bottom: 20px;
    }
    
    /* Buttons ko bada aur mobile friendly banane ke liye */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIN LOGIC ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center; color:#FF4B4B;'>DEEWARY.COM</h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        user_name = st.selectbox("Apna Naam Select Karen", ["Umer (Manager)", "Sawer Khan", "Tariq Hussain"])
        pwd = st.text_input("Access Code", type="password")
        if st.button("🔓 Open Portal"):
            if pwd == "admin786":
                st.session_state.logged_in = True
                st.session_state.user_name = user_name
                st.rerun()
            else:
                st.error("Ghalat Code!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. MAIN APP CONTENT ---
user_name = st.session_state.user_name
if "menu" not in st.session_state:
    st.session_state.menu = "🏠 Dashboard"

def set_menu(name):
    st.session_state.menu = name

# HEADER
st.markdown(f"""
    <div style="text-align: center; background-color: #1E1E1E; padding: 15px; border-radius: 15px; border: 2px solid #FF4B4B; margin-bottom: 10px;">
        <h2 style="color: #FF4B4B; margin: 0;">DEEWARY MANAGER</h2>
        <p style="color: white; margin: 0;">User: {user_name}</p>
    </div>
""", unsafe_allow_html=True)

# --- 5. MAIN SCREEN NAVIGATION (Agar sidebar gayab ho jaye toh yahan se kaam chalega) ---
st.write("### 🚀 Quick Menu")
m_col1, m_col2, m_col3 = st.columns(3)
with m_col1:
    if st.button("📊 Dashboard"): set_menu("🏠 Dashboard")
with m_col2:
    if st.button("🏠 Add House"): set_menu("🏠 Ghar Entry")
with m_col3:
    if st.button("📋 History"): set_menu("📋 History")

st.divider()

# SIDEBAR (Backup for desktop)
with st.sidebar:
    st.title("📂 Navigation")
    if st.button("📊 Main Dashboard", key="side_dash"): set_menu("🏠 Dashboard")
    if st.button("🏠 Nayi Ghar Entry", key="side_ghar"): set_menu("🏠 Ghar Entry")
    if st.button("👤 Nayi Client Entry", key="side_client"): set_menu("👤 Client Entry")
    if st.button("📋 Mukammal History", key="side_hist"): set_menu("📋 History")
    st.markdown("---")
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

# --- 6. PAGE LOGIC ---
menu = st.session_state.menu

if menu == "🏠 Dashboard":
    st.subheader("📊 Business Overview")
    # Yahan Stats ka code (metrics)
    st.info("Dashboard Data Load Ho Raha Hai...")
    # metrics and charts here...

elif menu == "🏠 Ghar Entry":
    st.subheader("🏡 Naye Ghar ki Detail")
    with st.form("h_form"):
        o_name = st.text_input("Owner Name")
        loc = st.text_input("Location")
        rent = st.number_input("Demand", min_value=0)
        if st.form_submit_button("Save Property"):
            supabase.table('house_inventory').insert({"owner_name": o_name, "location": loc, "rent": rent, "added_by": user_name}).execute()
            st.success("Record Saved!")

elif menu == "📋 History":
    st.subheader("📋 Records")
    res = supabase.table('house_inventory').select("*").order('id', desc=True).execute()
    if res.data:
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)

st.caption(f"Portal Active | Manager: {user_name}")
