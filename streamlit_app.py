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

# Custom CSS for Professional Look
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-metric-label] { font-weight: bold; color: #FF4B4B ! aspiration; }
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    .stButton>button { border-radius: 5px; height: 3em; width: 100%; background-color: #262730; color: white; border: 1px solid #4B4B4B; }
    .stButton>button:hover { border: 1px solid #FF4B4B; color: #FF4B4B; }
    [data-testid="stMetricValue"] { font-size: 28px; color: #FF4B4B; }
    </style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
def delete_record(table_name, record_id):
    supabase.table(table_name).delete().eq("id", record_id).execute()
    st.warning(f"Record ID {record_id} delete kar diya gaya hai.")
    st.rerun()

def update_record(table_name, record_id, data_dict):
    supabase.table(table_name).update(data_dict).eq("id", record_id).execute()
    st.success(f"Record ID {record_id} update ho gaya!")
    st.rerun()

# --- 4. HEADER ---
st.markdown("""
    <div style="text-align: center; background: linear-gradient(90deg, #1E1E1E 0%, #323232 100%); padding: 25px; border-radius: 15px; border-bottom: 4px solid #FF4B4B; margin-bottom: 25px;">
        <h1 style="color: #FF4B4B; margin: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; letter-spacing: 1px;">DEEWARY.COM</h1>
        <p style="color: #CCCCCC; margin: 0; font-size: 18px; font-weight: 300;">PREMIUM RENTAL PROPERTY MANAGEMENT | MANAGER PORTAL</p>
    </div>
""", unsafe_allow_html=True)

# --- 5. SIDEBAR & USER AUTH ---
st.sidebar.markdown("<h2 style='text-align: center; color: #FF4B4B;'>🔐 STAFF LOGIN</h2>", unsafe_allow_html=True)
user_name = st.sidebar.selectbox("Select User", ["Umer (Manager)", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "admin786":
    st.sidebar.markdown("---")
    
    if "menu" not in st.session_state:
        st.session_state.menu = "🏠 Dashboard"

    def set_menu(name):
        st.session_state.menu = name

    # Navigation Buttons
    st.sidebar.subheader("🚀 Navigation")
    if st.sidebar.button("📊 Dashboard Overview", use_container_width=True): set_menu("🏠 Dashboard")
    
    st.sidebar.subheader("➕ New Entries")
    if st.sidebar.button("🏡 Add House/Shop", use_container_width=True): set_menu("🏠 Ghar Entry")
    if st.sidebar.button("👤 Add New Client", use_container_width=True): set_menu("👤 Client Entry")
    if st.sidebar.button("💬 Discussion Note", use_container_width=True): set_menu("💬 Discussion")
    
    st.sidebar.subheader("📂 Records & Logs")
    if st.sidebar.button("📋 House Inventory", use_container_width=True): set_menu("📋 House History")
    if st.sidebar.button("👥 Client Database", use_container_width=True): set_menu("👥 Client History")
    if st.sidebar.button("💰 Done Deals", use_container_width=True): set_menu("💰 Done History")

    menu = st.session_state.menu

    # --- 6. DASHBOARD (PROFESSIONAL LOOK WITH USER TRACKING) ---
    if menu == "🏠 Dashboard":
        st.markdown(f"### 📊 System Status: <span style='color:#FF4B4B'>{user_name}</span>", unsafe_allow_html=True)
        
        # Fetch Data
        h_data = supabase.table('house_inventory').select("*").execute()
        c_data = supabase.table('client_leads').select("*").execute()
        d_data = supabase.table('deals_done').select("*").execute()

        df_h = pd.DataFrame(h_data.data) if h_data.data else pd.DataFrame()
        df_c = pd.DataFrame(c_data.data) if c_data.data else pd.DataFrame()
        df_d = pd.DataFrame(d_data.data) if d_data.data else pd.DataFrame()

        # KPIs
        c1, c2, col3, col4 = st.columns(4)
        with c1:
            st.metric("Total Inventory", len(df_h))
        with c2:
            avail = len(df_h[df_h['status'] == 'Available']) if not df_h.empty else 0
            st.metric("Available Properties", avail)
        with col3:
            st.metric("Total Clients", len(df_c))
        with col4:
            st.metric("Deals Completed", len(df_d))

        st.markdown("---")
        
        # Daily Progress with User Mention
        t1, t2 = st.columns(2)
        with t1:
            st.markdown("#### 🏠 Recently Added Properties")
            if not df_h.empty:
                # 'added_by' column shows who added it
                st.dataframe(df_h[['added_by', 'owner_name', 'location', 'rent', 'status']].head(10), use_container_width=True)
            else: st.info("No data available.")

        with t2:
            st.markdown("#### 👥 New Client Leads")
            if not df_c.empty:
                st.dataframe(df_c[['added_by', 'client_name', 'budget', 'status']].head(10), use_container_width=True)
            else: st.info("No data available.")

    # --- 7. FORMS & HISTORY (Same as before but polished) ---
    elif menu == "🏠 Ghar Entry":
        st.subheader("🏡 Property Entry Form")
        with st.form("h_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                o_name = st.text_input("Owner Name")
                loc = st.text_input("Location")
                rent = st.number_input("Demand", min_value=0)
            with col2:
                o_con = st.text_input("Contact Number")
                status = st.selectbox("Status", ["Available", "Rent Out"])
                size = st.text_input("Size")
            if st.form_submit_button("Submit Property"):
                supabase.table('house_inventory').insert({
                    "owner_name": o_name, "location": loc, "rent": rent, 
                    "contact": o_con, "status": status, "size": size, "added_by": user_name
                }).execute()
                st.success(f"Property added successfully by {user_name}!")

    # [History Section with Edit/Delete]
    def show_history(table_name):
        res = supabase.table(table_name).select("*").order('id', desc=True).execute()
        if res.data:
            df = pd.DataFrame(res.data)
            st.dataframe(df, use_container_width=True)
            st.markdown("---")
            c_edit, c_del = st.columns(2)
            with c_del:
                id_to_del = st.number_input("Enter ID to Delete", min_value=0, step=1, key=f"d_{table_name}")
                if st.button("🗑️ Delete Permanently", key=f"bd_{table_name}"):
                    delete_record(table_name, id_to_del)
            with c_edit:
                id_to_edit = st.number_input("Enter ID to Edit", min_value=0, step=1, key=f"e_{table_name}")
                if id_to_edit > 0:
                    rec = next((item for item in res.data if item["id"] == id_to_edit), None)
                    if rec:
                        with st.expander(f"Update Details for ID {id_to_edit}"):
                            with st.form(f"ef_{table_name}"):
                                new_data = {}
                                for k, v in rec.items():
                                    if k not in ['id', 'created_at', 'added_by']:
                                        new_data[k] = st.text_input(f"{k}", value=str(v))
                                if st.form_submit_button("Update Record"):
                                    update_record(table_name, id_to_edit, new_data)

    elif menu == "📋 House History": show_history('house_inventory')
    elif menu == "👥 Client History": show_history('client_leads')
    elif menu == "💰 Done History": show_history('deals_done')

else:
    if pwd != "": st.error("Access Denied: Invalide Password")

st.divider()
st.caption(f"Portal Managed by: {user_name} | Deewary.com © {datetime.now().year}")
