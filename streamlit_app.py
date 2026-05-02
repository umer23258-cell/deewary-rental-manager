import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# --- 1. SUPABASE SETUP ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. PAGE CONFIG ---
st.set_page_config(
    page_title="Deewary Property Manager", 
    layout="wide", 
    page_icon="🏢",
    initial_sidebar_state="expanded" # Mobile pe pehli baar khula nazar ayega
)

# --- MOBILE SIDEBAR FIX CSS ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* Mobile par Sidebar ka arrow button hamesha dikhane ke liye */
    section[data-testid="stSidebar"] {
        transition: all 0.3s;
    }
    
    /* Sidebar ke button ko customize karna taake wo asani se click ho */
    .st-emotion-cache-zq5wmm {
        display: block !important;
        background-color: #FF4B4B !important;
        color: white !important;
        border-radius: 50% !important;
        left: 10px !important;
        top: 10px !important;
    }

    .login-box {
        background-color: #1E1E1E; 
        padding: 25px; 
        border-radius: 15px; 
        border: 1px solid #FF4B4B;
        margin-bottom: 20px;
    }
    .stButton>button { width: 100%; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
def delete_record(table_name, record_id):
    supabase.table(table_name).delete().eq("id", record_id).execute()
    st.warning(f"Record ID {record_id} delete kar diya gaya hai.")
    st.rerun()

def update_record(table_name, record_id, data_dict):
    supabase.table(table_name).update(data_dict).eq("id", record_id).execute()
    st.success(f"Record ID {record_id} update ho gaya!")
    st.rerun()

# --- 4. LOGIN SYSTEM ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("""
        <div style="text-align: center; padding: 10px;">
            <h1 style="color: #FF4B4B; font-family: 'Arial Black';">DEEWARY.COM</h1>
            <p style="color: white;">STAFF LOGIN PORTAL</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        user_name = st.selectbox("Apna Naam Select Karen", ["Umer (Manager)", "Sawer Khan", "Tariq Hussain"])
        pwd = st.text_input("Access Code", type="password", placeholder="Enter Password")
        if st.button("🔓 Login"):
            if pwd == "admin786":
                st.session_state.logged_in = True
                st.session_state.user_name = user_name
                st.rerun()
            else:
                st.error("Code Ghalat Hai!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 5. LOGGED IN CONTENT ---
user_name = st.session_state.user_name

# HEADER
st.markdown(f"""
    <div style="text-align: center; background-color: #1E1E1E; padding: 15px; border-radius: 15px; border: 2px solid #FF4B4B; margin-bottom: 20px;">
        <h2 style="color: #FF4B4B; margin: 0; font-size: 24px;">DEEWARY PROPERTY MANAGER</h2>
        <p style="color: white; margin: 0;">Welcome: <b>{user_name}</b></p>
    </div>
""", unsafe_allow_html=True)

# SIDEBAR MENU
st.sidebar.title("🚀 Navigation")
if "menu" not in st.session_state:
    st.session_state.menu = "🏠 Dashboard"

def set_menu(name):
    st.session_state.menu = name

# Buttons on Sidebar
if st.sidebar.button("📊 Dashboard", use_container_width=True): set_menu("🏠 Dashboard")
st.sidebar.markdown("---")
st.sidebar.subheader("➕ NAYI ENTRY")
if st.sidebar.button("🏠 Ghar Entry", use_container_width=True): set_menu("🏠 Ghar Entry")
if st.sidebar.button("👤 Client Entry", use_container_width=True): set_menu("👤 Client Entry")
if st.sidebar.button("💬 Discussion", use_container_width=True): set_menu("💬 Discussion")
if st.sidebar.button("✅ Deal Done", use_container_width=True): set_menu("✅ Deal Done")

st.sidebar.markdown("---")
st.sidebar.subheader("📋 RECORDS")
if st.sidebar.button("📋 Gharon ki History", use_container_width=True): set_menu("📋 History")
if st.sidebar.button("🚪 Logout", use_container_width=True): 
    st.session_state.logged_in = False
    st.rerun()

menu = st.session_state.menu

# --- 6. DASHBOARD LOGIC ---
if menu == "🏠 Dashboard":
    st.subheader("📊 Business Overview")
    h_res = supabase.table('house_inventory').select("*").execute()
    c_res = supabase.table('client_leads').select("*").execute()
    d_res = supabase.table('deals_done').select("*").execute()

    df_h = pd.DataFrame(h_res.data) if h_res.data else pd.DataFrame()
    df_c = pd.DataFrame(c_res.data) if c_res.data else pd.DataFrame()
    df_d = pd.DataFrame(d_res.data) if d_res.data else pd.DataFrame()

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Houses", len(df_h))
    c2.metric("Total Clients", len(df_c))
    c3.metric("Deals Done", len(df_d))

    st.markdown("---")
    st.write("### 🏠 Recent Properties")
    if not df_h.empty:
        st.dataframe(df_h[['added_by', 'owner_name', 'location', 'rent', 'status']].head(10), use_container_width=True)

# --- 7. ENTRY FORMS ---
elif menu == "🏠 Ghar Entry":
    st.subheader("🏡 Naye Ghar ki Entry")
    with st.form("house_form", clear_on_submit=True):
        o_name = st.text_input("Owner Name")
        loc = st.text_input("Location")
        rent = st.number_input("Demand Rent", min_value=0)
        status = st.selectbox("Status", ["Available", "Rent Out"])
        if st.form_submit_button("Save House"):
            supabase.table('house_inventory').insert({
                "owner_name": o_name, "location": loc, "rent": rent, "status": status, "added_by": user_name
            }).execute()
            st.success("Save ho gaya!")

# --- 8. HISTORY LOGIC ---
elif menu == "📋 History":
    st.subheader("📋 Property History")
    res = supabase.table('house_inventory').select("*").order('id', desc=True).execute()
    if res.data:
        df = pd.DataFrame(res.data)
        st.dataframe(df, use_container_width=True)
        st.markdown("---")
        del_id = st.number_input("ID to Delete", min_value=0, step=1)
        if st.button("🗑️ Confirm Delete"):
            delete_record('house_inventory', del_id)
    else:
        st.info("No records found.")

st.divider()
st.caption(f"© {datetime.now().year} Deewary.com | Active: {user_name}")
