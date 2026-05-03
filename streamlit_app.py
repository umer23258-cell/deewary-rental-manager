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

# --- 3. MOBILE APP STYLE CSS ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    header {visibility: hidden;}
    
    /* Buttons ko bare aur touch-friendly banana */
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 4em;
        font-weight: bold;
        font-size: 16px;
        border: 2px solid #FF4B4B;
        background-color: #1E1E1E;
        color: white;
        margin-bottom: 10px;
    }
    
    /* Active Button Color */
    div.stButton > button:hover {
        background-color: #FF4B4B;
        color: white;
    }

    /* Container for Mobile Spacing */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. HELPER FUNCTIONS ---
def delete_record(table_name, record_id):
    supabase.table(table_name).delete().eq("id", record_id).execute()
    st.warning(f"Record ID {record_id} delete kar diya gaya hai.")
    st.rerun()

def update_record(table_name, record_id, data_dict):
    supabase.table(table_name).update(data_dict).eq("id", record_id).execute()
    st.success(f"Record ID {record_id} update ho gaya!")
    st.rerun()

# --- 5. HEADER ---
st.markdown("""
    <div style="text-align: center; background-color: #1E1E1E; padding: 15px; border-radius: 15px; border: 2px solid #FF4B4B; margin-bottom: 20px;">
        <h2 style="color: #FF4B4B; margin: 0; font-family: 'Arial Black'; font-size: 22px;">DEEWARY PROPERTY MANAGER</h2>
        <p style="color: white; font-size: 12px; margin: 0;">MANAGER PORTAL - WELCOME UMER</p>
    </div>
""", unsafe_allow_html=True)

# --- 6. AUTHENTICATION ---
# Mobile pe sidebar aksar hide ho jata hai, isliye login samne rakhte hain
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("🔐 Staff Access")
    user_name = st.selectbox("Apna Naam Select Karen", ["Umer (Manager)", "Sawer Khan", "Tariq Hussain"])
    pwd = st.text_input("Access Code", type="password")
    if st.button("Unlock System", use_container_width=True):
        if pwd == "admin786":
            st.session_state.logged_in = True
            st.session_state.user_name = user_name
            st.rerun()
        else:
            st.error("Ghalat Code!")
    st.stop()

# --- 7. MOBILE APP MENU (NAYI TABDEELI) ---
if "menu" not in st.session_state:
    st.session_state.menu = "🏠 Dashboard"

def set_menu(name):
    st.session_state.menu = name

# Yahan menu sidebar se nikal kar screen par grid layout mein hai
st.write("### 📲 Main Menu")
col_m1, col_m2 = st.columns(2)

with col_m1:
    if st.button("🏠 Dashboard"): set_menu("🏠 Dashboard")
    if st.button("🏠 Ghar Entry"): set_menu("🏠 Ghar ki Entry (Owners)")
    if st.button("👤 Client Entry"): set_menu("👤 Client ki Entry (New)")

with col_m2:
    if st.button("📋 Ghar History"): set_menu("📋 Gharon ki History")
    if st.button("👥 Client History"): set_menu("👥 New Clients History")
    if st.button("🚪 Logout"): 
        st.session_state.logged_in = False
        st.rerun()

st.divider()
menu = st.session_state.menu
st.markdown(f"#### 📍 Selected: {menu}")

# --- 8. ORIGINAL LOGIC (DASHBOARD & FORMS) ---
if menu == "🏠 Dashboard":
    # Aapka dashboard logic yahan same rahega
    h_res = supabase.table('house_inventory').select("*").execute()
    df_h = pd.DataFrame(h_res.data) if h_res.data else pd.DataFrame()
    
    c1, c2 = st.columns(2)
    c1.metric("Total Houses", len(df_h))
    c2.metric("Available", len(df_h[df_h['status'] == 'Available']) if not df_h.empty else 0)
    
    st.dataframe(df_h[['owner_name', 'location', 'rent', 'status']].head(10), use_container_width=True)

elif menu == "🏠 Ghar ki Entry (Owners)":
    # Aapka original form logic yahan same rahega
    with st.form("house_form", clear_on_submit=True):
        o_name = st.text_input("Owner Name")
        loc = st.text_input("Location")
        rent = st.number_input("Rent", min_value=0)
        if st.form_submit_button("Save House Record", use_container_width=True):
            supabase.table('house_inventory').insert({
                "owner_name": o_name, "location": loc, "rent": rent, "added_by": st.session_state.user_name
            }).execute()
            st.success("Save ho gaya!")

elif menu == "📋 Gharon ki History":
    # Aapka original history logic yahan same rahega
    res = supabase.table('house_inventory').select("*").order('id', desc=True).execute()
    if res.data:
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)

# Baki saari history aur forms ka logic aapka original hi rahega...

st.divider()
st.caption(f"© {datetime.now().year} Deewary.com | Mobile Friendly Mode")
