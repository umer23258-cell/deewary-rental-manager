import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
import plotly.express as px # Charts ke liye

# --- 1. CONNECTION ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Deewary Hub | Premium CRM", layout="wide", page_icon="🏢")

# --- 2. UNIQUE DARK & GLOW STYLE CSS ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #05070A; color: #E0E0E0; }
    
    /* Glowing Cards for Dashboard */
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 75, 75, 0.3);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.1);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] { background-color: #0B0E14; border-right: 1px solid #1E2130; }
    
    /* Buttons Styling */
    .stButton>button {
        background: linear-gradient(90deg, #FF4B4B 0%, #FF8080 100%);
        color: white; border: none; border-radius: 8px;
        font-weight: bold; transition: 0.3s;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(255, 75, 75, 0.4); }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-thumb { background: #FF4B4B; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIN & AUTHENTICATION ---
if "authenticated" not in st.session_state:
    st.session_state.update({"authenticated": False, "user_role": None, "user_name": None})

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>DEEWARY PRO</h1>", unsafe_allow_html=True)
        user = st.selectbox("Login Identity", ["Sawer Khan", "Tariq Hussain", "Anas (Admin)"])
        pwd = st.text_input("Access Key", type="password")
        if st.button("Unlock System"):
            if user == "Anas (Admin)" and pwd == "admin786":
                st.session_state.update({"authenticated": True, "user_role": "admin", "user_name": "Anas"})
                st.rerun()
            elif (user == "Sawer Khan" and pwd == "sawer123") or (user == "Tariq Hussain" and pwd == "tariq123"):
                st.session_state.update({"authenticated": True, "user_role": "staff", "user_name": user})
                st.rerun()
            else: st.error("Access Denied!")
    st.stop()

# --- 4. DATA LOGIC ---
def fetch_data(table):
    try:
        res = supabase.table(table).select("*").order('created_at', desc=True).execute()
        return pd.DataFrame(res.data)
    except: return pd.DataFrame()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.image("https://i.ibb.co/HfKMwQJh/deewaryn-com-logo.jpg", width=120)
    st.write(f"### Welcome, {st.session_state.user_name}")
    st.caption(f"Role: {st.session_state.user_role.upper()}")
    if st.button("🚪 Log Out"):
        st.session_state.authenticated = False
        st.rerun()

# --- 6. MAIN DASHBOARD ---
df_h = fetch_data('house_inventory')
df_c = fetch_data('client_leads')
df_v = fetch_data('visit_logs')

tab_dash, tab_manage, tab_history = st.tabs(["📊 Executive Dashboard", "📝 Entry Center", "📂 Data Management"])

# --- TAB 1: DASHBOARD ---
with tab_dash:
    st.markdown("## Operational Overview")
    
    # Dashboard Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div class='metric-card'><h3>🏠 Houses</h3><h2>{len(df_h)}</h2></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='metric-card'><h3>👥 Leads</h3><h2>{len(df_c)}</h2></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='metric-card'><h3>🚗 Visits</h3><h2>{len(df_v)}</h2></div>", unsafe_allow_html=True)
    with c4:
        rev = df_h[df_h['status'] == 'Rented']['rent'].sum()
        st.markdown(f"<div class='metric-card'><h3>💰 Volume</h3><h2>{rev//1000}k</h2></div>", unsafe_allow_html=True)

    st.write("##")
    col_chart, col_staff = st.columns([2, 1])
    
    with col_chart:
        st.subheader("Visit Trends")
        if not df_v.empty:
            fig = px.line(df_v, x='date', title="Daily Activity", color_discrete_sequence=['#FF4B4B'])
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig, use_container_width=True)
    
    with col_staff:
        st.subheader("Leaderboard")
        if not df_v.empty:
            v_counts = df_v['staff'].value_counts().reset_index()
            st.table(v_counts)

# --- TAB 2: ENTRY CENTER ---
with tab_manage:
    mode = st.radio("What would you like to add?", ["New Property", "Client Requirement", "Visit Log"], horizontal=True)
    
    if mode == "New Property":
        with st.form("h_form"):
            ca, cb, cc = st.columns(3)
            with ca:
                name = st.text_input("Owner Name")
                rent = st.number_input("Monthly Rent", min_value=0)
            with cb:
                loc = st.text_input("Exact Location")
                water = st.selectbox("Water", ["Yes", "Boring", "Line Water"])
            with cc:
                gas = st.selectbox("Gas", ["Separate", "Common", "No"])
                elec = st.selectbox("Electricity", ["Separate", "Sub Meter"])
            if st.form_submit_button("Submit Property"):
                supabase.table('house_inventory').insert({"owner_name": name, "rent": rent, "location": loc, "water": water, "gas": gas, "electricity": elec, "added_by": st.session_state.user_name}).execute()
                st.success("Property Linked!")

    elif mode == "Client Requirement":
        with st.form("c_form"):
            c_name = st.text_input("Client Name")
            c_bud = st.number_input("Max Budget", min_value=0)
            c_req = st.text_area("Detailed Requirements")
            if st.form_submit_button("Save Lead"):
                supabase.table('client_leads').insert({"name": c_name, "budget": c_bud, "other_req": c_req, "added_by": st.session_state.user_name}).execute()
                st.success("Lead Captured!")

    elif mode == "Visit Log":
        with st.form("v_form"):
            v_cl = st.text_input("Client Name")
            v_h = st.text_input("Property Address")
            st.info(f"Assigning Visit to: {st.session_state.user_name}")
            if st.form_submit_button("Record Visit"):
                supabase.table('visit_logs').insert({"client": v_cl, "house": v_h, "staff": st.session_state.user_name, "date": str(datetime.now().date())}).execute()
                st.success("Activity Logged!")

# --- TAB 3: DATA MANAGEMENT ---
with tab_history:
    target = st.selectbox("Select Database", ["house_inventory", "client_leads", "visit_logs"])
    df_raw = fetch_data(target)
    
    if not df_raw.empty:
        # Staff filter
        if st.session_state.user_role != "admin":
            col_to_filter = 'added_by' if 'added_by' in df_raw.columns else 'staff'
            df_raw = df_raw[df_raw[col_to_filter] == st.session_state.user_name]
        
        search = st.text_input("🔍 Quick Search...")
        if search:
            df_raw = df_raw[df_raw.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
        
        st.dataframe(df_raw, use_container_width=True)
        
        # Edit/Delete Center
        st.divider()
        st.subheader("Modify Record")
        mod_id = st.text_input("Enter ID to Edit/Delete")
        if mod_id:
            col_edit, col_del = st.columns(2)
            with col_del:
                if st.button("🗑️ Delete Permanently"):
                    supabase.table(target).delete().eq('id', mod_id).execute()
                    st.warning("Record Purged!")
                    st.rerun()
            with col_edit:
                new_stat = st.selectbox("Update Status to:", ["Available", "Rented", "Pending", "Closed"])
                if st.button("📝 Apply Change"):
                    supabase.table(target).update({"status": new_stat}).eq('id', mod_id).execute()
                    st.success("Record Updated!")
                    st.rerun()

# --- FOOTER ---
st.divider()
st.markdown("<p style='text-align: center; opacity: 0.5;'>Deewary OS v2.0 | Staff: Sawer & Tariq | Manager: Anas</p>", unsafe_allow_html=True)
