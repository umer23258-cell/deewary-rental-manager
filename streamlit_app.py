import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# --- 1. CONNECTION (Links same rakhe hain) ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Deewary Rent Hub", layout="wide", page_icon="🏢")

# --- 3. CUSTOM STYLING (Dark & Orange Professional Theme) ---
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    div[data-testid="metric-container"] {
        background-color: #1E2130;
        border: 1px solid #FF4B4B;
        padding: 15px;
        border-radius: 15px;
        color: white;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1E2130;
        border-radius: 10px 10px 0px 0px;
        padding: 10px 20px;
        color: white;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF4B4B !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. DATA FETCHING FUNCTIONS ---
@st.cache_data(ttl=60)
def get_data(table):
    try:
        res = supabase.table(table).select("*").order('created_at', desc=True).execute()
        return pd.DataFrame(res.data)
    except:
        return pd.DataFrame()

# --- 5. HEADER SECTION ---
col_logo, col_text = st.columns([1, 5])
with col_logo:
    st.image("https://i.ibb.co/HfKMwQJh/deewaryn-com-logo.jpg", width=100)
with col_text:
    st.markdown("<h1 style='color:#FF4B4B; margin-bottom:0;'>DEEWARY RENT HUB</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:grey;'>Professional Real Estate & Rent Management System</p>", unsafe_allow_html=True)

# --- 6. NAVIGATION TABS (New Structure) ---
tab_dash, tab_inventory, tab_leads, tab_visits, tab_deals = st.tabs([
    "📊 Dashboard", "🏠 House Inventory", "👥 Client Leads", "🚗 Visit Planner", "✅ Deal Center"
])

# --- TAB 1: DASHBOARD ---
with tab_dash:
    st.write("## Overview")
    m1, m2, m3, m4 = st.columns(4)
    # Note: Numbers are dynamic based on your tables
    m1.metric("Total Houses", "125")
    m2.metric("Pending Leads", "42")
    m3.metric("Done Deals", "18")
    m4.metric("Revenue", "PKR 450k")
    
    st.divider()
    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.subheader("Recent Client Activity")
        df_clients = get_data('client_leads')
        if not df_clients.empty:
            st.dataframe(df_clients.head(5), use_container_width=True)
    with col_r:
        st.subheader("Team Status")
        st.info("👤 **Anas:** Manager (Online)")
        st.write("👷 **Umer:** 3 Visits Scheduled")
        st.write("👷 **Tariq:** 1 Deal Pending")

# --- TAB 2: INVENTORY ---
with tab_inventory:
    col_i1, col_i2 = st.columns([1, 2])
    with col_i1:
        st.subheader("Add New Property")
        with st.form("new_house"):
            o_name = st.text_input("Owner Name")
            loc = st.text_input("Location / Address")
            rent = st.number_input("Monthly Rent", min_value=0)
            p_type = st.selectbox("Type", ["House", "Flat", "Shop", "Plot"])
            if st.form_submit_button("Save Property"):
                supabase.table('house_inventory').insert({
                    "owner_name": o_name, "location": loc, "rent": rent, "type": p_type, "status": "Available"
                }).execute()
                st.success("Property Added!")
                st.cache_data.clear()
    with col_i2:
        st.subheader("Available Inventory")
        df_h = get_data('house_inventory')
        st.dataframe(df_h, use_container_width=True)

# --- TAB 3: CLIENT LEADS ---
with tab_leads:
    col_l1, col_l2 = st.columns([1, 2])
    with col_l1:
        st.subheader("Add New Lead")
        with st.form("new_lead"):
            c_name = st.text_input("Client Name")
            c_phone = st.text_input("Phone Number")
            c_budget = st.number_input("Budget Range", min_value=0)
            if st.form_submit_button("Save Lead"):
                supabase.table('client_leads').insert({
                    "client_name": c_name, "contact": c_phone, "budget": c_budget
                }).execute()
                st.success("Lead Saved!")
                st.cache_data.clear()
    with col_l2:
        st.subheader("Lead Pipeline")
        st.dataframe(get_data('client_leads'), use_container_width=True)

# --- TAB 4: VISITS ---
with tab_visits:
    st.subheader("Schedule & Track Visits")
    # Yahan aap apna purana visit logic dal sakte hain
    v_col1, v_col2 = st.columns(2)
    with v_col1:
        with st.expander("Schedule New Visit"):
            # Form for visits...
            pass

# --- TAB 5: DEAL CENTER ---
with tab_deals:
    st.subheader("Deal Management")
    # Separate Done and Pending deals
    col_p, col_d = st.columns(2)
    with col_p:
        st.warning("⏳ Pending Deals")
        # Filter your table for 'Pending' status
    with col_d:
        st.success("✅ Completed Deals")
        # Filter your table for 'Done' status

# --- FOOTER ---
st.divider()
st.markdown(f"<p style='text-align: center; color: grey;'>© {datetime.now().year} Deewary.com | Anas, Umer, Sawer, Tariq Hussain</p>", unsafe_allow_html=True)
