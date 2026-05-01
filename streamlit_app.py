import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
from fpdf import FPDF

# --- 1. SUPABASE SETUP ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Deewary Property Manager", layout="wide", page_icon="🏢")

# Custom CSS for Professional Sidebar and Buttons
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .sidebar-header { color: #FF4B4B; font-weight: bold; font-size: 16px; margin-top: 15px; border-bottom: 1px solid #444; padding-bottom: 5px; }
    .stButton>button { width: 100%; border-radius: 5px; height: 2.5em; margin-bottom: 5px; }
    .status-card { background-color: #2c3e50; color: white; padding: 15px; border-radius: 10px; border-left: 5px solid #FF4B4B; }
    </style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
def fetch_data(table_name):
    res = supabase.table(table_name).select("*").order("id", desc=True).execute()
    return pd.DataFrame(res.data)

def save_data(table_name, data_dict):
    try:
        supabase.table(table_name).insert(data_dict).execute()
        st.success(f"✅ Record saved in {table_name.replace('_', ' ').title()}!")
    except Exception as e:
        st.error(f"Error: {e}")

# --- 4. SIDEBAR NAVIGATION ---
st.sidebar.title("🏢 DEEWARY ADMIN")
user_name = st.sidebar.selectbox("Personnel", ["Anas", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "admin786":
    # --- NAVIGATION CATEGORIES ---
    st.sidebar.markdown('<p class="sidebar-header">🏠 PROPERTIES</p>', unsafe_allow_html=True)
    if st.sidebar.button("➕ Register New Property"): st.session_state.page = "reg_prop"
    if st.sidebar.button("📋 View All Properties"): st.session_state.page = "view_prop"

    st.sidebar.markdown('<p class="sidebar-header">👥 CLIENTS</p>', unsafe_allow_html=True)
    if st.sidebar.button("➕ Register New Client"): st.session_state.page = "reg_client"
    if st.sidebar.button("📋 View Client Leads"): st.session_state.page = "view_client"

    st.sidebar.markdown('<p class="sidebar-header">⏳ TASKS & VISITS</p>', unsafe_allow_html=True)
    if st.sidebar.button("➕ Add Pending Task"): st.session_state.page = "reg_task"
    if st.sidebar.button("📋 Pending Task List"): st.session_state.page = "view_task"
    if st.sidebar.button("➕ Log Site Visit"): st.session_state.page = "reg_visit"
    if st.sidebar.button("📋 Site Visit History"): st.session_state.page = "view_visit"

    st.sidebar.markdown('<p class="sidebar-header">🤝 DEALS</p>', unsafe_allow_html=True)
    if st.sidebar.button("🏆 Record Done Deal"): st.session_state.page = "reg_deal"
    if st.sidebar.button("📋 Closed Deals History"): st.session_state.page = "view_deal"

    st.sidebar.markdown('<p class="sidebar-header">🔍 REPORTS</p>', unsafe_allow_html=True)
    if st.sidebar.button("🖨️ Search & Export PDF"): st.session_state.page = "search_pdf"

    # Default Page
    if "page" not in st.session_state: st.session_state.page = "view_prop"

    # --- 5. PAGE LOGIC ---
    current_page = st.session_state.page

    # --- REGISTRATION FORMS ---
    if current_page == "reg_prop":
        st.subheader("🏠 New Property Registration")
        with st.form("prop_form"):
            c1, c2 = st.columns(2)
            with c1:
                o_name = st.text_input("Owner Name")
                loc = st.text_input("Location/Address")
                p_type = st.selectbox("Type", ["House", "Flat", "Shop", "Office", "Plot"])
            with c2:
                rent = st.number_input("Demand (PKR)", min_value=0)
                size = st.text_input("Size (e.g. 5 Marla)")
                contact = st.text_input("Contact Number")
            if st.form_submit_button("Save Property"):
                save_data('house_inventory', {"owner_name": o_name, "location": loc, "portion": p_type, "rent": rent, "size": size, "contact": contact, "added_by": user_name})

    elif current_page == "reg_client":
        st.subheader("👥 New Client Requirement")
        with st.form("client_form"):
            c1, c2 = st.columns(2)
            with c1:
                c_name = st.text_input("Client Name")
                c_req = st.text_input("Required Area")
            with c2:
                budget = st.number_input("Budget (PKR)", min_value=0)
                contact = st.text_input("Client Contact")
            if st.form_submit_button("Save Client"):
                save_data('client_leads', {"client_name": c_name, "req_location": c_req, "budget": budget, "contact": contact, "added_by": user_name})

    elif current_page == "reg_task":
        st.subheader("⏳ Add Pending Task")
        with st.form("task_form"):
            task = st.text_area("Task Detail")
            priority = st.selectbox("Priority", ["Low", "Medium", "High"])
            if st.form_submit_button("Save Task"):
                save_data('pending_tasks', {"task": task, "priority": priority, "status": "Pending", "added_by": user_name})

    elif current_page == "reg_visit":
        st.subheader("📍 Log Site Visit")
        with st.form("visit_form"):
            c1, c2 = st.columns(2)
            with c1:
                v_client = st.text_input("Client Name")
                v_prop = st.text_input("Property Visited")
            with c2:
                v_date = st.date_input("Visit Date")
                outcome = st.selectbox("Outcome", ["Interested", "Thinking", "Rejected"])
            if st.form_submit_button("Log Visit"):
                save_data('site_visits', {"client_name": v_client, "property_details": v_prop, "visit_date": str(v_date), "outcome": outcome, "agent": user_name})

    elif current_page == "reg_deal":
        st.subheader("🏆 Record Done Deal")
        with st.form("deal_form"):
            c1, c2 = st.columns(2)
            with c1:
                prop = st.text_input("Property Address")
                client = st.text_input("Client Name")
                f_rent = st.number_input("Final Rent", min_value=0)
            with c2:
                comm = st.number_input("Commission Earned", min_value=0)
                d_date = st.date_input("Closing Date")
            if st.form_submit_button("🏆 SAVE DEAL"):
                save_data('deals_done', {"property": prop, "client": client, "rent": f_rent, "commission": comm, "closing_date": str(d_date), "closed_by": user_name})

    # --- VIEW RECORDS PAGES ---
    elif current_page.startswith("view_"):
        table_map = {
            "view_prop": "house_inventory",
            "view_client": "client_leads",
            "view_task": "pending_tasks",
            "view_visit": "site_visits",
            "view_deal": "deals_done"
        }
        target_table = table_map[current_page]
        st.subheader(f"📋 {target_table.replace('_', ' ').upper()} RECORDS")
        df = fetch_data(target_table)
        st.dataframe(df, use_container_width=True)

    # --- SEARCH & PDF PAGE ---
    elif current_page == "search_pdf":
        st.subheader("🔍 Universal Search & PDF Report")
        mode = st.selectbox("Select Category", ["house_inventory", "client_leads", "pending_tasks", "site_visits", "deals_done"])
        q = st.text_input("Search Anything...")
        df = fetch_data(mode)
        if q:
            df = df[df.astype(str).apply(lambda x: x.str.contains(q, case=False)).any(axis=1)]
        st.dataframe(df, use_container_width=True)
        # PDF generation logic (same as your original code) goes here

else:
    st.info("Please enter Access Code in Sidebar to manage Deewary Database.")
