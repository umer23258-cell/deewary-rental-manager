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

# Sidebar Style (Aapke mutabiq)
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1E1E1E; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #FF4B4B; color: white; border: none; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER (Original Style) ---
st.markdown("""
    <div style="text-align: center; background-color: #1E1E1E; padding: 20px; border-radius: 15px; border: 2px solid #FF4B4B;">
        <h1 style="color: #FF4B4B; margin: 0; font-family: 'Arial Black';">DEEWARY PROPERTY MANAGER</h1>
        <p style="color: white; letter-spacing: 2px;">OWNER INVENTORY & CLIENT DATABASE</p>
    </div>
""", unsafe_allow_html=True)

# --- 4. SIDEBAR NAVIGATION ---
st.sidebar.title("🔐 Control Panel")
user_name = st.sidebar.selectbox("Select Staff", ["Anas", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "admin786":
    st.sidebar.divider()
    if st.sidebar.button("📊 DAILY DASHBOARD"): st.session_state.page = "dash"
    
    st.sidebar.subheader("➕ NAYI ENTRY")
    if st.sidebar.button("🏠 Ghar ki Entry"): st.session_state.page = "add_h"
    if st.sidebar.button("👤 Client Entry"): st.session_state.page = "add_c"
    if st.sidebar.button("⏳ Deal Pending"): st.session_state.page = "add_p"
    if st.sidebar.button("✅ Deal Done"): st.session_state.page = "add_d"
    
    st.sidebar.subheader("📜 HISTORY")
    if st.sidebar.button("📋 Ghar History"): st.session_state.page = "hist_h"
    if st.sidebar.button("👥 Client History"): st.session_state.page = "hist_c"
    if st.sidebar.button("📂 Deals History"): st.session_state.page = "hist_deals"

    # Current Page Logic
    page = st.session_state.get('page', 'dash')

    # --- 5. DASHBOARD ---
    if page == "dash":
        st.subheader("📊 Office Dashboard")
        h_res = supabase.table('house_inventory').select("*").execute()
        c_res = supabase.table('client_leads').select("*").execute()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Ghar", len(h_res.data))
        c2.metric("Total Clients", len(c_res.data))
        c3.metric("Current Staff", user_name)
        
        st.divider()
        st.write("### Recent Activity")
        if h_res.data:
            st.dataframe(pd.DataFrame(h_res.data).tail(5), use_container_width=True)

    # --- 6. GHAR KI ENTRY (With Gas, Water, Elec) ---
    elif page == "add_h":
        st.subheader("🏡 Naye Ghar ki Entry")
        with st.form("house_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                o_name = st.text_input("Owner ka Naam")
                o_contact = st.text_input("Owner Contact")
                loc = st.text_input("Location")
                portion = st.selectbox("Portion", ["Full House", "Ground", "First", "Second", "Shop", "Office"])
                marla = st.text_input("Size (Marla)")
            with col2:
                rent = st.number_input("Rent Demand", min_value=0)
                v_time = st.text_input("Visit Time")
                gas = st.radio("Gas", ["Yes", "No"], horizontal=True)
                water = st.radio("Water", ["Yes", "No"], horizontal=True)
                elec = st.radio("Electricity", ["Yes", "No"], horizontal=True)
            
            if st.form_submit_button("Save House Record"):
                payload = {
                    "owner_name": o_name, "contact": o_contact, "location": loc, "portion": portion,
                    "rent": rent, "size": marla, "gas": gas, "water": water, "electricity": elec,
                    "visit_time": v_time, "added_by": user_name
                }
                supabase.table('house_inventory').insert(payload).execute()
                st.success("House Saved!")

    # --- 7. PENDING DEAL ---
    elif page == "add_p":
        st.subheader("⏳ Deal Pending ki Entry")
        with st.form("pending_form"):
            p_client = st.text_input("Client Name")
            p_details = st.text_area("Property Details")
            p_token = st.number_input("Token Amount", min_value=0)
            p_date = st.date_input("Expected Closing Date")
            if st.form_submit_button("Save Pending Deal"):
                supabase.table('deals_pending').insert({
                    "client_name": p_client, "property_details": p_details, 
                    "token_amount": p_token, "expected_date": str(p_date), "agent_name": user_name
                }).execute()
                st.success("Pending Deal Recorded!")

    # --- 8. HISTORY ---
    elif page == "hist_h":
        st.subheader("📋 Gharon ka Record")
        res = supabase.table('house_inventory').select("*").execute()
        if res.data: st.dataframe(pd.DataFrame(res.data), use_container_width=True)

    elif page == "hist_deals":
        st.subheader("📂 Deals History")
        t1, t2 = st.tabs(["Pending Deals", "Done Deals"])
        with t1:
            res_p = supabase.table('deals_pending').select("*").execute()
            if res_p.data: st.dataframe(pd.DataFrame(res_p.data))
        with t2:
            res_d = supabase.table('deals_done').select("*").execute()
            if res_d.data: st.dataframe(pd.DataFrame(res_d.data))

else:
    st.info("Sidebar mein sahi Access Code dalen.")
