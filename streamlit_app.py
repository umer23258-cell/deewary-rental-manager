import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# --- 1. SUPABASE SETUP ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Deewary | Pakistan's Property Portal", layout="wide", page_icon="🏢")

# --- 3. ZAMEEN.COM THEME CSS ---
st.markdown("""
    <style>
    /* Main Background */
    [data-testid="stAppViewContainer"] { background-color: #f4f4f4; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #ddd; }
    
    /* Zameen Green Buttons */
    div.stButton > button {
        width: 100%;
        height: 38px !important;
        background-color: #27a344 !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
        transition: 0.3s;
        margin-bottom: -10px;
    }
    div.stButton > button:hover {
        background-color: #1e7e34 !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }

    /* Sidebar Headers */
    .nav-header {
        font-size: 11px;
        font-weight: 700;
        color: #888;
        text-transform: uppercase;
        margin-top: 20px;
        margin-bottom: 5px;
        letter-spacing: 1px;
    }

    /* Property Card Style */
    .prop-card {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin-bottom: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.02);
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. NAVIGATION ALGORITHM ---
# Sidebar Brand
st.sidebar.markdown("<h1 style='color: #27a344; font-size: 28px; margin-bottom: 0;'>zameen</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='color: #666; font-size: 12px; margin-bottom: 20px;'>Har Pata, Humain Pata Hai</p>", unsafe_allow_html=True)

user_name = st.sidebar.selectbox("Personnel", ["Anas", "Sawer Khan", "Tariq Hussain"])
access_code = st.sidebar.text_input("Access Code", type="password")

if access_code == "admin786":
    # Navigation Structure
    st.sidebar.markdown('<p class="nav-header">MAIN MENU</p>', unsafe_allow_html=True)
    if st.sidebar.button("🏠 Property Buy/Rent"): st.session_state.menu = "inventory"
    if st.sidebar.button("👥 Client Leads"): st.session_state.menu = "clients"
    
    st.sidebar.markdown('<p class="nav-header">OPERATIONS</p>', unsafe_allow_html=True)
    if st.sidebar.button("⏳ Pending Tasks"): st.session_state.menu = "tasks"
    if st.sidebar.button("📍 Site Visits"): st.session_state.menu = "visits"
    
    st.sidebar.markdown('<p class="nav-header">ACCOUNTS</p>', unsafe_allow_html=True)
    if st.sidebar.button("🤝 Done Deals"): st.session_state.menu = "deals"
    if st.sidebar.button("🔍 Search & Reports"): st.session_state.menu = "reports"

    # Default View
    if "menu" not in st.session_state: st.session_state.menu = "inventory"

    # --- 5. MAIN CONTENT AREA ---
    active = st.session_state.menu

    # --- INVENTORY ALGORITHM (ZAMEEN STYLE) ---
    if active == "inventory":
        col_main, col_form = st.columns([2, 1])
        
        with col_form:
            st.markdown("<div class='prop-card'><b>+ Add New Property</b></div>", unsafe_allow_html=True)
            with st.form("add_prop_form", clear_on_submit=True):
                title = st.text_input("Property Title")
                loc = st.text_input("Location (e.g. DHA Phase 2)")
                p_type = st.selectbox("Type", ["House", "Flat", "Plot", "Commercial"])
                rent = st.number_input("Demand (PKR)", min_value=0)
                if st.form_submit_button("List Property"):
                    supabase.table('house_inventory').insert({"owner_name": title, "location": loc, "portion": p_type, "rent": rent, "added_by": user_name}).execute()
                    st.success("Listed on Portal!")

        with col_main:
            st.subheader("Properties in Pakistan")
            res = supabase.table('house_inventory').select("*").order("id", desc=True).execute()
            df = pd.DataFrame(res.data)
            
            for index, row in df.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="prop-card">
                        <h4 style="color: #27a344; margin-bottom: 5px;">PKR {row['rent']:,}</h4>
                        <p style="margin: 0;"><b>{row['portion']}</b> in {row['location']}</p>
                        <p style="font-size: 12px; color: #666;">Added by: {row['added_by']} | ID: #00{row['id']}</p>
                    </div>
                    """, unsafe_allow_html=True)

    # --- CLIENTS ALGORITHM ---
    elif active == "clients":
        st.subheader("Client Requirements & Leads")
        c1, c2 = st.columns([1, 2])
        with c1:
            with st.form("client_f"):
                c_name = st.text_input("Client Name")
                c_budget = st.number_input("Budget", min_value=0)
                if st.form_submit_button("Register Lead"):
                    supabase.table('client_leads').insert({"client_name": c_name, "budget": c_budget, "added_by": user_name}).execute()
        with c2:
            res = supabase.table('client_leads').select("*").execute()
            st.table(pd.DataFrame(res.data))

    # --- TASKS & VISITS (Separated) ---
    elif active == "tasks":
        st.subheader("⏳ Daily To-Do List")
        task = st.text_input("New Task Description")
        if st.button("Save Task"):
            supabase.table('pending_tasks').insert({"task": task, "added_by": user_name}).execute()
        
        res = supabase.table('pending_tasks').select("*").execute()
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)

    # --- DEALS ALGORITHM ---
    elif active == "deals":
        st.subheader("🤝 Closed Deals Record")
        res = supabase.table('deals_done').select("*").execute()
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)

    # --- REPORTS & SEARCH ---
    elif active == "reports":
        st.subheader("🔍 Centralized Search Engine")
        search_query = st.text_input("Search across database (Price, Location, Name)...")
        # Logic for filtering data goes here

else:
    st.info("Deewary Property Portal: Please enter your access code in the sidebar to continue.")

# --- FOOTER ---
st.markdown("<br><hr><p style='text-align: center; color: #888;'>Powered by Deewary.com | Zameen-Inspired CRM v2.0</p>", unsafe_allow_html=True)
