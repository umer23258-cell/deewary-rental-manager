import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# --- 1. SUPABASE SETUP ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Deewary Property Manager", layout="wide", page_icon="🏢")

# --- 3. MOBILE FRIENDLY CSS ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    header {visibility: hidden;}
    
    /* Buttons ko mobile friendly banana */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #f0f2f6;
        border: 1px solid #d1d1d1;
        font-weight: bold;
    }
    
    /* Header Responsive */
    .main-header {
        text-align: center; 
        background-color: #1E1E1E; 
        padding: 15px; 
        border-radius: 12px; 
        border-left: 5px solid #FF4B4B;
        margin-bottom: 15px;
    }

    /* Mobile screen pe spacing set karna */
    @media (max-width: 600px) {
        .reportview-container .main .block-container {
            padding: 1rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. HEADER ---
st.markdown("""
    <div class="main-header">
        <h1 style="color: #FF4B4B; margin: 0; font-size: 24px;">DEEWARY PROPERTY MANAGER</h1>
        <p style="color: white; margin: 0;">Welcome, Umer (Manager)</p>
    </div>
""", unsafe_allow_html=True)

# --- 5. LOGIN & ACCESS ---
# Mobile pe sidebar aksar log bhool jate hain, isliye password main screen pe rakhte hain
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.subheader("🔐 Staff Login")
    user_name = st.selectbox("User Select Karen", ["Umer (Manager)", "Sawer Khan", "Tariq Hussain"])
    pwd = st.text_input("Access Code", type="password")
    if st.button("Unlock System"):
        if pwd == "admin786":
            st.session_state.authenticated = True
            st.session_state.user_name = user_name
            st.rerun()
        else:
            st.error("Ghalat Code!")
    st.stop()

# --- 6. NAVIGATION MENU (AB MAIN SCREEN PE SHOW HOGA) ---
if "menu" not in st.session_state:
    st.session_state.menu = "🏠 Dashboard"

# Function for menu navigation
def navigate_to(page):
    st.session_state.menu = page

# Mobile-Friendly Menu (Buttons on Main Screen)
st.write("### 📍 Menu")
m_col1, m_col2 = st.columns(2)

with m_col1:
    if st.button("🏠 Dashboard"): navigate_to("🏠 Dashboard")
    if st.button("🏠 Ghar Entry"): navigate_to("🏠 Ghar ki Entry (Owners)")
    if st.button("👤 Client Entry"): navigate_to("👤 Client ki Entry (New)")
    if st.button("💬 Discussion"): navigate_to("💬 Client in Discussion")

with m_col2:
    if st.button("⏳ Pending Deals"): navigate_to("⏳ Deal Pending Entry")
    if st.button("✅ Done Deals"): navigate_to("✅ Deal Done Entry")
    if st.button("📋 History View"): navigate_to("📋 All History")
    if st.button("🚪 Logout"): 
        st.session_state.authenticated = False
        st.rerun()

st.divider()

# --- 7. PAGE CONTENT LOGIC ---
menu = st.session_state.menu
st.info(f"Current Page: {menu}")

if menu == "🏠 Dashboard":
    # Dashboard Code (Original Logic)
    h_res = supabase.table('house_inventory').select("*").execute()
    df_h = pd.DataFrame(h_res.data) if h_res.data else pd.DataFrame()
    
    col1, col2 = st.columns(2)
    col1.metric("Total Houses", len(df_h))
    col2.metric("Available", len(df_h[df_h['status'] == 'Available']) if not df_h.empty else 0)
    
    st.subheader("Recent Updates")
    st.dataframe(df_h[['owner_name', 'location', 'rent', 'status']].head(10), use_container_width=True)

elif menu == "🏠 Ghar ki Entry (Owners)":
    # Form for House Entry
    with st.form("house_form", clear_on_submit=True):
        o_name = st.text_input("Owner ka Naam")
        o_contact = st.text_input("Owner Contact")
        loc = st.text_input("Location")
        rent = st.number_input("Demand Rent", min_value=0)
        h_status = st.selectbox("Status", ["Available", "Rent Out"])
        if st.form_submit_button("Save House"):
            supabase.table('house_inventory').insert({
                "owner_name": o_name, "contact": o_contact, "location": loc, 
                "rent": rent, "status": h_status, "added_by": st.session_state.user_name
            }).execute()
            st.success("Data Save Ho Gaya!")

elif menu == "📋 All History":
    # History tabbed for Mobile
    tab1, tab2, tab3 = st.tabs(["Ghar", "Clients", "Deals"])
    with tab1:
        res = supabase.table('house_inventory').select("*").execute()
        if res.data: st.dataframe(pd.DataFrame(res.data), use_container_width=True)
    with tab2:
        res = supabase.table('client_leads').select("*").execute()
        if res.data: st.dataframe(pd.DataFrame(res.data), use_container_width=True)
    with tab3:
        res = supabase.table('deals_done').select("*").execute()
        if res.data: st.dataframe(pd.DataFrame(res.data), use_container_width=True)

# Footer
st.caption(f"System Active | {st.session_state.user_name} | {datetime.now().year}")
