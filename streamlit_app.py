import streamlit as st
import pandas as pd
from supabase import create_client, Client
import plotly.express as px
from datetime import datetime

# --- 1. ENTERPRISE CONNECTION ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Deewary OS | Black Edition", layout="wide", initial_sidebar_state="collapsed")

# --- 2. ADVANCED NEON-GLASS CSS ---
st.markdown("""
    <style>
    /* Full Page Gradient */
    .stApp { background: #050505; color: #E0E0E0; }
    
    /* Neon Metric Cards */
    .metric-container {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    }
    .neon-blue { border-left: 4px solid #00D1FF; box-shadow: -5px 0 15px rgba(0, 209, 255, 0.1); }
    .neon-green { border-left: 4px solid #00FFA3; box-shadow: -5px 0 15px rgba(0, 255, 163, 0.1); }
    .neon-orange { border-left: 4px solid #FFB800; box-shadow: -5px 0 15px rgba(255, 184, 0, 0.1); }
    
    /* Custom Button Glow */
    .stButton>button {
        background: transparent;
        color: #FF4B4B;
        border: 1px solid #FF4B4B;
        border-radius: 8px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: #FF4B4B;
        color: white;
        box-shadow: 0 0 20px rgba(255, 75, 75, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. STATE LOGIC ---
if "active_tab" not in st.session_state: st.session_state.active_tab = "Dashboard"

# --- 4. TOP NAV BAR (THE LEVEL LOOK) ---
st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0px; border-bottom: 1px solid #333;">
        <h2 style="margin:0; color:#FF4B4B;">DEEWARY.COM <span style="font-size:12px; color:#888;">PRO OS v4.0</span></h2>
        <div style="color:#aaa;">Active Manager: <b style="color:white;">ANAS</b> | Status: <span style="color:#00FF00;">● Online</span></div>
    </div>
""", unsafe_allow_html=True)

# --- 5. DASHBOARD LAYOUT ---
def render_dashboard():
    # Metrics Row
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown('<div class="metric-container neon-blue"><h4>Total Units</h4><h1 style="margin:0;">125</h1><small style="color:#00FF00;">↑ 12% vs Last Month</small></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="metric-container neon-green"><h4>Leads</h4><h1 style="margin:0;">42</h1><small style="color:#00FF00;">↑ 5% New</small></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="metric-container neon-orange"><h4>Pending</h4><h1 style="margin:0;">18</h1><small style="color:#FFB800;">Requires Follow-up</small></div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="metric-container" style="border-left: 4px solid #FF4B4B;"><h4>Closed</h4><h1 style="margin:0;">09</h1><small style="color:#FF4B4B;">Target: 15</small></div>', unsafe_allow_html=True)

    st.write("##")

    # Main Grid
    col_main, col_side = st.columns([2, 1])

    with col_main:
        st.subheader("🏙️ Inventory Control & Virtual Tours")
        # Advance Filter Tabs
        f1, f2, f3 = st.tabs(["All Units", "Available Only", "Rented Out"])
        
        with f1:
            # Code to fetch from house_inventory
            st.markdown("""
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div class="metric-container">
                        <img src="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=400" style="width:100%; border-radius:10px;">
                        <h4>DHA Phase 6 - Villa</h4>
                        <p>Rent: 120k | Owner: Tariq</p>
                        <button style="width:100%; padding:10px; border-radius:5px; background:#FF4B4B; border:none; color:white;">Quick Edit</button>
                    </div>
                    <div class="metric-container">
                        <img src="https://images.unsplash.com/photo-1600607687940-4e524cb35797?w=400" style="width:100%; border-radius:10px;">
                        <h4>F-11 Apartment</h4>
                        <p>Rent: 85k | Owner: Sawer</p>
                        <button style="width:100%; padding:10px; border-radius:5px; background:#FF4B4B; border:none; color:white;">Quick Edit</button>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with col_side:
        st.subheader("⚡ System Logs & Activity")
        # User Summary mentions staff association
        st.write("---")
        st.caption("Today - 10:45 AM")
        st.info("Umer added 2 new listings in G-11")
        st.caption("Today - 09:12 AM")
        st.success("Sawer Khan closed deal for DHA Villa")
        
        st.subheader("📈 Staff Performance")
        staff_perf = pd.DataFrame({"Name": ["Umer", "Sawer", "Tariq"], "Deals": [12, 18, 15]})
        st.plotly_chart(px.bar(staff_perf, x="Name", y="Deals", color="Name", template="plotly_dark"), use_container_width=True)

# Navigation Logic
if st.session_state.active_tab == "Dashboard":
    render_dashboard()

# Footer
st.markdown("<br><hr><center>DEEWARY.COM CLOUD OS | 2026 Edition</center>", unsafe_allow_html=True)
