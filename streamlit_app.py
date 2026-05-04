import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# --- 1. CONFIG & CONNECTION ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Deewary Pro Suite", layout="wide", page_icon="🏗️")

# --- 2. THE "LEVEL" UI (CUSTOM CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
    
    /* Main Background */
    .stApp { background: radial-gradient(circle at top right, #1a1a2e, #16213e, #0f3460); }

    /* Glassmorphism Cards */
    .stat-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        transition: 0.3s;
    }
    .stat-card:hover { transform: translateY(-5px); border-color: #FF4B4B; }

    /* Status Badges */
    .badge {
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
    }
    .badge-done { background-color: #2ecc71; color: white; }
    .badge-pending { background-color: #f1c40f; color: black; }
    .badge-visiting { background-color: #3498db; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- 3. STATE MANAGEMENT ---
if "auth" not in st.session_state: st.session_state.auth = False

# --- 4. AUTHENTICATION ---
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/602/602182.png", width=80)
        st.title("Deewary Enterprise")
        access_code = st.text_input("Security Key", type="password")
        if st.button("Unlock System", use_container_width=True):
            if access_code == "admin786":
                st.session_state.auth = True
                st.rerun()
    st.stop()

# --- 5. NAVIGATION (PRO SIDEBAR) ---
with st.sidebar:
    st.markdown("### 🏢 DEEWARY.COM")
    st.caption("v3.0.1 Stable Build")
    st.divider()
    choice = st.selectbox("Menu", ["🚀 Dashboard", "📋 Inventory", "🤝 Deal Pipeline", "👥 Clients", "⚙️ Settings"])
    
    st.sidebar.markdown("---")
    st.sidebar.info("Manager: Anas\nStaff: Sawer, Tariq, Umer")

# --- 6. CORE LOGIC ---

# Data Fetcher (Cached for Performance)
def get_data(table):
    res = supabase.table(table).select("*").execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()

if choice == "🚀 Dashboard":
    st.title("Executive Dashboard")
    
    # Load Data
    df_h = get_data('house_inventory')
    df_c = get_data('client_leads')
    df_d = get_data('deals_done')
    
    # Metrics Row
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div class='stat-card'><h3>Houses</h3><h2>{len(df_h)}</h2></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='stat-card'><h3>Active Leads</h3><h2>{len(df_c)}</h2></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='stat-card'><h3>Deals Done</h3><h2>{len(df_d)}</h2></div>", unsafe_allow_html=True)
    with c4: 
        revenue = df_d['rent'].sum() if not df_d.empty else 0
        st.markdown(f"<div class='stat-card'><h3>Revenue</h3><h2>{revenue:,.0f}</h2></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Graphs Row
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.subheader("Monthly Performance")
        fig = px.area(df_d, x="created_at", y="rent", color_discrete_sequence=['#FF4B4B'])
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        st.subheader("Inventory Split")
        if not df_h.empty:
            fig_pie = px.sunburst(df_h, path=['status', 'portion'], values='rent')
            st.plotly_chart(fig_pie, use_container_width=True)

elif choice == "🤝 Deal Pipeline":
    st.title("Deal Management Pipeline")
    st.caption("Visiting se Done Deal tak ka safar track karen")

    # Kanban Style Columns
    k1, k2, k3 = st.columns(3)
    
    with k1:
        st.markdown("### 🔵 Visiting")
        # Logic to fetch only 'Visiting' status clients
        st.warning("Client: Ali | House: E-11")
        
    with k2:
        st.markdown("### 🟡 Pending")
        st.info("Client: Hamza | House: G-13")

    with k3:
        st.markdown("### 🟢 Done")
        st.success("Client: Kamran | House: F-10")

elif choice == "📋 Inventory":
    st.title("Property Repository")
    
    # Search Bar
    search = st.text_input("🔍 Search by Location, Owner or Rent...", "")
    
    df_h = get_data('house_inventory')
    if not df_h.empty:
        if search:
            df_h = df_h[df_h.apply(lambda row: search.lower() in row.astype(str).str.lower().values, axis=1)]
        
        st.dataframe(df_h, use_container_width=True, hide_index=True)
    
    # Action Buttons
    if st.button("➕ Add New Property"):
        # Pop up form logic
        pass

# --- 7. FOOTER ---
st.divider()
st.caption(f"Deewary Cloud OS | System Timestamp: {datetime.now().strftime('%H:%M:%S')}")
