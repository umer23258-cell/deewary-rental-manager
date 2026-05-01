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

# --- 3. CUSTOM CSS FOR SMALL BUTTONS ---
st.markdown("""
    <style>
    /* Sidebar width and spacing */
    [data-testid="stSidebar"] { min-width: 250px; max-width: 250px; }
    
    /* Buttons ko chota aur compact banane ke liye */
    .stButton>button {
        width: 100%;
        height: 32px !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
        font-size: 14px !important;
        border-radius: 4px;
        margin-bottom: -10px;
        background-color: #2c3e50;
        color: white;
    }
    
    /* Sidebar Headers */
    .sidebar-header {
        color: #FF4B4B;
        font-weight: bold;
        font-size: 13px;
        margin-top: 15px;
        margin-bottom: 5px;
        text-transform: uppercase;
        border-bottom: 1px solid #444;
    }
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 4. DATA HELPERS ---
def save_to_supabase(table, data):
    try:
        supabase.table(table).insert(data).execute()
        st.success("✅ Data Successfully Saved!")
    except Exception as e:
        st.error(f"Error: {e}")

# --- 5. SIDEBAR LOGIN & NAVIGATION ---
st.sidebar.markdown("### 🔐 ACCESS CONTROL")
user_name = st.sidebar.selectbox("Personnel", ["Anas", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "admin786":
    
    # --- SECTION: PROPERTIES ---
    st.sidebar.markdown('<p class="sidebar-header">🏠 Properties</p>', unsafe_allow_html=True)
    if st.sidebar.button("➕ Register Property"): st.session_state.page = "reg_prop"
    if st.sidebar.button("📋 Property History"): st.session_state.page = "hist_prop"

    # --- SECTION: CLIENTS ---
    st.sidebar.markdown('<p class="sidebar-header">👥 Clients</p>', unsafe_allow_html=True)
    if st.sidebar.button("➕ Register Client"): st.session_state.page = "reg_client"
    if st.sidebar.button("📋 Client History"): st.session_state.page = "hist_client"

    # --- SECTION: TASKS ---
    st.sidebar.markdown('<p class="sidebar-header">⏳ Pending Tasks</p>', unsafe_allow_html=True)
    if st.sidebar.button("➕ Add New Task"): st.session_state.page = "reg_task"
    if st.sidebar.button("📋 Task History"): st.session_state.page = "hist_task"

    # --- SECTION: SITE VISITS ---
    st.sidebar.markdown('<p class="sidebar-header">📍 Site Visits</p>', unsafe_allow_html=True)
    if st.sidebar.button("➕ Log New Visit"): st.session_state.page = "reg_visit"
    if st.sidebar.button("📋 Visit History"): st.session_state.page = "hist_visit"

    # --- SECTION: DEALS ---
    st.sidebar.markdown('<p class="sidebar-header">🤝 Deals Done</p>', unsafe_allow_html=True)
    if st.sidebar.button("🏆 Record Done Deal"): st.session_state.page = "reg_deal"
    if st.sidebar.button("📋 Deal History"): st.session_state.page = "hist_deal"

    # --- SECTION: REPORTS ---
    st.sidebar.markdown('<p class="sidebar-header">🔍 Reports</p>', unsafe_allow_html=True)
    if st.sidebar.button("🖨️ Search & PDF"): st.session_state.page = "search_report"

    # Default Page
    if "page" not in st.session_state: st.session_state.page = "hist_prop"

    # --- 6. PAGE ROUTING ---
    pg = st.session_state.page

    # 1. PROPERTY PAGES
    if pg == "reg_prop":
        st.subheader("🏡 Register New Property")
        with st.form("p_form", clear_on_submit=True):
            o_name = st.text_input("Owner Name")
            loc = st.text_input("Address")
            rent = st.number_input("Demand", min_value=0)
            if st.form_submit_button("Save Property"):
                save_to_supabase("house_inventory", {"owner_name": o_name, "location": loc, "rent": rent, "added_by": user_name})
    
    elif pg == "hist_prop":
        st.subheader("📋 Property Records")
        res = supabase.table("house_inventory").select("*").execute()
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)

    # 2. CLIENT PAGES
    elif pg == "reg_client":
        st.subheader("👥 Register New Client")
        with st.form("c_form", clear_on_submit=True):
            c_name = st.text_input("Client Name")
            budget = st.number_input("Budget", min_value=0)
            if st.form_submit_button("Save Client"):
                save_to_supabase("client_leads", {"client_name": c_name, "budget": budget, "added_by": user_name})
    
    elif pg == "hist_client":
        st.subheader("📋 Client Records")
        res = supabase.table("client_leads").select("*").execute()
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)

    # 3. TASK PAGES
    elif pg == "reg_task":
        st.subheader("⏳ Add New Pending Task")
        with st.form("t_form", clear_on_submit=True):
            task = st.text_area("Task Detail")
            if st.form_submit_button("Save Task"):
                save_to_supabase("pending_tasks", {"task": task, "status": "Pending", "added_by": user_name})
    
    elif pg == "hist_task":
        st.subheader("📋 Pending Task Records")
        res = supabase.table("pending_tasks").select("*").execute()
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)

    # 4. VISIT PAGES
    elif pg == "reg_visit":
        st.subheader("📍 Log New Site Visit")
        with st.form("v_form", clear_on_submit=True):
            v_client = st.text_input("Client Name")
            v_prop = st.text_input("Property Visited")
            if st.form_submit_button("Save Visit"):
                save_to_supabase("site_visits", {"client_name": v_client, "property_details": v_prop, "agent": user_name})
    
    elif pg == "hist_visit":
        st.subheader("📋 Site Visit Records")
        res = supabase.table("site_visits").select("*").execute()
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)

    # 5. DEAL PAGES
    elif pg == "reg_deal":
        st.subheader("🏆 Record Done Deal")
        with st.form("d_form", clear_on_submit=True):
            d_prop = st.text_input("Property Address")
            d_rent = st.number_input("Final Rent", min_value=0)
            if st.form_submit_button("Save Done Deal"):
                save_to_supabase("deals_done", {"property": d_prop, "rent": d_rent, "closed_by": user_name})
    
    elif pg == "hist_deal":
        st.subheader("📋 Successful Deal Records")
        res = supabase.table("deals_done").select("*").execute()
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)

    # 6. SEARCH & PDF
    elif pg == "search_report":
        st.subheader("🔍 Universal Search & Report")
        mode = st.selectbox("Select Record Type", ["house_inventory", "client_leads", "pending_tasks", "site_visits", "deals_done"])
        q = st.text_input("Type to search...")
        res = supabase.table(mode).select("*").execute()
        df = pd.DataFrame(res.data)
        if q:
            df = df[df.astype(str).apply(lambda x: x.str.contains(q, case=False)).any(axis=1)]
        st.dataframe(df, use_container_width=True)

else:
    st.warning("Please enter correct access code to view the menu.")

st.divider()
st.caption(f"© {datetime.now().year} Deewary.com | Data Protection Active")
