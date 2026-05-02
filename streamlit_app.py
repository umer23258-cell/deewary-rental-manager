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
        <h1 style="color: #FF4B4B; margin: 0; font-family: 'Arial Black';">DEEWARY PROPERTY MANAGER</h1>
        <p style="color: white; letter-spacing: 2px;">OWNER INVENTORY & CLIENT DATABASE</p>
    </div>
""", unsafe_allow_html=True)

# --- 4. SIDEBAR & MENU ---
st.sidebar.title("🔐 Staff Access")
user_name = st.sidebar.selectbox("Apna Naam Select Karen", ["Anas", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "admin786":
    menu = st.sidebar.radio("KAAM SELECT KAREN", [
        "🏠 Dashboard",
        "--- NAYI ENTRY ---",
        "🏠 Ghar ki Entry (Owners)", 
        "👤 Client ki Entry (Tenants)", 
        "⏳ Deal Pending Entry",
        "✅ Deal Done Entry",
        "--- RECORDS & HISTORY ---",
        "📋 Gharon ki History",
        "👥 Clients ki History",
        "📂 Pending Deals History",
        "💰 Done Deals History",
        "🔍 Search & Print PDF"
    ])

    # --- 5. DASHBOARD ---
    if menu == "🏠 Dashboard":
        st.subheader(f"📊 Office Stats - {user_name}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Properties", len(supabase.table('house_inventory').select("id").execute().data))
        c2.metric("Total Clients", len(supabase.table('client_leads').select("id").execute().data))
        c3.metric("Pending Deals", len(supabase.table('deals_pending').select("id").execute().data))

    # --- 6. GHAR KI ENTRY ---
    elif menu == "🏠 Ghar ki Entry (Owners)":
        st.subheader("🏡 Naye Ghar ya Shop ki Detail")
        with st.form("house_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                o_name = st.text_input("Owner ka Naam")
                o_contact = st.text_input("Owner Contact")
                loc = st.text_input("Location / Address")
                portion = st.selectbox("Portion", ["Full House", "Ground Floor", "First Floor", "Basement", "Shop", "Office"])
                size = st.text_input("Size (Marla/Kanal)")
            with col2:
                beds = st.selectbox("Bedrooms", ["1", "2", "3", "4", "5", "6+", "N/A"])
                rent = st.number_input("Demand Rent (PKR)", min_value=0)
                v_time = st.text_input("Visit Time")
                gas = st.radio("Gas?", ["Yes", "No"], horizontal=True)
                water = st.radio("Water?", ["Yes", "No"], horizontal=True)
                elec = st.radio("Electricity?", ["Yes", "No"], horizontal=True)
            other = st.text_area("Other Details")
            if st.form_submit_button("Save House Record"):
                supabase.table('house_inventory').insert({
                    "owner_name": o_name, "contact": o_contact, "location": loc, "portion": portion, 
                    "beds": beds, "rent": rent, "size": size, "gas": gas, "water": water, 
                    "electricity": elec, "visit_time": v_time, "details": other, "added_by": user_name
                }).execute()
                st.success("House Saved!")

    # --- 7. CLIENT KI ENTRY ---
    elif menu == "👤 Client ki Entry (Tenants)":
        st.subheader("👨‍👩‍👧‍👦 Client Requirement Register Karen")
        with st.form("client_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                c_name = st.text_input("Client ka Naam")
                c_contact = st.text_input("Client Contact")
                c_loc = st.text_input("Required Location")
            with c2:
                c_budget = st.number_input("Monthly Budget", min_value=0)
                c_portion = st.selectbox("Requirement", ["Full House", "Portion", "Flat", "Shop", "Office"])
                c_marla = st.text_input("Required Size")
            c_req = st.text_area("Extra Requirements")
            if st.form_submit_button("Save Client Lead"):
                supabase.table('client_leads').insert({
                    "client_name": c_name, "contact": c_contact, "req_location": c_loc, 
                    "budget": c_budget, "req_portion": c_portion, "marla": c_marla, 
                    "requirements": c_req, "added_by": user_name
                }).execute()
                st.success("Client Lead Saved!")

    # --- 8. DEAL PENDING ENTRY ---
    elif menu == "⏳ Deal Pending Entry":
        st.subheader("⏳ Pending Deal Register Karen")
        with st.form("pending_form", clear_on_submit=True):
            p_client = st.text_input("Client Name")
            p_prop = st.text_area("Property Details")
            p_token = st.number_input("Token Amount Received", min_value=0)
            p_date = st.date_input("Expected Closing Date")
            if st.form_submit_button("Save Pending Deal"):
                supabase.table('deals_pending').insert({
                    "client_name": p_client, "property_details": p_prop, 
                    "token_amount": p_token, "expected_date": str(p_date), "agent_name": user_name
                }).execute()
                st.success("Pending Deal Added!")

    # --- 9. DEAL DONE ENTRY ---
    elif menu == "✅ Deal Done Entry":
        st.subheader("✅ Deal Done Detail")
        with st.form("done_form", clear_on_submit=True):
            d_client = st.text_input("Client Name")
            d_owner = st.text_input("Owner Name")
            d_rent = st.number_input("Final Rent", min_value=0)
            d_comm = st.number_input("Commission Earned", min_value=0)
            if st.form_submit_button("Save Done Deal"):
                supabase.table('deals_done').insert({
                    "client_name": d_client, "owner_name": d_owner, 
                    "final_rent": d_rent, "commission": d_comm, "agent_name": user_name
                }).execute()
                st.success("Deal Done Record Saved!")

    # --- 10. HISTORY SECTIONS ---
    elif menu == "📋 Gharon ki History":
        res = supabase.table('house_inventory').select("*").execute()
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)

    elif menu == "👥 Clients ki History":
        res = supabase.table('client_leads').select("*").execute()
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)

    elif menu == "📂 Pending Deals History":
        res = supabase.table('deals_pending').select("*").execute()
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)

    elif menu == "💰 Done Deals History":
        res = supabase.table('deals_done').select("*").execute()
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)

else:
    if pwd != "": st.error("Access Code Ghalat Hai!")

st.divider()
st.caption(f"© {datetime.now().year} Deewary.com | System Active")
