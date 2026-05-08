import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# --- CONNECTION ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except:
    st.error("Supabase Config Missing!")
    st.stop()

# --- LUXURY UI ---
st.set_page_config(page_title="Deewary Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background: #0F111A; color: #E0E0E0; }
    .app-header { background: linear-gradient(90deg, #FF4B4B, #822727); padding: 20px; border-radius: 0 0 30px 30px; text-align: center; }
    .metric-box { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 20px; text-align: center; }
    .house-card { background: #1A1D27; border-radius: 20px; padding: 15px; margin-bottom: 15px; border-bottom: 3px solid #FF4B4B; }
    .stButton>button { background: linear-gradient(90deg, #FF4B4B, #FF8080); color: white; border-radius: 15px; height: 50px; font-weight: bold; width: 100%; }
    </style>
""", unsafe_allow_html=True)

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state.update({"auth": False, "user": None})
if not st.session_state.auth:
    st.markdown("<div class='app-header'><h1>DEEWARY PRO</h1></div>", unsafe_allow_html=True)
    user = st.selectbox("User", ["Sawer Khan", "Tariq Hussain", "Anas (Admin)"])
    pin = st.text_input("Pin", type="password")
    if st.button("Unlock"):
        if pin in ["admin786", "sawer123", "tariq123"]:
            st.session_state.update({"auth": True, "user": user})
            st.rerun()
    st.stop()

# --- DATA FETCH ---
def get_data(table):
    try:
        res = supabase.table(table).select("*").order('created_at', desc=True).execute()
        return pd.DataFrame(res.data)
    except: return pd.DataFrame()

df_h = get_data('house_inventory')
df_c = get_data('client_leads')
df_v = get_data('visit_logs')

# --- NAVIGATION ---
t1, t2, t3 = st.tabs(["📊 Dashboard", "📝 Add Entry", "📂 Records"])

with t1:
    st.write(f"### Welcome, {st.session_state.user} ✨")
    m1, m2, m3 = st.columns(3)
    
    # SAFETY CHECKS FOR COUNTS
    h_avail = len(df_h[df_h['status'] == 'Available']) if not df_h.empty and 'status' in df_h.columns else 0
    c_count = len(df_c) if not df_c.empty else 0
    v_today = len(df_v[df_v['date'] == str(datetime.now().date())]) if not df_v.empty and 'date' in df_v.columns else 0

    m1.markdown(f"<div class='metric-box'><h2>{h_avail}</h2><p>Available Homes</p></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='metric-box'><h2>{c_count}</h2><p>Active Leads</p></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='metric-box'><h2>{v_today}</h2><p>Today's Visits</p></div>", unsafe_allow_html=True)

    st.markdown("#### 💎 Live Listings")
    if not df_h.empty and 'status' in df_h.columns:
        avail_only = df_h[df_h['status'] == 'Available'].head(10)
        for _, r in avail_only.iterrows():
            st.markdown(f"<div class='house-card'><b>📍 {r.get('location','N/A')}</b> | Rs. {r.get('rent',0)}<br><small>{r.get('marla','')} • {r.get('beds',0)} Beds</small></div>", unsafe_allow_html=True)

with t2:
    mode = st.radio("Type", ["Property", "Client", "Visit"], horizontal=True)
    if mode == "Property":
        with st.form("p_f"):
            on, ol = st.text_input("Owner"), st.text_input("Location")
            rn, mr = st.number_input("Rent", 0), st.text_input("Marla")
            if st.form_submit_button("PUBLISH"):
                supabase.table('house_inventory').insert({"owner_name":on,"location":ol,"rent":rn,"marla":mr,"status":"Available","added_by":st.session_state.user}).execute()
                st.success("Published!"); st.rerun()
    elif mode == "Client":
        with st.form("c_f"):
            cn, cb = st.text_input("Client Name"), st.number_input("Budget", 0)
            if st.form_submit_button("SAVE"):
                supabase.table('client_leads').insert({"name":cn,"budget":cb,"added_by":st.session_state.user}).execute()
                st.success("Saved!"); st.rerun()

with t3:
    v = st.selectbox("View", ["Houses", "Visits"])
    target = 'house_inventory' if v=="Houses" else 'visit_logs'
    data = get_data(target)
    if not data.empty:
        st.dataframe(data, use_container_width=True)
        mid = st.text_input("ID to Rent/Delete")
        if mid and st.button("Mark as Rented"):
            supabase.table(target).update({"status":"Rented"}).eq('id', mid).execute()
            st.rerun()
