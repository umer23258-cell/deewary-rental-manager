import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# --- 1. CONNECTION ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Deewary Hub", layout="wide", page_icon="🏢")

# --- 2. LOGIN SYSTEM LOGIC ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.user_name = None

def login_user():
    st.markdown("<h2 style='text-align: center; color: #FF4B4B;'>🔐 Deewary Staff Login</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        user = st.selectbox("Select Your Name", ["Sawer Khan", "Tariq Hussain", "Anas (Admin)"])
        password = st.text_input("Enter Password", type="password")
        if st.button("Login"):
            # Simple Password Logic (Aap secrets mein bhi rakh sakte hain)
            if user == "Anas (Admin)" and password == "admin786":
                st.session_state.authenticated = True
                st.session_state.user_role = "admin"
                st.session_state.user_name = "Anas"
                st.rerun()
            elif user == "Sawer Khan" and password == "sawer123":
                st.session_state.authenticated = True
                st.session_state.user_role = "staff"
                st.session_state.user_name = "Sawer Khan"
                st.rerun()
            elif user == "Tariq Hussain" and password == "tariq123":
                st.session_state.authenticated = True
                st.session_state.user_role = "staff"
                st.session_state.user_name = "Tariq Hussain"
                st.rerun()
            else:
                st.error("Ghalat Password!")

if not st.session_state.authenticated:
    login_user()
    st.stop()

# --- 3. GLOBAL SETUP AFTER LOGIN ---
st.sidebar.write(f"👤 Logged in as: **{st.session_state.user_name}**")
if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.rerun()

def get_history(table_name):
    try:
        res = supabase.table(table_name).select("*").order('created_at', desc=True).execute()
        return pd.DataFrame(res.data)
    except:
        return pd.DataFrame()

# --- 4. NAVIGATION ---
tabs = ["🏠 Ghar ki Entry", "👥 Client Entry", "🚗 Visit Log"]
if st.session_state.user_role == "admin":
    tabs.append("📊 Admin Dashboard")

active_tabs = st.tabs(tabs)

# --- TAB: HOUSE ENTRY ---
with active_tabs[0]:
    st.subheader("Naya Ghar Register Karein")
    with st.form("house_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            h_name = st.text_input("Owner Name")
            h_cont = st.text_input("Contact")
            h_loc = st.text_input("Location")
        with col2:
            h_rent = st.number_input("Rent", min_value=0)
            h_marla = st.text_input("Marla")
            h_floor = st.selectbox("Floor", ["Ground", "First", "Second", "Full House"])
        with col3:
            h_water = st.selectbox("Water", ["Yes", "No", "Boring", "Line Water"])
            h_gas = st.selectbox("Gas", ["No", "Separate Meter", "Common Meter"])
            h_elec = st.selectbox("Electricity", ["Separate Meter", "Sub Meter"])
        
        if st.form_submit_button("Save Property"):
            data = {
                "owner_name": h_name, "contact": h_cont, "location": h_loc, "rent": h_rent,
                "marla": h_marla, "floor": h_floor, "water": h_water, "gas": h_gas, 
                "electricity": h_elec, "added_by": st.session_state.user_name
            }
            supabase.table('house_inventory').insert(data).execute()
            st.success("Ghar save ho gaya!")

# --- TAB: CLIENT ENTRY ---
with active_tabs[1]:
    st.subheader("Naya Client Requirement")
    with st.form("client_form"):
        c1, c2 = st.columns(2)
        with c1:
            cl_name = st.text_input("Client Name")
            cl_cont = st.text_input("Contact")
        with c2:
            cl_bud = st.number_input("Budget", min_value=0)
            cl_area = st.text_input("Preferred Area")
        
        if st.form_submit_button("Save Client"):
            data = {
                "name": cl_name, "contact": cl_cont, "budget": cl_bud, 
                "area": cl_area, "added_by": st.session_state.user_name
            }
            supabase.table('client_leads').insert(data).execute()
            st.success("Client Requirement Save ho gayi!")

# --- TAB: VISIT LOG ---
with active_tabs[2]:
    st.subheader("Visit Activity")
    with st.form("visit_form"):
        v_cl = st.text_input("Client Name")
        v_house = st.text_input("Ghar ka Address")
        # Automatic staff name
        st.info(f"Staff Member: **{st.session_state.user_name}**")
        
        if st.form_submit_button("Record Visit"):
            data = {
                "client": v_cl, "house": v_house, 
                "staff": st.session_state.user_name, # Auto lock name
                "date": str(datetime.now().date())
            }
            supabase.table('visit_logs').insert(data).execute()
            st.success("Visit Record ho gayi!")

# --- TAB: ADMIN DASHBOARD (Only for Admin) ---
if st.session_state.user_role == "admin":
    with active_tabs[3]:
        st.title("📊 Master Control Panel")
        
        view = st.radio("Select View", ["All Houses", "All Clients", "All Visits"], horizontal=True)
        
        if view == "All Houses":
            df = get_history('house_inventory')
            st.dataframe(df, use_container_width=True)
        elif view == "All Clients":
            df = get_history('client_leads')
            st.dataframe(df, use_container_width=True)
        elif view == "All Visits":
            df = get_history('visit_logs')
            st.dataframe(df, use_container_width=True)
            
        st.divider()
        st.write("### Staff Performance")
        if not get_history('visit_logs').empty:
            v_counts = get_history('visit_logs')['staff'].value_counts()
            st.bar_chart(v_counts)

# --- FOOTER ---
st.divider()
st.caption(f"Deewary.com | User: {st.session_state.user_name} | Role: {st.session_state.user_role}")
