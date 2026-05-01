import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
import plotly.express as px
from fpdf import FPDF
import io

# --- 1. SUPABASE SETUP ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Deewary CRM", layout="wide", page_icon="🏢")

# Hide Streamlit UI
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# --- 3. DATA HELPERS ---
def get_data(table):
    try:
        res = supabase.table(table).select("*").execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except: return pd.DataFrame()

# --- 4. HEADER ---
st.markdown("""
    <div style="text-align: center; background-color: #1E1E1E; padding: 20px; border-radius: 15px; border: 2px solid #FF4B4B;">
        <h1 style="color: #FF4B4B; margin: 0; font-family: 'Arial Black';">DEEWARY PROPERTY MANAGER</h1>
        <p style="color: white; letter-spacing: 2px;">PERSONALIZED STAFF DASHBOARD</p>
    </div>
""", unsafe_allow_html=True)

# --- 5. STAFF LOGIN & FILTERING ---
st.sidebar.title("🔐 Staff Access")
user_name = st.sidebar.selectbox("Apna Naam Select Karen", ["Anas", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "admin786":
    # Sidebar Sections
    st.sidebar.markdown(f"### 👤 Welcome, {user_name}!")
    st.sidebar.markdown("---")
    
    st.sidebar.markdown("### 📝 DATA ENTRY")
    entry_menu = st.sidebar.radio("Nayi Entry Karen:", [
        "🏠 Ghar ki Entry", 
        "👤 Client ki Entry", 
        "🤝 Deal Entry"
    ])

    st.sidebar.divider()
    
    st.sidebar.markdown("### 📜 YOUR RECORDS")
    history_menu = st.sidebar.radio("Apni History Dekhen:", [
        "📊 My Daily Progress",
        "📋 My Inventory History",
        "⏳ My Pending Deals",
        "✅ My Done Deals"
    ])

    # --- 6. GLOBAL DATA FILTERING (User ke naam par filter) ---
    df_h_all = get_data('house_inventory')
    df_d_all = get_data('deals')
    df_c_all = get_data('client_leads')

    # Filtering for the selected staff member
    my_houses = df_h_all[df_h_all['added_by'] == user_name] if not df_h_all.empty else pd.DataFrame()
    my_deals = df_d_all[df_d_all['staff_name'] == user_name] if not df_d_all.empty else pd.DataFrame()
    my_clients = df_c_all[df_c_all['added_by'] == user_name] if not df_c_all.empty else pd.DataFrame()

    # --- 7. DATA ENTRY FORMS ---
    if entry_menu == "🏠 Ghar ki Entry":
        st.subheader(f"🏡 Naye Ghar ki Entry (By: {user_name})")
        with st.form("h_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                o_name = st.text_input("Owner Name")
                loc = st.text_input("Location")
            with col2:
                rent = st.number_input("Demand Rent", min_value=0)
                status = st.selectbox("Status", ["Available", "Rent Out"])
            if st.form_submit_button("Save Property"):
                supabase.table('house_inventory').insert({"owner_name": o_name, "location": loc, "rent": rent, "status": status, "added_by": user_name}).execute()
                st.success("Record Saved!")

    elif entry_menu == "👤 Client ki Entry":
        st.subheader(f"👤 Client Requirement (By: {user_name})")
        with st.form("c_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                c_name = st.text_input("Client Name")
                req = st.text_input("Location Required")
            with col2:
                budget = st.number_input("Budget", min_value=0)
            if st.form_submit_button("Save Client"):
                supabase.table('client_leads').insert({"client_name": c_name, "req_location": req, "budget": budget, "added_by": user_name}).execute()
                st.success("Client Saved!")

    elif entry_menu == "🤝 Deal Entry":
        st.subheader(f"🤝 New Deal Record (By: {user_name})")
        with st.form("d_form", clear_on_submit=True):
            d1, d2 = st.columns(2)
            with d1:
                cl_name = st.text_input("Client Name")
                h_id = st.text_input("House ID")
            with d2:
                d_status = st.selectbox("Deal Status", ["Pending", "Done"])
                d_amt = st.number_input("Amount", min_value=0)
            if st.form_submit_button("Submit Deal"):
                supabase.table('deals').insert({"client_name": cl_name, "house_id": h_id, "deal_status": d_status, "amount": d_amt, "staff_name": user_name, "date": str(datetime.now().date())}).execute()
                st.success("Deal Saved!")

    # --- 8. PERSONALIZED DASHBOARD & HISTORY ---
    st.markdown(f"### 📍 Overview for: {user_name}")
    st.divider()

    if history_menu == "📊 My Daily Progress":
        st.subheader(f"🚀 {user_name}'s Performance Dashboard")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("My Properties", len(my_houses))
        m2.metric("My Pending Deals", len(my_deals[my_deals['deal_status']=='Pending']) if not my_deals.empty else 0)
        m3.metric("My Done Deals", len(my_deals[my_deals['deal_status']=='Done']) if not my_deals.empty else 0)
        
        if not my_houses.empty:
            fig = px.pie(my_houses, names='status', title="Inventory Status", color_discrete_sequence=['#FF4B4B', '#00CC96'])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Filhal aapka koi data nahi hai.")

    elif history_menu == "📋 My Inventory History":
        st.subheader("📋 My Property Entries")
        st.dataframe(my_houses, use_container_width=True)

    elif history_menu == "⏳ My Pending Deals":
        st.subheader("⏳ My Active Pending Deals")
        if not my_deals.empty:
            st.dataframe(my_deals[my_deals['deal_status'] == 'Pending'], use_container_width=True)
        else: st.info("Koi pending deal nahi mili.")

    elif history_menu == "✅ My Done Deals":
        st.subheader("✅ My Closed Deals History")
        if not my_deals.empty:
            st.dataframe(my_deals[my_deals['deal_status'] == 'Done'], use_container_width=True)
        else: st.info("Abhi tak koi deal close nahi hui.")

else:
    if pwd != "": st.error("Access Code Ghalat Hai!")

st.divider()
st.caption(f"© {datetime.now().year} Deewary.com | Filtered View Enabled")
