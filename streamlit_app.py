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

# Sidebar Styling
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1E1E1E; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #FF4B4B; color: white; border: none; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR NAVIGATION ---
st.sidebar.title("🏢 DEEWARY OFFICE")
user_name = st.sidebar.selectbox("Apna Naam Select Karen", ["Anas", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "admin786":
    st.sidebar.divider()
    if st.sidebar.button("📊 DAILY DASHBOARD"): st.session_state.page = "dash"
    
    st.sidebar.subheader("➕ NAYI ENTRY")
    if st.sidebar.button("🏠 Ghar ki Entry"): st.session_state.page = "add_h"
    if st.sidebar.button("👤 Client ki Entry"): st.session_state.page = "add_c"
    if st.sidebar.button("⏳ Deal Pending"): st.session_state.page = "add_p"
    if st.sidebar.button("✅ Deal Done"): st.session_state.page = "add_d"
    
    st.sidebar.subheader("📜 HISTORY (RECORDS)")
    if st.sidebar.button("📋 Gharon ki List"): st.session_state.page = "hist_h"
    if st.sidebar.button("👥 Clients ki List"): st.session_state.page = "hist_c"
    if st.sidebar.button("📂 Deals History"): st.session_state.page = "hist_deals"

    # --- 4. MAIN AREA LOGIC ---
    page = st.session_state.get('page', 'dash')

    # --- DASHBOARD ---
    if page == "dash":
        st.title("📊 Daily Office Dashboard")
        h_res = supabase.table('house_inventory').select("*").execute()
        c_res = supabase.table('client_leads').select("*").execute()
        p_res = supabase.table('deals_pending').select("*").execute()
        d_res = supabase.table('deals_done').select("*").execute()
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Ghar", len(h_res.data))
        c2.metric("Total Clients", len(c_res.data))
        c3.metric("Pending Deals", len(p_res.data))
        c4.metric("Deals Done ✅", len(d_res.data))
        
        st.divider()
        st.subheader("Recent Activity")
        st.write("Aaj ki naye gharon ki entries yahan nazar ayengi.")
        if h_res.data:
            st.dataframe(pd.DataFrame(h_res.data).tail(5), use_container_width=True)

    # --- GHAR KI ENTRY ---
    elif page == "add_h":
        st.header("🏠 Naye Ghar ki Entry")
        with st.form("h_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                o_name = st.text_input("Owner Name")
                o_contact = st.text_input("Contact")
                loc = st.text_input("Location")
                floor = st.selectbox("Floor", ["Ground", "First", "Second", "Full House", "Shop", "Office"])
                marla = st.text_input("Size (Marla/Kanal)")
            with col2:
                rent = st.number_input("Demand Rent", min_value=0)
                beds = st.selectbox("Beds", ["1","2","3","4","5+"])
                v_time = st.text_input("Visit Time")
                gas = st.radio("Gas", ["Yes", "No"], horizontal=True)
                water = st.radio("Water", ["Yes", "No"], horizontal=True)
                elec = st.radio("Electricity", ["Yes", "No"], horizontal=True)
            
            if st.form_submit_button("Save Property"):
                payload = {
                    "owner_name": o_name, "contact": o_contact, "location": loc, "portion": floor,
                    "marla": marla, "rent": rent, "beds": beds, "visit_time": v_time,
                    "gas": gas, "water": water, "electricity": elec, "added_by": user_name
                }
                supabase.table('house_inventory').insert(payload).execute()
                st.success("Ghar save ho gaya!")

    # --- DEAL PENDING ---
    elif page == "add_p":
        st.header("⏳ Deal Pending Karen")
        with st.form("p_form"):
            p_client = st.text_input("Client Name")
            p_prop = st.text_area("Property Details")
            p_token = st.number_input("Token Amount", min_value=0)
            p_date = st.date_input("Expected Date")
            if st.form_submit_button("Save Pending Deal"):
                supabase.table('deals_pending').insert({
                    "client_name": p_client, "property_details": p_prop, 
                    "token_amount": p_token, "expected_closing_date": str(p_date), "agent_name": user_name
                }).execute()
                st.success("Pending Deal Saved!")

    # --- HISTORY SECTIONS ---
    elif page == "hist_h":
        st.header("📋 Gharon ki List")
        res = supabase.table('house_inventory').select("*").execute()
        if res.data: st.dataframe(pd.DataFrame(res.data), use_container_width=True)

    elif page == "hist_deals":
        st.header("📂 Deals ki History")
        t1, t2 = st.tabs(["Pending", "Done"])
        with t1:
            res_p = supabase.table('deals_pending').select("*").execute()
            if res_p.data: st.dataframe(pd.DataFrame(res_p.data))
        with t2:
            res_d = supabase.table('deals_done').select("*").execute()
            if res_d.data: st.dataframe(pd.DataFrame(res_d.data))

else:
    st.markdown("<h2 style='text-align: center;'>DEEWARY PROPERTY MANAGER</h2>", unsafe_allow_html=True)
    st.info("Meharbani kar ke Sidebar mein Access Code enter karen.")
