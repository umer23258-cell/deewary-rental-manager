import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# --- 1. SUPABASE SETUP ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Deewary Property Manager", layout="wide", page_icon="🏢")

# --- 3. CUSTOM CSS (Focused on Button Shape & Size) ---
st.markdown("""
    <style>
    /* Sidebar ki width ko standard rakha hai */
    [data-testid="stSidebar"] {
        min-width: 300px !important;
    }

    /* Buttons ka shape chota aur sleek banane ke liye */
    div.stButton > button {
        height: 28px !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
        font-size: 12px !important;
        font-weight: 500;
        border-radius: 4px;
        border: 1px solid #34495e;
        margin-bottom: -10px; /* Buttons ke darmiyan gap kam karne ke liye */
    }

    /* Sidebar headers styling */
    .sidebar-header {
        color: #FF4B4B;
        font-weight: bold;
        font-size: 14px;
        margin-top: 15px;
        margin-bottom: 2px;
        border-bottom: 1px solid #444;
    }
    
    /* Input fields and selectbox in sidebar ko bhi thoda compact kiya */
    .stSelectbox, .stTextInput {
        margin-bottom: -10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. HELPERS ---
def save_rec(table, data):
    supabase.table(table).insert(data).execute()
    st.success(f"Saved in {table}!")

# --- 5. SIDEBAR NAVIGATION ---
st.sidebar.title("🏢 DEEWARY ADMIN")
user_name = st.sidebar.selectbox("Personnel", ["Anas", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "admin786":
    # --- PROPERTIES ---
    st.sidebar.markdown('<p class="sidebar-header">🏠 PROPERTIES</p>', unsafe_allow_html=True)
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("➕ Reg"): st.session_state.page = "reg_prop"
    with col2:
        if st.button("📋 Hist"): st.session_state.page = "hist_prop"

    # --- CLIENTS ---
    st.sidebar.markdown('<p class="sidebar-header">👥 CLIENTS</p>', unsafe_allow_html=True)
    col3, col4 = st.sidebar.columns(2)
    with col3:
        if st.button("➕ Reg Client"): st.session_state.page = "reg_client"
    with col4:
        if st.button("📋 Hist Client"): st.session_state.page = "hist_client"

    # --- TASKS ---
    st.sidebar.markdown('<p class="sidebar-header">⏳ PENDING TASKS</p>', unsafe_allow_html=True)
    col5, col6 = st.sidebar.columns(2)
    with col5:
        if st.button("➕ Add Task"): st.session_state.page = "reg_task"
    with col6:
        if st.button("📋 Task List"): st.session_state.page = "hist_task"

    # --- VISITS ---
    st.sidebar.markdown('<p class="sidebar-header">📍 SITE VISITS</p>', unsafe_allow_html=True)
    col7, col8 = st.sidebar.columns(2)
    with col7:
        if st.button("➕ Log Visit"): st.session_state.page = "reg_visit"
    with col8:
        if st.button("📋 Visit Log"): st.session_state.page = "hist_visit"

    # --- DEALS ---
    st.sidebar.markdown('<p class="sidebar-header">🤝 DEALS DONE</p>', unsafe_allow_html=True)
    col9, col10 = st.sidebar.columns(2)
    with col9:
        if st.button("🏆 Record Deal"): st.session_state.page = "reg_deal"
    with col10:
        if st.button("📋 Deal Hist"): st.session_state.page = "hist_deal"

    # --- SEARCH ---
    st.sidebar.markdown('<p class="sidebar-header">🔍 REPORTS</p>', unsafe_allow_html=True)
    if st.sidebar.button("🔎 Search & PDF Report"): st.session_state.page = "search"

    # Default Page
    if "page" not in st.session_state: st.session_state.page = "hist_prop"

    # --- 6. PAGE CONTENT ---
    pg = st.session_state.page

    # Example Logic for View (Repeated for all categories)
    if pg.startswith("hist_"):
        table_name = {
            "hist_prop": "house_inventory",
            "hist_client": "client_leads",
            "hist_task": "pending_tasks",
            "hist_visit": "site_visits",
            "hist_deal": "deals_done"
        }[pg]
        st.subheader(f"📋 {table_name.replace('_', ' ').upper()} RECORDS")
        res = supabase.table(table_name).select("*").execute()
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)

    elif pg == "reg_prop":
        st.subheader("🏡 New Property Registration")
        with st.form("p_form"):
            o_name = st.text_input("Owner Name")
            loc = st.text_input("Location")
            rent = st.number_input("Rent", min_value=0)
            if st.form_submit_button("Save"):
                save_rec("house_inventory", {"owner_name": o_name, "location": loc, "rent": rent, "added_by": user_name})

    # (Aap baki forms bhi isi tarah add kar sakte hain...)

else:
    st.info("Sidebar se Access Code enter karein.")

st.divider()
st.caption(f"© {datetime.now().year} Deewary.com | All Records Separated")
