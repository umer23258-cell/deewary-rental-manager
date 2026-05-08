import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# --- 1. CONNECTION ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Deewary Hub", layout="wide", page_icon="🏢")

# --- 2. THEME & STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    h1, h2, h3 { color: #FF4B4B !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #1E2130; 
        color: white; 
        border-radius: 5px; 
        padding: 8px 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
def get_history(table_name):
    try:
        res = supabase.table(table_name).select("*").order('created_at', desc=True).execute()
        return pd.DataFrame(res.data)
    except:
        return pd.DataFrame()

# --- 4. NAVIGATION ---
tab_home, tab_house, tab_client, tab_visit = st.tabs([
    "📊 Dashboard", "🏠 Ghar ki Entry", "👥 Client Entry", "🚗 Visit & Staff History"
])

# --- DASHBOARD ---
with tab_home:
    st.title("DEEWARY ACTION CENTER")
    c1, c2, c3 = st.columns(3)
    df_h = get_history('house_inventory')
    df_c = get_history('client_leads')
    df_v = get_history('visit_logs')
    
    c1.metric("Total Houses", len(df_h))
    c2.metric("Total Clients", len(df_c))
    c3.metric("Visits Done", len(df_v))
    
    st.divider()
    st.subheader("Recent Updates")
    st.write("Current Staff on Duty: **Sawer Khan, Tariq Hussain**")

# --- HOUSE ENTRY ---
with tab_house:
    st.subheader("Naya Ghar Register Karein")
    with st.form("house_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            h_name = st.text_input("Owner Name")
            h_cont = st.text_input("Contact Number")
            h_loc = st.text_input("Location")
            h_rent = st.number_input("Rent", min_value=0)
        with col2:
            h_marla = st.text_input("Marla")
            h_floor = st.selectbox("Floor", ["Ground", "First", "Second", "Full House"])
            h_bed = st.number_input("Bedrooms", 1, 10)
            h_v_time = st.text_input("Visit Time (e.g. 10am-5pm)")
        with col3:
            h_water = st.selectbox("Water Status", ["Yes", "No", "Boring", "Line Water"])
            h_gas = st.selectbox("Gas Status", ["No", "Separate Meter", "Common Meter"])
            h_elec = st.selectbox("Electricity", ["Separate Meter", "Sub Meter"])
            h_status = st.selectbox("Current Status", ["Available", "Rented", "Pending"])
        
        if st.form_submit_button("Save Property"):
            data = {
                "owner_name": h_name, "contact": h_cont, "location": h_loc, "rent": h_rent,
                "marla": h_marla, "floor": h_floor, "beds": h_bed, "visit_time": h_v_time,
                "water": h_water, "gas": h_gas, "electricity": h_elec, "status": h_status
            }
            supabase.table('house_inventory').insert(data).execute()
            st.success("Ghar ka record save ho gaya!")
            st.rerun()
    
    st.divider()
    st.subheader("🏠 Gharon ki History")
    st.dataframe(df_h, use_container_width=True)

# --- CLIENT ENTRY ---
with tab_client:
    st.subheader("Naya Client Requirements")
    with st.form("client_form"):
        cc1, cc2 = st.columns(2)
        with cc1:
            cl_name = st.text_input("Client Name")
            cl_cont = st.text_input("Contact")
            cl_bud = st.number_input("Budget", min_value=0)
        with cc2:
            cl_marla = st.text_input("Required Marla")
            cl_portion = st.selectbox("Required Portion", ["Ground", "First", "Upper", "Full House"])
            cl_area = st.text_input("Preferred Area")
        
        cl_other = st.text_area("Other Requirements")
        
        if st.form_submit_button("Save Client"):
            data = {
                "name": cl_name, "contact": cl_cont, "budget": cl_bud, 
                "marla": cl_marla, "portion": cl_portion, "area": cl_area, "other_req": cl_other
            }
            supabase.table('client_leads').insert(data).execute()
            st.success("Client Requirement Save ho gayi!")
            st.rerun()

    st.divider()
    st.subheader("👥 Clients ki History")
    st.dataframe(df_c, use_container_width=True)

# --- VISIT & STAFF HISTORY ---
with tab_visit:
    st.subheader("Visit Log & Staff Activity")
    with st.form("visit_form"):
        vv1, vv2 = st.columns(2)
        with vv1:
            v_cl = st.text_input("Client Name")
            v_house = st.text_input("Ghar ka Address")
        with vv2:
            v_staff = st.selectbox("Staff Jisne Visit Karwaya", ["Sawer Khan", "Tariq Hussain", "Anas"])
            v_date = st.date_input("Visit Date", datetime.now())
        
        if st.form_submit_button("Record Visit"):
            data = {"client": v_cl, "house": v_house, "staff": v_staff, "date": str(v_date)}
            supabase.table('visit_logs').insert(data).execute()
            st.success("Visit Log ho gayi!")
            st.rerun()

    st.divider()
    st.subheader("🚗 Visit History")
    st.dataframe(df_v, use_container_width=True)

# --- FOOTER ---
st.divider()
st.caption(f"Deewary.com ERP | Developed for Anas | Staff: Sawer Khan & Tariq Hussain")
