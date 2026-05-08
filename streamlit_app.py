import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
import plotly.express as px

# --- 1. CONNECTION ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("Supabase Connection Fail!")
    st.stop()

# --- 2. PAGE CONFIG & STYLE ---
st.set_page_config(page_title="Deewary Hub Pro", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .stApp { background-color: #05070A; color: #E0E0E0; }
    [data-testid="stMetric"] { background-color: #1E2130; border-left: 5px solid #FF4B4B; padding: 15px; border-radius: 10px; }
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 75, 75, 0.3);
        padding: 20px; border-radius: 15px; text-align: center;
    }
    .stButton>button {
        background: linear-gradient(90deg, #FF4B4B 0%, #FF8080 100%);
        color: white; border: none; border-radius: 8px; font-weight: bold; width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIN SYSTEM ---
if "authenticated" not in st.session_state:
    st.session_state.update({"authenticated": False, "user_role": None, "user_name": None})

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>DEEWARY PRO</h1>", unsafe_allow_html=True)
        user = st.selectbox("Select User", ["Sawer Khan", "Tariq Hussain", "Anas (Admin)"])
        pwd = st.text_input("Password", type="password")
        if st.button("Unlock System"):
            if user == "Anas (Admin)" and pwd == "admin786":
                st.session_state.update({"authenticated": True, "user_role": "admin", "user_name": "Anas"})
                st.rerun()
            elif (user == "Sawer Khan" and pwd == "sawer123") or (user == "Tariq Hussain" and pwd == "tariq123"):
                st.session_state.update({"authenticated": True, "user_role": "staff", "user_name": user})
                st.rerun()
            else: st.error("Access Denied!")
    st.stop()

# --- 4. DATA FETCHING ---
def fetch_data(table):
    try:
        res = supabase.table(table).select("*").order('created_at', desc=True).execute()
        return pd.DataFrame(res.data)
    except: return pd.DataFrame()

df_h = fetch_data('house_inventory')
df_c = fetch_data('client_leads')
df_v = fetch_data('visit_logs')

# --- 5. TABS ---
tab_dash, tab_entry, tab_mgmt = st.tabs(["📊 Dashboard (Live)", "📝 Nayi Entry", "📂 Full History & Edit"])

# --- TAB 1: DASHBOARD (Logic: Sirf Available Items dikhayega) ---
with tab_dash:
    st.markdown("## Live Inventory Stock")
    
    # Filtering only 'Available' properties for Dashboard
    if not df_h.empty and 'status' in df_h.columns:
        available_houses = df_h[df_h['status'] == 'Available']
        rented_houses = df_h[df_h['status'] == 'Rented']
    else:
        available_houses = pd.DataFrame()
        rented_houses = pd.DataFrame()

    c1, c2, c3, c4 = st.columns(4)
    with c1: 
        st.markdown(f"<div class='metric-card'><h3>🏠 Available Houses</h3><h2>{len(available_houses)}</h2><p style='color:grey;'>Rented: {len(rented_houses)}</p></div>", unsafe_allow_html=True)
    with c2: 
        st.markdown(f"<div class='metric-card'><h3>👥 Active Leads</h3><h2>{len(df_c)}</h2></div>", unsafe_allow_html=True)
    with c3: 
        st.markdown(f"<div class='metric-card'><h3>🚗 Total Visits</h3><h2>{len(df_v)}</h2></div>", unsafe_allow_html=True)
    with c4:
        # Business Volume from Rented Properties
        rev = rented_houses['rent'].sum() if not rented_houses.empty else 0
        st.markdown(f"<div class='metric-card'><h3>💰 Rented Volume</h3><h2>{rev:,.0f}</h2></div>", unsafe_allow_html=True)

    st.divider()
    if not available_houses.empty:
        st.subheader("📍 Quick Available List")
        st.dataframe(available_houses[['owner_name', 'location', 'rent', 'marla', 'beds', 'water', 'added_by']], use_container_width=True)

# --- TAB 2: ENTRY CENTER ---
with tab_entry:
    mode = st.radio("Add New:", ["Property (Ghar)", "Client (Gahak)", "Visit Log"], horizontal=True)
    
    if mode == "Property (Ghar)":
        with st.form("house_form"):
            ca, cb, cc = st.columns(3)
            with ca:
                o_n = st.text_input("Owner Name")
                o_c = st.text_input("Contact")
                o_l = st.text_input("Location")
            with cb:
                rnt = st.number_input("Monthly Rent", min_value=0)
                mrl = st.text_input("Marla (Size)")
                flr = st.selectbox("Floor", ["Ground", "First", "Upper", "Full House"])
                bed = st.number_input("Bedrooms", 1, 15)
            with cc:
                wtr = st.selectbox("Water", ["Yes", "Boring", "Line Water", "Tanker", "No"])
                gas = st.selectbox("Gas", ["Separate", "Common", "No"])
                ele = st.selectbox("Electricity", ["Separate", "Sub Meter"])
            if st.form_submit_button("Save Property"):
                supabase.table('house_inventory').insert({"owner_name":o_n,"contact":o_c,"location":o_l,"rent":rnt,"marla":mrl,"floor":flr,"beds":bed,"water":wtr,"gas":gas,"electricity":ele,"status":"Available","added_by":st.session_state.user_name}).execute()
                st.success("Ghar Dashboard mein add ho gaya!")
                st.rerun()

    elif mode == "Client (Gahak)":
        with st.form("client_form"):
            c1, c2 = st.columns(2)
            with c1:
                cn = st.text_input("Client Name"); cc = st.text_input("Contact")
                cb = st.number_input("Budget", min_value=0); cbd = st.number_input("Beds", 1, 15)
            with c2:
                cm = st.text_input("Marla"); ca = st.text_input("Area")
                cp = st.selectbox("Portion", ["Ground", "First", "Full", "Any"])
            if st.form_submit_button("Save Client"):
                supabase.table('client_leads').insert({"name":cn,"contact":cc,"budget":cb,"beds":cbd,"marla":cm,"area":ca,"portion":cp,"added_by":st.session_state.user_name}).execute()
                st.success("Client Saved!"); st.rerun()

    elif mode == "Visit Log":
        with st.form("visit_form"):
            v_cl = st.text_input("Client Name"); v_h = st.text_input("House Address")
            v_f = st.text_area("Feedback")
            if st.form_submit_button("Log Visit"):
                supabase.table('visit_logs').insert({"client":v_cl,"house":v_h,"staff":st.session_state.user_name,"feedback":v_f,"date":str(datetime.now().date())}).execute()
                st.success("Visit Recorded!"); st.rerun()

# --- TAB 3: DATA MANAGEMENT (HISTORY) ---
with tab_mgmt:
    target = st.selectbox("Select View", ["house_inventory", "client_leads", "visit_logs"])
    df_raw = fetch_data(target)
    
    if not df_raw.empty:
        # Search
        q = st.text_input("🔍 Search History (Find Rented or Available)...")
        if q: df_raw = df_raw[df_raw.astype(str).apply(lambda x: x.str.contains(q, case
