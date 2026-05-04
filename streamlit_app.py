import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- 1. SETUP ---
st.set_page_config(page_title="Real Estate Hub CRM", layout="wide", initial_sidebar_state="expanded")

# --- 2. THE DESIGN (CSS for Dark Theme & Layout) ---
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    
    /* Top Metric Cards */
    .metric-card {
        background-color: #1E2130;
        padding: 20px;
        border-radius: 10px;
        border-top: 5px solid #00D1FF;
        color: white;
        text-align: left;
    }
    
    /* Property Card */
    .prop-card {
        background-color: #1E2130;
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 10px;
        border: 1px solid #333;
    }
    .prop-img {
        width: 100%;
        border-radius: 8px;
        height: 150px;
        object-fit: cover;
    }
    
    /* Deal Pipeline Column */
    .pipeline-col {
        background-color: #161925;
        padding: 15px;
        border-radius: 10px;
        min-height: 400px;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] { background-color: #11141D; }
    </style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🏗️ RealEstate Hub")
    st.caption("CRM - Islamabad")
    st.divider()
    menu = st.radio("MAIN MENU", ["📊 Dashboard", "➕ Add Property", "👥 Client CRM", "🔄 Deal Pipeline", "📈 Staff Performance"])

# --- 4. DASHBOARD (The Image Layout) ---
if menu == "📊 Dashboard":
    st.write(f"### Welcome, Admin ID: #001")
    
    # ROW 1: METRICS
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown('<div class="metric-card" style="border-color: #00D1FF;"><h4>TOTAL LISTINGS</h4><h2>125 <span style="color:#00FF00; font-size:15px;">+5</span></h2></div>', unsafe_allow_html=True)
    m2.markdown('<div class="metric-card" style="border-color: #00FFA3;"><h4>ACTIVE LEADS</h4><h2>42</h2></div>', unsafe_allow_html=True)
    m3.markdown('<div class="metric-card" style="border-color: #FFB800;"><h4>PENDING VISITS</h4><h2>18</h2></div>', unsafe_allow_html=True)
    m4.markdown('<div class="metric-card" style="border-color: #FF4B4B;"><h4>CLOSED DEALS</h4><h2>9</h2></div>', unsafe_allow_html=True)
    
    st.write("##")

    # ROW 2: PROPERTIES & PIPELINE
    col_left, col_right = st.columns([1.5, 1])
    
    with col_left:
        st.subheader("PROPERTIES & INVENTORY")
        # Property Cards Grid
        p_col1, p_col2, p_col3 = st.columns(3)
        
        # Example Card 1
        with p_col1:
            st.markdown("""
                <div class="prop-card">
                    <img src="https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=500" class="prop-img">
                    <p style="font-size:12px; margin-top:5px;"><b>UNIT 102 - F-11 - PKR 75,000/mo</b><br><span style="color:#00FF00;">Available</span></p>
                </div>
            """, unsafe_allow_html=True)
            st.button("View Details", key="v1", use_container_width=True)
            st.button("Add Visit", key="a1", use_container_width=True)

        with p_col2:
            st.markdown("""
                <div class="prop-card">
                    <img src="https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=500" class="prop-img">
                    <p style="font-size:12px; margin-top:5px;"><b>VILLA 305 - DHA II - 6.5 Crore</b><br><span style="color:#00FF00;">Available</span></p>
                </div>
            """, unsafe_allow_html=True)
            st.button("View Details", key="v2", use_container_width=True)
            st.button("Add Visit", key="a2", use_container_width=True)

    with col_right:
        st.subheader("DEAL PIPELINE & STATUS")
        pipe_tabs = st.tabs(["Interested", "Scheduled", "Negotiation", "Closed"])
        with pipe_tabs[0]:
            st.info("Asif | DHA II - Villa 305")
            st.info("Amna | F-11 - Unit 102")

    # ROW 3: VISITS & STAFF PERFORMANCE
    st.write("##")
    col_v, col_s = st.columns([1.5, 1])
    
    with col_v:
        st.subheader("RECENT VISITS & ACTIVITY")
        # Dummy Visit Data
        visit_data = {
            "Client Name": ["Anna", "Ali", "Amna"],
            "Property": ["F-11", "DHA II", "G-11"],
            "Staff": ["Admin", "Umer", "Sawer"],
            "Status": ["Visiting", "Done", "Pending"]
        }
        st.table(pd.DataFrame(visit_data))

    with col_s:
        st.subheader("STAFF LEADERBOARD")
        # Bar Chart for Staff
        st.bar_chart({"Admin": 23, "Amna": 15, "Umer": 10, "Sawer": 5})

# --- 5. FOOTER ---
st.markdown("<hr><center><small>Powered by Streamlit | Data: Supabase | © 2026 Deewary.com</small></center>", unsafe_allow_html=True)
