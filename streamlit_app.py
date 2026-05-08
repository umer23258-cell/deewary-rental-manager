import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# --- 1. CONFIG & CONNECTION ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Deewary Premium CRM", layout="wide", page_icon="🏠")

# --- 2. CUSTOM CSS (Professional Dark & Orange Theme) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    [data-testid="stMetric"] { background-color: #1E2130; border-left: 5px solid #FF4B4B; padding: 15px; border-radius: 10px; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #FF4B4B; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
def save_to_supabase(table, data):
    try:
        supabase.table(table).insert(data).execute()
        st.success("✅ Record Saved Successfully!")
    except Exception as e:
        st.error(f"❌ Error: {e}")

# --- 4. NAVIGATION TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["🏠 House Inventory", "👥 Client Leads", "🚗 Visit Log", "🔐 Admin Panel"])

# --- TAB 1: HOUSE INVENTORY (Owner & Property Details) ---
with tab1:
    st.subheader("Add New Property Entry")
    with st.form("house_entry_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            h_owner = st.text_input("Owner Name")
            h_contact = st.text_input("Owner Contact")
            h_location = st.text_input("Area / Location")
        with c2:
            h_marla = st.number_input("Marla / Size", min_value=0.0)
            h_rent = st.number_input("Rent Amount", min_value=0)
            h_floor = st.selectbox("Floor", ["Ground", "First", "Second", "Full House", "Basement"])
        with c3:
            h_beds = st.slider("Bedrooms", 1, 10, 3)
            h_gas = st.checkbox("Gas Available")
            h_water = st.checkbox("Water Available")
            h_elec = st.checkbox("Electricity Available")
            
        h_visit_time = st.text_input("Available Visit Time (e.g. 2pm to 6pm)")
        h_status = st.selectbox("Property Status", ["Available", "Rented", "Maintenance"])
        
        if st.form_submit_button("Save Property"):
            payload = {
                "owner_name": h_owner, "contact": h_contact, "location": h_location,
                "marla": h_marla, "rent": h_rent, "floor": h_floor, "beds": h_beds,
                "gas": h_gas, "water": h_water, "electricity": h_elec,
                "visit_time": h_visit_time, "status": h_status
            }
            save_to_supabase("house_inventory", payload)

# --- TAB 2: CLIENT LEADS (Requirement Matching) ---
with tab2:
    st.subheader("Add New Client Requirement")
    with st.form("client_lead_form", clear_on_submit=True):
        cl1, cl2 = st.columns(2)
        with cl1:
            cl_name = st.text_input("Client Name")
            cl_contact = st.text_input("Client Contact")
            cl_budget = st.number_input("Budget Range", min_value=0)
            cl_beds = st.number_input("Required Beds", min_value=1)
        with cl2:
            cl_marla = st.text_input("Required Size (Marla)")
            cl_area = st.text_input("Preferred Area")
            cl_portion = st.selectbox("Preferred Portion", ["Ground", "First", "Upper", "Full House"])
        
        cl_others = st.text_area("Other Requirements (e.g. School nearby, Separate Gate)")
        
        if st.form_submit_button("Save Client Lead"):
            payload = {
                "name": cl_name, "contact": cl_contact, "budget": cl_budget,
                "beds": cl_beds, "marla": cl_marla, "area": cl_area,
                "portion": cl_portion, "other_req": cl_others
            }
            save_to_supabase("client_leads", payload)

# --- TAB 3: VISIT LOG (Staff & Activity Tracking) ---
with tab3:
    st.subheader("Log a Property Visit")
    with st.form("visit_form", clear_on_submit=True):
        v1, v2 = st.columns(2)
        with v1:
            v_client = st.text_input("Client Name / ID")
            v_house = st.text_input("House Address / ID")
        with v2:
            v_staff = st.selectbox("Staff Member (Visited By)", ["Sawer Khan", "Tariq Hussain", "Anas"])
            v_date = st.date_input("Visit Date", datetime.now())
        
        v_feedback = st.text_input("Client Feedback (e.g. Liked kitchen, Rent too high)")
        
        if st.form_submit_button("Log Visit"):
            payload = {
                "client": v_client, "house": v_house, "staff": v_staff,
                "date": str(v_date), "feedback": v_feedback
            }
            save_to_supabase("visit_logs", payload)

# --- TAB 4: ADMIN PANEL ---
with tab4:
    st.subheader("🔐 Master Control")
    pwd = st.text_input("Admin Password", type="password")
    if pwd == st.secrets.get("ADMIN_PASSWORD", "admin123"):
        view_mode = st.radio("View Data", ["Properties", "Clients", "Visits"], horizontal=True)
        
        if view_mode == "Properties":
            res = supabase.table("house_inventory").select("*").execute()
            st.dataframe(pd.DataFrame(res.data), use_container_width=True)
        elif view_mode == "Clients":
            res = supabase.table("client_leads").select("*").execute()
            st.dataframe(pd.DataFrame(res.data), use_container_width=True)
        elif view_mode == "Visits":
            res = supabase.table("visit_logs").select("*").execute()
            st.dataframe(pd.DataFrame(res.data), use_container_width=True)
    else:
        st.warning("Enter correct password to view records.")

# --- FOOTER ---
st.divider()
st.markdown(f"<div style='text-align: center; color: grey;'>Deewary.com ERP | Developed for Anas | Staff: Sawer Khan & Tariq Hussain</div>", unsafe_allow_html=True)
