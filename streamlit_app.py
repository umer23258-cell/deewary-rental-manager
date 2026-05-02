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

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    [data-testid="stMetricValue"] { font-size: 35px; color: #FF4B4B; }
    .stButton>button { border-radius: 8px; border: 1px solid #4B4B4B; transition: 0.3s; }
    .stButton>button:hover { border: 1px solid #FF4B4B; color: #FF4B4B; background-color: #1E1E1E; }
    .stDataFrame { border: 1px solid #333; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
def delete_record(table_name, record_id):
    supabase.table(table_name).delete().eq("id", record_id).execute()
    st.warning(f"ID {record_id} delete kar di gayi hai.")
    st.rerun()

def update_record(table_name, record_id, data_dict):
    supabase.table(table_name).update(data_dict).eq("id", record_id).execute()
    st.success(f"ID {record_id} update ho gayi!")
    st.rerun()

# --- 4. HEADER ---
st.markdown("""
    <div style="text-align: center; background: linear-gradient(90deg, #1E1E1E 0%, #323232 100%); padding: 30px; border-radius: 15px; border-bottom: 5px solid #FF4B4B;">
        <h1 style="color: #FF4B4B; margin: 0; font-family: 'Arial Black';">DEEWARY.COM</h1>
        <p style="color: white; letter-spacing: 3px; font-size: 18px;">PREMIUM RENTAL PROPERTY MANAGEMENT | MANAGER: UMER</p>
    </div>
""", unsafe_allow_html=True)

# --- 5. SIDEBAR & ACCESS ---
st.sidebar.title("🔐 Staff Access")
user_name = st.sidebar.selectbox("User Select Karen", ["Umer (Manager)", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "admin786":
    st.sidebar.markdown("---")
    if "menu" not in st.session_state:
        st.session_state.menu = "🏠 Dashboard"

    def set_menu(name):
        st.session_state.menu = name

    # Professional Sidebar Buttons
    st.sidebar.subheader("🚀 Operations")
    if st.sidebar.button("📊 Dashboard Overview", use_container_width=True): set_menu("🏠 Dashboard")
    if st.sidebar.button("🏠 Add House/Shop", use_container_width=True): set_menu("🏠 Ghar Entry")
    if st.sidebar.button("👤 Add New Client", use_container_width=True): set_menu("👤 Client Entry")
    if st.sidebar.button("🚶 Add Property Visit", use_container_width=True): set_menu("🚶 Visit Entry")
    if st.sidebar.button("💬 Discussion Log", use_container_width=True): set_menu("💬 Discussion")
    
    st.sidebar.subheader("📂 View Records")
    if st.sidebar.button("📋 House Inventory", use_container_width=True): set_menu("📋 House History")
    if st.sidebar.button("👥 Client Database", use_container_width=True): set_menu("👥 Client History")
    if st.sidebar.button("📅 Visit History", use_container_width=True): set_menu("📅 Visit History")
    if st.sidebar.button("💰 Done Deals", use_container_width=True): set_menu("💰 Done History")

    menu = st.session_state.menu

    # --- 6. DASHBOARD ---
    if menu == "🏠 Dashboard":
        st.subheader(f"👋 Welcome, {user_name}")
        
        # Data Fetching
        h_data = supabase.table('house_inventory').select("*").execute()
        c_data = supabase.table('client_leads').select("*").execute()
        v_data = supabase.table('property_visits').select("*").execute() # Nayi Table
        d_data = supabase.table('deals_done').select("*").execute()
        
        df_h = pd.DataFrame(h_data.data) if h_data.data else pd.DataFrame()
        df_c = pd.DataFrame(c_data.data) if c_data.data else pd.DataFrame()
        df_v = pd.DataFrame(v_data.data) if v_data.data else pd.DataFrame()
        df_d = pd.DataFrame(d_data.data) if d_data.data else pd.DataFrame()

        # Stats Cards
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total Houses", len(df_h))
        kpi2.metric("Total Clients", len(df_c))
        kpi3.metric("Property Visits", len(df_v))
        kpi4.metric("Deals Done", len(df_d))

        st.markdown("---")
        
        st.markdown("### 📅 Recent Activity Tracking")
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.write("#### 🚶 Latest Visits")
            if not df_v.empty:
                st.dataframe(df_v[['added_by', 'client_name', 'property_detail', 'visit_date']].head(10), use_container_width=True)
            else: st.info("No visits recorded yet.")
        
        with col_b:
            st.write("#### 🏠 New Houses")
            if not df_h.empty:
                st.dataframe(df_h[['added_by', 'owner_name', 'location', 'status']].head(10), use_container_width=True)

    # --- 7. NEW VISIT ENTRY FORM ---
    elif menu == "🚶 Visit Entry":
        st.subheader("🚶 Record a New Property Visit")
        with st.form("v_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                v_client = st.text_input("Client Name")
                v_prop = st.text_area("Property Detail (Which house shown?)")
            with c2:
                v_date = st.date_input("Visit Date")
                v_feedback = st.text_input("Client Feedback (Optional)")
            if st.form_submit_button("Save Visit Record"):
                supabase.table('property_visits').insert({
                    "client_name": v_client, "property_detail": v_prop, 
                    "visit_date": str(v_date), "feedback": v_feedback, "added_by": user_name
                }).execute()
                st.success(f"Visit saved by {user_name}!")

    # --- 8. OTHER FORMS (House, Client, Discussion) ---
    elif menu == "🏠 Ghar Entry":
        st.subheader("🏡 Property Detail Form")
        with st.form("h_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                o_name = st.text_input("Owner Name")
                o_con = st.text_input("Contact")
                loc = st.text_input("Location")
            with c2:
                rent = st.number_input("Demand Rent", min_value=0)
                status = st.selectbox("Status", ["Available", "Rent Out"])
                portion = st.selectbox("Portion", ["Full", "Ground", "First", "Shop", "Office"])
            if st.form_submit_button("Save Property"):
                supabase.table('house_inventory').insert({
                    "owner_name": o_name, "contact": o_con, "location": loc, 
                    "rent": rent, "status": status, "portion": portion, "added_by": user_name
                }).execute()
                st.success(f"Saved! Added by {user_name}")

    elif menu == "👤 Client Entry":
        st.subheader("👤 Client Requirement Form")
        with st.form("c_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                cn = st.text_input("Client Name")
                cc = st.text_input("Contact")
            with c2:
                cb = st.number_input("Budget", min_value=0)
                cl = st.text_input("Req. Location")
            if st.form_submit_button("Save Client"):
                supabase.table('client_leads').insert({
                    "client_name": cn, "contact": cc, "budget": cb, 
                    "req_location": cl, "status": "Searching", "added_by": user_name
                }).execute()
                st.success(f"Client recorded by {user_name}")

    # --- 9. HISTORY SECTIONS ---
    def show_history(table_name):
        res = supabase.table(table_name).select("*").order('id', desc=True).execute()
        if res.data:
            df = pd.DataFrame(res.data)
            st.dataframe(df, use_container_width=True)
            st.markdown("---")
            e1, e2 = st.columns(2)
            with e1:
                del_id = st.number_input("ID to Delete", min_value=0, step=1, key=f"d_{table_name}")
                if st.button("🗑️ Delete", key=f"bd_{table_name}"):
                    delete_record(table_name, del_id)
            with e2:
                edit_id = st.number_input("ID to Edit", min_value=0, step=1, key=f"e_{table_name}")
                if edit_id > 0:
                    rec = next((item for item in res.data if item["id"] == edit_id), None)
                    if rec:
                        with st.expander(f"Edit ID {edit_id}"):
                            with st.form(f"ef_{table_name}"):
                                new_vals = {}
                                for k, v in rec.items():
                                    if k not in ['id', 'created_at', 'added_by']:
                                        new_vals[k] = st.text_input(f"{k}", value=str(v))
                                if st.form_submit_button("Update"):
                                    update_record(table_name, edit_id, new_vals)

    if menu == "📋 House History": show_history('house_inventory')
    elif menu == "👥 Client History": show_history('client_leads')
    elif menu == "📅 Visit History": show_history('property_visits')
    elif menu == "💰 Done History": show_history('deals_done')

else:
    if pwd != "": st.error("Ghalat Password!")

st.divider()
st.caption(f"Portal Managed by: {user_name} | © {datetime.now().year} Deewary.com")
