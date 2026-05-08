import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# --- 1. CONNECTION ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except:
    st.error("Secrets missing! Please add SUPABASE_URL and SUPABASE_KEY.")
    st.stop()

# --- 2. PREMIUM MOBILE UI ---
st.set_page_config(page_title="Deewary OS", layout="wide", page_icon="📱")

st.markdown("""
    <style>
    .stApp { background: #0A0E14; color: #FFFFFF; }
    .metric-container {
        background: #161B22; border: 1px solid #30363D;
        padding: 15px; border-radius: 15px; text-align: center; margin-bottom: 10px;
    }
    .metric-value { font-size: 22px; font-weight: bold; color: #FF4B4B; }
    .metric-label { font-size: 12px; color: #8B949E; }
    .prop-card {
        background: #1C2128; border-radius: 12px; padding: 12px;
        margin-bottom: 10px; border-left: 4px solid #FF4B4B;
    }
    .stButton>button {
        background: linear-gradient(90deg, #FF4B4B, #D73A49);
        color: white; border-radius: 10px; font-weight: bold; width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. AUTHENTICATION ---
if "authenticated" not in st.session_state:
    st.session_state.update({"authenticated": False, "user_role": None, "user_name": None})

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align:center;'>🏠 DEEWARY <span style='color:#FF4B4B'>OS</span></h2>", unsafe_allow_html=True)
    user = st.selectbox("Identify Yourself", ["Sawer Khan", "Tariq Hussain", "Anas (Admin)"])
    pwd = st.text_input("Security Pin", type="password")
    if st.button("Unlock Dashboard"):
        if user == "Anas (Admin)" and pwd == "admin786":
            st.session_state.update({"authenticated": True, "user_role": "admin", "user_name": "Anas"})
            st.rerun()
        elif (user == "Sawer Khan" and pwd == "sawer123") or (user == "Tariq Hussain" and pwd == "tariq123"):
            st.session_state.update({"authenticated": True, "user_role": "staff", "user_name": user})
            st.rerun()
        else: st.error("Access Denied!")
    st.stop()

# --- 4. DATA FETCHING (With Error Handling) ---
def safe_fetch(table):
    try:
        res = supabase.table(table).select("*").order('created_at', desc=True).execute()
        return pd.DataFrame(res.data)
    except:
        return pd.DataFrame()

df_h = safe_fetch('house_inventory')
df_c = safe_fetch('client_leads')
df_v = safe_fetch('visit_logs')

# --- 5. APP TABS ---
tab1, tab2, tab3 = st.tabs(["🏠 Home", "➕ Add", "📁 Logs"])

# --- TAB 1: HOME (DASHBOARD) ---
with tab1:
    st.write(f"### Hi, {st.session_state.user_name} ✨")
    
    # Live Counts Logic
    avail_count = 0
    today_visits = 0
    if not df_h.empty and 'status' in df_h.columns:
        avail_count = len(df_h[df_h['status'] == 'Available'])
    if not df_v.empty and 'date' in df_v.columns:
        today_visits = len(df_v[df_v['date'] == str(datetime.now().date())])

    m1, m2 = st.columns(2)
    with m1:
        st.markdown(f"<div class='metric-container'><div class='metric-label'>Available</div><div class='metric-value'>{avail_count}</div></div>", unsafe_allow_html=True)
    with m2:
        st.markdown(f"<div class='metric-container'><div class='metric-label'>Visits Today</div><div class='metric-value'>{today_visits}</div></div>", unsafe_allow_html=True)

    st.markdown("#### 📍 Newest Listings")
    if not df_h.empty:
        # Show only available ones
        avail_list = df_h[df_h['status'] == 'Available'].head(5)
        for _, row in avail_list.iterrows():
            st.markdown(f"""
            <div class='prop-card'>
                <div style='display:flex; justify-content:space-between;'>
                    <b>{row.get('location', 'N/A')}</b> 
                    <span style='color:#FF4B4B;'>Rs. {row.get('rent', 0)}</span>
                </div>
                <div style='font-size:11px; color:#8B949E; margin-top:4px;'>
                    🛏️ {row.get('beds', 0)} | 📏 {row.get('marla', 'N/A')} | 💧 {row.get('water', 'N/A')}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No properties found.")

# --- TAB 2: ADD ENTRY ---
with tab2:
    mode = st.radio("Entry Type", ["Property", "Client", "Visit"], horizontal=True)
    
    if mode == "Property":
        with st.form("h_f", clear_on_submit=True):
            o_name = st.text_input("Owner Name")
            o_loc = st.text_input("Location")
            o_rent = st.number_input("Rent", min_value=0)
            o_marla = st.text_input("Marla")
            o_beds = st.number_input("Beds", 1, 10)
            o_water = st.selectbox("Water", ["Tanker", "Boring", "Line", "Yes"])
            if st.form_submit_button("SAVE"):
                supabase.table('house_inventory').insert({
                    "owner_name": o_name, "location": o_loc, "rent": o_rent,
                    "marla": o_marla, "beds": o_beds, "water": o_water,
                    "status": "Available", "added_by": st.session_state.user_name
                }).execute()
                st.success("Property Added!")
                st.rerun()

    elif mode == "Client":
        with st.form("c_f", clear_on_submit=True):
            c_name = st.text_input("Client Name")
            c_bud = st.number_input("Budget", min_value=0)
            c_area = st.text_input("Area Required")
            if st.form_submit_button("SAVE CLIENT"):
                supabase.table('client_leads').insert({
                    "name": c_name, "budget": c_bud, "area": c_area,
                    "added_by": st.session_state.user_name
                }).execute()
                st.success("Lead Logged!")
                st.rerun()

    elif mode == "Visit":
        with st.form("v_f", clear_on_submit=True):
            v_client = st.text_input("Client Name")
            v_prop = st.text_input("Property Visited")
            if st.form_submit_button("LOG VISIT"):
                supabase.table('visit_logs').insert({
                    "client": v_client, "house": v_prop,
                    "staff": st.session_state.user_name, "date": str(datetime.now().date())
                }).execute()
                st.success("Visit Recorded!")
                st.rerun()

# --- TAB 3: LOGS & ACTIONS ---
with tab3:
    view = st.selectbox("View Records", ["Houses", "Visits"])
    search = st.text_input("🔍 Search...")
    
    data = df_h if view == "Houses" else df_v
    if not data.empty:
        if search:
            data = data[data.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
        st.dataframe(data, use_container_width=True)
        
        # Action Center
        st.divider()
        mid = st.text_input("Enter ID to Update/Delete")
        if mid:
            col1, col2 = st.columns(2)
            if col1.button("Mark Rented"):
                supabase.table('house_inventory').update({"status": "Rented"}).eq('id', mid).execute()
                st.rerun()
            if st.session_state.user_role == "admin":
                if col2.button("🗑️ Delete"):
                    supabase.table('house_inventory').delete().eq('id', mid).execute()
                    st.rerun()

# --- LOGOUT ---
if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.rerun()
