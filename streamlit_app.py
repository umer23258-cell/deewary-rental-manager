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

# --- 3. CUSTOM CSS (Full Responsive) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    header {visibility: hidden;}
    
    /* Header Box */
    .main-header {
        text-align: center; 
        background-color: #1E1E1E; 
        padding: 20px; 
        border-radius: 15px; 
        border: 2px solid #FF4B4B;
        margin-bottom: 25px;
    }

    /* Buttons Style */
    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
        height: 3.5em;
        border: 1px solid #FF4B4B;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. HEADER ---
st.markdown("""
    <div class="main-header">
        <h1 style="color: #FF4B4B; margin: 0; font-family: 'Arial Black';">DEEWARY.COM RENTER PROPERTY MANAGEMENT</h1>
        <p style="color: white; letter-spacing: 2px;">MANAGER PORTAL - WELCOME UMER</p>
    </div>
""", unsafe_allow_html=True)

# --- 5. AUTHENTICATION (Ab samne screen par hai) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,2,1]) # Screen ke beech mein lane ke liye
    with col2:
        st.subheader("🔐 Staff Access")
        user_name = st.selectbox("Apna Naam Select Karen", ["Umer (Manager)", "Sawer Khan", "Tariq Hussain"])
        pwd = st.text_input("Access Code", type="password")
        if st.button("Unlock System"):
            if pwd == "admin786":
                st.session_state.logged_in = True
                st.session_state.user_name = user_name
                st.rerun()
            else:
                st.error("Ghalat Code Hai!")
    st.stop() # Jab tak login nahi hoga, niche wala code run nahi hoga

# --- 6. NAVIGATION MENU (Samne Screen Par) ---
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Dashboard"

def go_to(page):
    st.session_state.current_page = page

# Menu Buttons (Grid Layout for Mobile/PC)
st.write(f"### 📍 Welcome {st.session_state.user_name}")
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("🏠 Dashboard"): go_to("🏠 Dashboard")
    if st.button("🏠 Ghar Entry"): go_to("🏠 Ghar ki Entry (Owners)")
with c2:
    if st.button("👤 Client Entry"): go_to("👤 Client ki Entry (New)")
    if st.button("⏳ Pending Deals"): go_to("⏳ Deal Pending Entry")
with c3:
    if st.button("📋 View History"): go_to("📋 History")
    if st.button("🚪 Logout"): 
        st.session_state.logged_in = False
        st.rerun()

st.divider()

# --- 7. PAGES LOGIC ---
menu = st.session_state.current_page

if menu == "🏠 Dashboard":
    st.subheader("📊 Business Overview")
    # Yahan wahi dashboard wala code jo pehle tha
    h_res = supabase.table('house_inventory').select("*").execute()
    df_h = pd.DataFrame(h_res.data) if h_res.data else pd.DataFrame()
    st.metric("Total Renter Houses", len(df_h))
    st.dataframe(df_h[['owner_name', 'location', 'rent', 'status']].head(10), use_container_width=True)

elif menu == "🏠 Ghar ki Entry (Owners)":
    st.subheader("🏡 Naye Ghar ki Detail")
    with st.form("house_form", clear_on_submit=True):
        o_name = st.text_input("Owner ka Naam")
        loc = st.text_input("Location")
        rent = st.number_input("Demand Rent", min_value=0)
        if st.form_submit_button("Save Record"):
            supabase.table('house_inventory').insert({
                "owner_name": o_name, "location": loc, "rent": rent, "added_by": st.session_state.user_name
            }).execute()
            st.success("Save ho gaya!")

elif menu == "📋 History":
    st.subheader("📋 Records History")
    res = supabase.table('house_inventory').select("*").order('id', desc=True).execute()
    if res.data:
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)

# Footer
st.divider()
st.caption(f"© {datetime.now().year} Deewary.com | Manager: {st.session_state.user_name}")
