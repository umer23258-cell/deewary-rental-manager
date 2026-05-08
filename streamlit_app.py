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
    st.error("Connection Error!")
    st.stop()

# --- 2. MOBILE-FIRST PREMIUM UI ---
st.set_page_config(page_title="Deewary OS", layout="wide", page_icon="📱")

st.markdown("""
    <style>
    /* Mobile App Look */
    .stApp { background: #0A0E14; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    
    /* Neon Metric Cards */
    .metric-container {
        background: linear-gradient(145deg, #161B22, #0D1117);
        border: 1px solid #30363D;
        padding: 15px; border-radius: 20px;
        text-align: center; margin-bottom: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .metric-value { font-size: 24px; font-weight: 800; color: #FF4B4B; }
    .metric-label { font-size: 12px; color: #8B949E; text-transform: uppercase; letter-spacing: 1px; }

    /* Property Cards for Mobile */
    .prop-card {
        background: #1C2128; border-radius: 15px; padding: 15px;
        margin-bottom: 15px; border-left: 5px solid #FF4B4B;
    }

    /* Tabs & Buttons */
    .stTabs [data-baseweb="tab-list"] { display: flex; justify-content: space-around; background: #161B22; border-radius: 50px; padding: 5px; }
    .stTabs [data-baseweb="tab"] { color: white; border: none !important; }
    .stTabs [aria-selected="true"] { background: #FF4B4B !important; border-radius: 50px !important; color: white !important; }
    
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3em;
        background: linear-gradient(90deg, #FF4B4B, #D73A49);
        border: none; font-weight: bold; font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.update({"authenticated": False, "user_role": None, "user_name": None})

if not st.session_state.authenticated:
    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>🏢 DEEWARY <span style='color:#FF4B4B'>PRO</span></h1>", unsafe_allow_html=True)
    with st.container():
        user = st.selectbox("Who are you?", ["Sawer Khan", "Tariq Hussain", "Anas (Admin)"])
        pwd = st.text_input("Security Pin", type="password")
        if st.button("Access Dashboard"):
            if user == "Anas (Admin)" and pwd == "admin786":
                st.session_state.update({"authenticated": True, "user_role": "admin", "user_name": "Anas"})
                st.rerun()
            elif (user == "Sawer Khan" and pwd == "sawer123") or (user == "Tariq Hussain" and pwd == "tariq123"):
                st.session_state.update({"authenticated": True, "user_role": "staff", "user_name": user})
                st.rerun()
            else: st.error("Wrong Pin!")
    st.stop()

# --- 4. DATA LOGIC ---
def fetch_all():
    h = supabase.table('house_inventory').select("*").order('created_at', desc=True).execute()
    c = supabase.table('client_leads').select("*").order('created_at', desc=True).execute()
    v = supabase.table('visit_logs').select("*").order('created_at', desc=True).execute()
    return pd.DataFrame(h.data), pd.DataFrame(c.data), pd.DataFrame(v.data)

df_h, df_c, df_v = fetch_all()

# --- 5. APP NAVIGATION ---
# Icons ke liye hum simple text ya emojis use kar rahe hain jo mobile par fast load hote hain
tab1, tab2, tab3 = st.tabs(["🏠 Home", "➕ Add", "📁 Logs"])

# --- TAB 1: SMART DASHBOARD ---
with tab1:
    st.markdown(f"### Hello, {st.session_state.user_name} 👋")
    
    # Live Daily Snapshot
    avail = df_h[df_h['status'] == 'Available'] if not df_h.empty else []
    today_v = df_v[df_v['date'] == str(datetime.now().date())] if not df_v.empty else []

    m1, m2 = st.columns(2)
    with m1:
        st.markdown(f"<div class='metric-container'><div class='metric-label'>Available</div><div class='metric-value'>{len(avail)}</div></div>", unsafe_allow_html=True)
    with m2:
        st.markdown(f"<div class='metric-container'><div class='metric-label'>Visits Today</div>
