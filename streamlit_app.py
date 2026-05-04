import streamlit as st
from supabase import create_client
import pandas as pd

# Page Configuration for Wide Look
st.set_page_config(page_title="RealEstate Hub CRM", layout="wide", initial_sidebar_state="expanded")

# CSS for styling like the image (Dark Theme & Cards)
st.markdown("""
    <style>
    .main { background-color: #12141d; }
    .metric-card {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #00d1b2;
    }
    .prop-card {
        background-color: #262936;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Supabase Connection
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏠 RealEstate Hub")
    st.caption("CRM - Islamabad")
    menu = st.radio("Navigation", ["📊 Dashboard", "➕ Add Property", "👥 Client CRM", "🔄 Deal Pipeline", "📈 Staff Performance"])

# --- DASHBOARD PAGE ---
if "Dashboard" in menu:
    st.title("Property Management Overview")
    st.write("Welcome back, Admin!")

    # 1. Top Metrics (Colorful Boxes)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card" style="border-left-color: #00bcd4;"><h3>Total Listings</h3><h2>125 <span style="font-size:15px; color:#00ff00;">+5</span></h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card" style="border-left-color: #4caf50;"><h3>Active Leads</h3><h2>42</h2></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card" style="border-left-color: #ff9800;"><h3>Pending Visits</h3><h2>18</h2></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card" style="border-left-color: #f44336;"><h3>Closed Deals</h3><h2>9</h2></div>', unsafe_allow_html=True)

    st.divider()

    # 2. Main Sections (Properties & Pipeline)
    left_col, right_col = st.columns([1.2, 1])

    with left_col:
        st.subheader("🏢 Properties & Inventory")
        tab1, tab2, tab3 = st.tabs(["All", "Rent", "Sale"])
        
        # Fetching data for cards
        props = supabase.table("properties").select("*").execute().data
        
        # Displaying properties in a grid
        grid_col1, grid_col2 = st.columns(2)
        for i, p in enumerate(props):
            target_col = grid_col1 if i % 2 == 0 else grid_col2
            with target_col:
                st.markdown(f"""
                <div class="prop-card">
                    <img src="{p['image_url']}" width="100%" style="border-radius:5px;">
                    <p style="margin-top:10px; font-weight:bold;">{p['title']} - {p['location']}</p>
                    <p style="color:#00d1b2;">{p['type']} ({p['price_rent']})</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Add Visit for {p['title']}", key=f"btn_{p['id']}"):
                    st.info(f"Visit scheduled for {p['title']}")

    with right_col:
        st.subheader("🤝 Deal Pipeline & Status")
        # Visualizing columns like the image
        p1, p2 = st.columns(2)
        with p1:
            st.info("**Interested Leads**")
            st.caption("Asif - DHA II")
            st.caption("Amna - F-11")
        with p2:
            st.warning("**Visit Scheduled**")
            st.caption("Umer - G-11")

    # 3. Bottom Section (Recent Activity & Staff)
    st.divider()
    b_col1, b_col2 = st.columns([1.5, 1])
    
    with b_col1:
        st.subheader("📋 Recent Visits & Activity")
        activity_data = pd.DataFrame([
            {"Client": "Anas", "Property": "Unit 102", "Staff": "Admin", "Status": "Active"},
            {"Client": "Tariq", "Property": "Villa 305", "Staff": "Staff-01", "Status": "Pending"}
        ])
        st.table(activity_data)

    with b_col2:
        st.subheader("📊 Staff Performance")
        chart_data = pd.DataFrame({"Staff": ["Admin", "Amna", "Umer"], "Deals": [23, 13, 10]})
        st.bar_chart(chart_data.set_index("Staff"))
