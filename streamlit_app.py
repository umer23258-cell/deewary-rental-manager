import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# --- 1. CONNECTION ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Deewary Hub Pro", layout="wide", page_icon="🏢")

# --- 2. SESSION STATE ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.user_name = None

# --- 3. LOGIN INTERFACE ---
if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center; color: #FF4B4B;'>🔐 Deewary Hub Login</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        user = st.selectbox("Pehchan Select Karein", ["Sawer Khan", "Tariq Hussain", "Anas (Admin)"])
        password = st.text_input("Password", type="password")
        if st.button("System Mein Dakhil Hon"):
            if user == "Anas (Admin)" and password == "admin786":
                st.session_state.update({"authenticated": True, "user_role": "admin", "user_name": "Anas"})
                st.rerun()
            elif user == "Sawer Khan" and password == "sawer123":
                st.session_state.update({"authenticated": True, "user_role": "staff", "user_name": "Sawer Khan"})
                st.rerun()
            elif user == "Tariq Hussain" and password == "tariq123":
                st.session_state.update({"authenticated": True, "user_role": "staff", "user_name": "Tariq Hussain"})
                st.rerun()
            else:
                st.error("❌ Password Ghalat Hai!")
    st.stop()

# --- 4. DATA LOGIC (Search, Edit, Delete) ---
def fetch_filtered_data(table):
    res = supabase.table(table).select("*").order('created_at', desc=True).execute()
    df = pd.DataFrame(res.data)
    if not df.empty and st.session_state.user_role != "admin":
        # Staff ko sirf apni history dikhani hai (agar table mein 'added_by' ya 'staff' column hai)
        column = 'added_by' if 'added_by' in df.columns else 'staff'
        df = df[df[column] == st.session_state.user_name]
    return df

def manage_records(table, df):
    if df.empty:
        st.info("Filhal koi records nahi hain.")
        return

    search = st.text_input(f"🔍 Search in {table.replace('_', ' ')}...", key=f"search_{table}")
    if search:
        df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]

    st.dataframe(df, use_container_width=True)

    # Edit & Delete Logic
    with st.expander(f"🛠️ Edit / Delete Records in {table.title()}"):
        row_id = st.text_input("Enter ID to Modify", key=f"id_{table}")
        if row_id:
            c1, c2 = st.columns(2)
            if c1.button("🗑️ Delete Record", key=f"del_{table}"):
                supabase.table(table).delete().eq('id', row_id).execute()
                st.success("Record Khatam Kar Diya Gaya!")
                st.cache_data.clear()
                st.rerun()
            
            st.info("Edit karne ke liye niche fields fill karein:")
            # Yahan hum simplified edit de rahe hain, aap fields barha sakte hain
            new_status = st.selectbox("Update Status", ["Available", "Rented", "Pending", "Done Deal"], key=f"status_{table}")
            if st.button("📝 Update Status", key=f"upd_{table}"):
                supabase.table(table).update({"status": new_status}).eq('id', row_id).execute()
                st.success("Status Update Ho Gaya!")
                st.rerun()

# --- 5. MAIN INTERFACE ---
st.sidebar.title(f"Welcome, {st.session_state.user_name}")
if st.sidebar.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.rerun()

tabs = st.tabs(["🏠 Ghar Entry & History", "👥 Client Entry & History", "🚗 Visit Logs"])

# --- TAB 1: HOUSE ---
with tabs[0]:
    col_in, col_hist = st.columns([1, 2])
    with col_in:
        st.subheader("Add Property")
        with st.form("h_form"):
            h_owner = st.text_input("Owner Name")
            h_rent = st.number_input("Rent", min_value=0)
            h_loc = st.text_input("Location")
            h_gas = st.selectbox("Gas", ["No", "Separate", "Common"])
            h_water = st.selectbox("Water", ["Yes", "Boring", "Line"])
            if st.form_submit_button("Save"):
                supabase.table('house_inventory').insert({
                    "owner_name": h_owner, "rent": h_rent, "location": h_loc, 
                    "gas": h_gas, "water": h_water, "added_by": st.session_state.user_name
                }).execute()
                st.rerun()
    with col_hist:
        st.subheader("Inventory History")
        df_h = fetch_filtered_data('house_inventory')
        manage_records('house_inventory', df_h)

# --- TAB 2: CLIENT ---
with tabs[1]:
    col_in, col_hist = st.columns([1, 2])
    with col_in:
        st.subheader("Add Client")
        with st.form("c_form"):
            c_name = st.text_input("Client Name")
            c_bud = st.number_input("Budget", min_value=0)
            if st.form_submit_button("Save Client"):
                supabase.table('client_leads').insert({
                    "name": c_name, "budget": c_bud, "added_by": st.session_state.user_name
                }).execute()
                st.rerun()
    with col_hist:
        st.subheader("Client History")
        df_c = fetch_filtered_data('client_leads')
        manage_records('client_leads', df_c)

# --- TAB 3: VISITS ---
with tabs[2]:
    st.subheader("Visit Activity")
    v_col1, v_col2 = st.columns([1, 2])
    with v_col1:
        with st.form("v_form"):
            v_cl = st.text_input("Client Name")
            v_house = st.text_input("House Address")
            if st.form_submit_button("Record Visit"):
                supabase.table('visit_logs').insert({
                    "client": v_cl, "house": v_house, "staff": st.session_state.user_name, 
                    "date": str(datetime.now().date())
                }).execute()
                st.rerun()
    with v_col2:
        st.subheader("Staff Visit History")
        df_v = fetch_filtered_data('visit_logs')
        manage_records('visit_logs', df_v)

st.divider()
st.caption(f"Deewary.com | Authorized Access: {st.session_state.user_role}")
