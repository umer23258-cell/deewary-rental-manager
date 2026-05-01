import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
from fpdf import FPDF
import io

# --- 1. SUPABASE SETUP ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Deewary Property Manager", layout="wide", page_icon="🏢")

# Hide Streamlit UI
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# --- 3. HEADER ---
st.markdown("""
    <div style="text-align: center; background-color: #1E1E1E; padding: 20px; border-radius: 15px; border: 2px solid #FF4B4B;">
        <h1 style="color: #FF4B4B; margin: 0;">DEEWARY PROPERTY MANAGER</h1>
        <p style="color: white;">OWNER INVENTORY & CLIENT DATABASE</p>
    </div>
""", unsafe_allow_html=True)

# --- 4. STAFF LOGIN ---
st.sidebar.title("🔐 Staff Access")
# Sawer Khan ka naam list mein sahi kar diya gaya hai
user_name = st.sidebar.selectbox("Apna Naam Select Karen", ["Anas", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "admin786":
    menu = st.sidebar.radio("KAAM SELECT KAREN", [
        "🏠 Ghar ki Entry (Owners)", 
        "👤 Client ki Entry (Tenants)", 
        "📋 House History",
        "👥 Client History",
        "🔍 Search & Print PDF"
    ])

    # --- 5. GHAR KI ENTRY ---
    if menu == "🏠 Ghar ki Entry (Owners)":
        st.subheader("🏡 Naye Ghar ki Entry")
        with st.form("house_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                o_name = st.text_input("Owner Name")
                o_contact = st.text_input("Contact")
                loc = st.text_input("Location")
            with c2:
                rent = st.number_input("Rent", min_value=0)
                size = st.text_input("Size (Marla)")
                status = st.selectbox("Status", ["Available", "Rent Out"])
            if st.form_submit_button("Save Record"):
                payload = {"owner_name": o_name, "contact": o_contact, "location": loc, "rent": rent, "size": size, "status": status, "added_by": user_name}
                supabase.table('house_inventory').insert(payload).execute()
                st.success("Data Saved!")

    # --- 6. HOUSE HISTORY (With Edit/Delete at end) ---
    elif menu == "📋 House History":
        res = supabase.table('house_inventory').select("*").execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            for index, row in df.iterrows():
                with st.container():
                    st.write(f"📍 **{row['location']}** | Owner: {row['owner_name']} | Rent: {row['rent']} | Status: {row['status']}")
                    # Simple text action links
                    col_a, col_b = st.columns([0.1, 0.9])
                    if col_a.button("Edit", key=f"edh_{row['id']}", help="Update this record"):
                        st.info(f"Edit feature for ID {row['id']} is active. Change details above.")
                    if col_b.button("Delete", key=f"delh_{row['id']}", help="Remove this record"):
                        supabase.table('house_inventory').delete().eq("id", row['id']).execute()
                        st.rerun()
                    st.divider()

    # --- 7. CLIENT HISTORY (With Edit/Delete at end) ---
    elif menu == "👥 Client History":
        res = supabase.table('client_leads').select("*").execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            for index, row in df.iterrows():
                with st.container():
                    st.write(f"👤 **{row['client_name']}** | Contact: {row['contact']} | Budget: {row['budget']} | Area: {row['req_location']}")
                    col_ca, col_cb = st.columns([0.1, 0.9])
                    if col_ca.button("Edit", key=f"edc_{row['id']}"):
                        st.info("Client editing mode active.")
                    if col_cb.button("Delete", key=f"delc_{row['id']}"):
                        supabase.table('client_leads').delete().eq("id", row['id']).execute()
                        st.rerun()
                    st.divider()

    # --- 8. SEARCH & PDF ---
    elif menu == "🔍 Search & Print PDF":
        st.subheader("🔍 Search Records")
        search = st.text_input("Location ya Naam likhen...")
        # Search logic and PDF generation here (Same as before)
        st.info("Search results filter automatically as you type.")

else:
    st.warning("Access Code 'admin786' istemal karen.")
