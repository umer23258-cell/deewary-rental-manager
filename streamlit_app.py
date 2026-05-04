import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# --- 1. CONNECTION ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Deewary Hub", layout="wide", initial_sidebar_state="collapsed")

# --- 2. ADVANCED STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    .action-btn {
        background-color: #1E2130;
        border: 1px solid #FF4B4B;
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        cursor: pointer;
        font-weight: bold;
    }
    .action-btn:hover { background-color: #FF4B4B; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- 3. DYNAMIC MODAL FUNCTIONS (Entry Logic) ---
def save_data(table, data):
    supabase.table(table).insert(data).execute()
    st.success(f"{table.replace('_', ' ').title()} Entry Saved!")

# --- 4. TOP BAR ACTIONS (Entry Buttons) ---
st.markdown("<h2 style='color:white;'>DEEWARY ACTION CENTER</h2>", unsafe_allow_html=True)
col_a, col_b, col_c, col_d, col_e = st.columns(5)

with col_a:
    if st.button("➕ Naya Ghar"): st.session_state.entry_mode = "house"
with col_b:
    if st.button("👥 Naya Client"): st.session_state.entry_mode = "client"
with col_c:
    if st.button("🚗 Visit Plan"): st.session_state.entry_mode = "visit"
with col_d:
    if st.button("⏳ Deal Pending"): st.session_state.entry_mode = "pending"
with col_e:
    if st.button("✅ Deal Done"): st.session_state.entry_mode = "done"

st.divider()

# --- 5. ENTRY FORMS (Pop-up Style Logic) ---
if "entry_mode" in st.session_state:
    mode = st.session_state.entry_mode
    
    with st.expander(f"📝 {mode.upper()} ENTRY FORM", expanded=True):
        if mode == "house":
            with st.form("house_form"):
                o_name = st.text_input("Owner Name")
                loc = st.text_input("Location")
                rent = st.number_input("Rent", min_value=0)
                if st.form_submit_button("Save Property"):
                    save_data('house_inventory', {"owner_name": o_name, "location": loc, "rent": rent, "status": "Available"})
        
        elif mode == "client":
            with st.form("client_form"):
                c_name = st.text_input("Client Name")
                contact = st.text_input("Contact Number")
                req = st.text_area("Requirement Details")
                if st.form_submit_button("Save Client"):
                    save_data('client_leads', {"client_name": c_name, "contact": contact, "req_location": req})

        elif mode == "visit":
            with st.form("visit_form"):
                c_id = st.text_input("Client ID / Name")
                h_id = st.text_input("Property ID / Name")
                v_date = st.date_input("Visit Date")
                if st.form_submit_button("Schedule Visit"):
                    # Custom logic for visits table
                    st.info("Visit Scheduled!")

        elif mode == "pending" or mode == "done":
            with st.form("deal_form"):
                deal_client = st.text_input("Client Name")
                deal_amount = st.number_input("Final Amount", min_value=0)
                status = "Done Deal" if mode == "done" else "Pending"
                if st.form_submit_button("Submit Deal Status"):
                    # Custom logic for deals table
                    st.success(f"Deal marked as {status}")
        
        if st.button("❌ Close Form"):
            del st.session_state.entry_mode
            st.rerun()

# --- 6. DASHBOARD PREVIEW (The Layout you Liked) ---
st.write("### 📊 Live Dashboard")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Houses", "125", "+5")
m2.metric("Active Leads", "42", "New")
m3.metric("Visits Today", "8", "Action Required")
m4.metric("Revenue", "PKR 450k", "+12%")

# Row 2: Property Cards & Pipeline
col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.subheader("🏠 Inventory Preview")
    # Show last 4 properties in professional cards
    st.markdown("""
        <div style="display: flex; gap: 10px;">
            <div class="action-btn" style="flex:1;">Unit 102 - F-11<br>75k/mo</div>
            <div class="action-btn" style="flex:1;">Villa 305 - DHA<br>6.5 Cr</div>
        </div>
    """, unsafe_allow_html=True)

with col_right:
    st.subheader("🔄 Pipeline")
    st.write("Recent Activity Log...")
    st.caption("Umer: Visit Done for DHA Villa")
    st.caption("Tariq: New Lead Added - G-11")

st.divider()
st.caption("Deewary.com | Manager: Anas | Staff: Sawer Khan, Tariq Hussain, Umer")
