import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# --- 1. SUPABASE SETUP ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Deewary - Property Portal", layout="wide", page_icon="🏢")

# --- 3. ZAMEEN STYLE CSS ---
st.markdown("""
    <style>
    /* Main Background & Font */
    [data-testid="stAppViewContainer"] { background-color: #f8f9fa; }
    
    /* Sidebar Zameen Green Theme */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e0e0e0;
    }

    /* Modern Green Buttons (Zameen Style) */
    div.stButton > button {
        width: 100%;
        height: 35px !important;
        background-color: #27a344 !important; /* Zameen Green */
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        margin-bottom: -12px;
        transition: 0.3s;
    }

    /* Button Hover */
    div.stButton > button:hover {
        background-color: #1e7e34 !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
    }

    /* Sidebar Headers */
    .section-tag {
        color: #333333;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        margin-top: 20px;
        margin-bottom: 5px;
        letter-spacing: 0.5px;
        color: #666;
    }

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 4. NAVIGATION LOGIC ---
st.sidebar.image("https://www.zameen.com/assets/zameen-logo-en.f94086d7734a7803e7e22f28b3a0e695.svg", width=150) # Just for vibe
st.sidebar.markdown("<h3 style='color: #27a344; margin-top:-10px;'>Property Admin</h3>", unsafe_allow_html=True)

user_name = st.sidebar.selectbox("User", ["Anas", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "admin786":
    
    # --- PROPERTIES SECTION ---
    st.sidebar.markdown('<p class="section-tag">Homes & Plots</p>', unsafe_allow_html=True)
    c1, c2 = st.sidebar.columns(2)
    with c1:
        if st.button("➕ Add New"): st.session_state.page = "add_p"
    with c2:
        if st.button("📋 Inventory"): st.session_state.page = "view_p"

    # --- CLIENTS SECTION ---
    st.sidebar.markdown('<p class="section-tag">Clients & Leads</p>', unsafe_allow_html=True)
    c3, c4 = st.sidebar.columns(2)
    with c3:
        if st.button("➕ New Lead"): st.session_state.page = "add_c"
    with c4:
        if st.button("📋 All Leads"): st.session_state.page = "view_c"

    # --- OPERATIONS SECTION ---
    st.sidebar.markdown('<p class="section-tag">Field Operations</p>', unsafe_allow_html=True)
    c5, c6 = st.sidebar.columns(2)
    with c5:
        if st.button("⏳ Tasks"): st.session_state.page = "add_t"
    with c6:
        if st.button("📋 Task Log"): st.session_state.page = "view_t"

    c7, c8 = st.sidebar.columns(2)
    with c7:
        if st.button("📍 Visits"): st.session_state.page = "add_v"
    with c8:
        if st.button("📋 Visit Log"): st.session_state.page = "view_v"

    # --- SUCCESS SECTION ---
    st.sidebar.markdown('<p class="section-tag">Successful Deals</p>', unsafe_allow_html=True)
    c9, c10 = st.sidebar.columns(2)
    with c9:
        if st.button("🤝 Close Deal"): st.session_state.page = "add_d"
    with c10:
        if st.button("📜 Deal History"): st.session_state.page = "view_d"

    # --- REPORTS ---
    st.sidebar.markdown('<p class="section-tag">Reports Center</p>', unsafe_allow_html=True)
    if st.sidebar.button("🔎 Search & Export PDF"): st.session_state.page = "report"

    # --- PAGE ROUTING ---
    if "page" not in st.session_state: st.session_state.page = "view_p"
    pg = st.session_state.page

    # --- DISPLAY LOGIC ---
    if pg.startswith("view_"):
        st.info(f"Viewing {pg.split('_')[1].upper()} Records")
        # Yahan aapka database fetch ka code aayega
        
    elif pg == "add_p":
        st.subheader("🏠 Property Registration")
        with st.form("prop_form"):
            st.text_input("Property Title")
            st.selectbox("City", ["Islamabad", "Rawalpindi", "Lahore"])
            st.form_submit_button("Submit Property")

else:
    st.sidebar.warning("Please enter the admin code.")

# Main Header Design
st.markdown("""
    <div style="background-color: #27a344; padding: 10px; border-radius: 5px; text-align: center;">
        <h2 style="color: white; margin: 0;">DEEWARY PROPERTY MANAGEMENT</h2>
    </div>
""", unsafe_allow_html=True)
