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
    st.error("Supabase Connection Fail! Check your Secrets.")
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
        color: white; border: none; border-radius: 8px; width: 100%; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. AUTHENTICATION ---
if "authenticated" not in st.session_state:
    st.session_state.update({"authenticated": False, "user_role": None, "user_name": None})

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>DEEWARY PRO LOGIN</h1>", unsafe_allow_html=True)
        user = st.selectbox("Select User", ["Sawer Khan", "Tariq Hussain", "Anas (Admin)"])
        pwd = st.text_input("Password", type="password")
        if st.button("Unlock"):
            if user == "Anas (Admin)" and pwd == "admin786":
                st.session_state.update({"authenticated": True, "user_role": "admin", "user_name": "Anas"})
                st.rerun()
            elif (user == "Sawer Khan" and pwd == "sawer123") or (user == "Tariq Hussain" and pwd == "tariq123"):
                st.session_state.update({"authenticated": True, "user_role": "staff", "user_name": user})
                st.rerun()
            else: st.error("Wrong Password!")
    st.stop()

# --- 4. DATA FETCHING ---
def fetch_data(table):
    try:
        res = supabase.table(table).select("*").order('created_at', desc=True).execute()
        return pd.DataFrame(res.data)
    except:
        return pd.DataFrame()

# Fetching all data at once
df_h = fetch_data('house_inventory')
df_c = fetch_data('client_leads')
df_v = fetch_data('visit_logs')

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.user_name}")
    st.write(f"Role: **{st.session_state.user_role.upper()}**")
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# --- 6. NAVIGATION TABS ---
tab_dash, tab_entry, tab_mgmt = st.tabs(["📊 Dashboard", "📝 Nayi Entry", "📂 History & Edit"])

# --- TAB 1: DASHBOARD ---
with tab_dash:
    st.markdown("## Operational Overview")
    
    # Dashboard Cards with Safety
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div class='metric-card'><h3>🏠 Houses</h3><h2>{len(df_h)}</h2></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='metric-card'><h3>👥 Leads</h3><h2>{len(df_c)}</h2></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='metric-card'><h3>🚗 Visits</h3><h2>{len(df_v)}</h2></div>", unsafe_allow_html=True)
    with c4:
        # Fixed the KeyError by checking column names first
        if not df_h.empty and 'status' in df_h.columns and 'rent' in df_h.columns:
            rev = df_h[df_h['status'] == 'Rented']['rent'].sum()
        else: rev = 0
        st.markdown(f"<div class='metric-card'><h3>💰 Volume</h3><h2>{rev:,.0f}</h2></div>", unsafe_allow_html=True)

    st.write("##")
    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.subheader("Activity Chart")
        if not df_v.empty:
            fig = px.line(df_v, x='date', title="Visits over Time", color_discrete_sequence=['#FF4B4B'])
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("No visit data to chart yet.")
    with col_r:
        st.subheader("Leaderboard")
        if not df_v.empty:
            st.table(df_v['staff'].value_counts())

# --- TAB 2: ENTRY CENTER ---
with tab_entry:
    choice = st.radio("What to add?", ["Property", "Client", "Visit"], horizontal=True)
    
    if choice == "Property":
        with st.form("h_f"):
            c1, c2, c3 = st.columns(3)
            with c1:
                on = st.text_input("Owner Name")
                oc = st.text_input("Contact")
                ol = st.text_input("Location")
            with c2:
                ornt = st.number_input("Rent", min_value=0)
                om = st.text_input("Marla")
                of = st.selectbox("Floor", ["Ground", "First", "Upper", "Full House"])
            with c3:
                ow = st.selectbox("Water", ["Yes", "Boring", "Line"])
                og = st.selectbox("Gas", ["Separate", "Common", "No"])
                oe = st.selectbox("Elec", ["Separate", "Sub Meter"])
            if st.form_submit_button("Save Property"):
                supabase.table('house_inventory').insert({
                    "owner_name": on, "contact": oc, "location": ol, "rent": ornt, "marla": om,
                    "floor": of, "water": ow, "gas": og, "electricity": oe, "added_by": st.session_state.user_name
                }).execute()
                st.success("Saved!")
                st.rerun()

    elif choice == "Client":
        with st.form("c_f"):
            cn = st.text_input("Client Name")
            cc = st.text_input("Contact")
            cb = st.number_input("Budget", min_value=0)
            if st.form_submit_button("Save Lead"):
                supabase.table('client_leads').insert({
                    "name": cn, "contact": cc, "budget": cb, "added_by": st.session_state.user_name
                }).execute()
                st.success("Lead Saved!")
                st.rerun()

    elif choice == "Visit":
        with st.form("v_f"):
            vc = st.text_input("Client Name")
            vh = st.text_input("House Location")
            st.info(f"Staff: {st.session_state.user_name}")
            if st.form_submit_button("Record Visit"):
                supabase.table('visit_logs').insert({
                    "client": vc, "house": vh, "staff": st.session_state.user_name, "date": str(datetime.now().date())
                }).execute()
                st.success("Visit Logged!")
                st.rerun()

# --- TAB 3: HISTORY & EDIT ---
with tab_mgmt:
    target = st.selectbox("Select View", ["house_inventory", "client_leads", "visit_logs"])
    df_raw = fetch_data(target)
    
    if not df_raw.empty:
        # Staff specific filter
        if st.session_state.user_role != "admin":
            col_filter = 'added_by' if 'added_by' in df_raw.columns else 'staff'
            if col_filter in df_raw.columns:
                df_raw = df_raw[df_raw[col_filter] == st.session_state.user_name]
        
        search = st.text_input("🔍 Search History...")
        if search:
            df_raw = df_raw[df_raw.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
        
        st.dataframe(df_raw, use_container_width=True)
        
        st.divider()
        st.subheader("Edit / Delete Record")
        mid = st.text_input("Enter ID")
        if mid:
            col_e, col_d = st.columns(2)
            with col_e:
                new_stat = st.selectbox("Update Status", ["Available", "Rented", "Pending", "Done Deal"])
                if st.button("Apply Status Change"):
                    supabase.table(target).update({"status": new_stat}).eq('id', mid).execute()
                    st.success("Updated!")
                    st.rerun()
            with col_d:
                if st.button("🗑️ Delete Record"):
                    supabase.table(target).delete().eq('id', mid).execute()
                    st.warning("Deleted!")
                    st.rerun()
    else: st.info("No records found in this table.")

st.divider()
st.caption("Deewary Hub v2.0 | Anas, Sawer Khan, Tariq Hussain")
