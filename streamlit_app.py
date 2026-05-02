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

# Hide Streamlit UI
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
def delete_record(table_name, record_id):
    supabase.table(table_name).delete().eq("id", record_id).execute()
    st.warning(f"Record ID {record_id} Khatam kar diya gaya hai!")
    st.rerun()

# --- 4. HEADER ---
st.markdown("""
    <div style="text-align: center; background-color: #1E1E1E; padding: 20px; border-radius: 15px; border: 2px solid #FF4B4B;">
        <h1 style="color: #FF4B4B; margin: 0; font-family: 'Arial Black';">DEEWARY PROPERTY MANAGER</h1>
        <p style="color: white; letter-spacing: 2px;">MANAGEMENT PORTAL</p>
    </div>
""", unsafe_allow_html=True)

# --- 5. SIDEBAR & MENU ---
st.sidebar.title("🔐 Staff Access")
user_name = st.sidebar.selectbox("Apna Naam Select Karen", ["Anas", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "admin786":
    menu = st.sidebar.radio("KAAM SELECT KAREN", [
        "🏠 Dashboard",
        "--- NAYI ENTRY ---",
        "🏠 Ghar ki Entry (Owners)", 
        "👤 Client ki Entry (New)",
        "💬 Client in Discussion",
        "⏳ Deal Pending Entry",
        "✅ Deal Done Entry",
        "--- RECORDS & HISTORY ---",
        "📋 Gharon ki History",
        "👥 New Clients History",
        "🗣️ Discussion History",
        "📂 Pending Deals History",
        "💰 Done Deals History"
    ])

    # --- 6. GHAR KI ENTRY FORM ---
    if menu == "🏠 Ghar ki Entry (Owners)":
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
                beds = st.selectbox("Bedrooms (Total)", ["1", "2", "3", "4", "5", "6+", "N/A"])
                rent = st.number_input("Demand Rent (PKR)", min_value=0)
                v_time = st.text_input("Visit Time")
                h_status = st.selectbox("Ghar ka Status", ["Available", "Rent Out"]) # Naya Option
                gas = st.selectbox("Gas Connection", ["Yes", "No", "Single Meter", "Combine Meter"])
                water = st.selectbox("Water Facility", ["Water Supply", "Boor", "Yes", "No"])
                elec = st.selectbox("Electricity", ["Separate Meter", "Combine Meter", "Yes", "No"])
            other = st.text_area("Other Details")
            if st.form_submit_button("Save House Record"):
                supabase.table('house_inventory').insert({
                    "owner_name": o_name, "contact": o_contact, "location": loc, "portion": portion, 
                    "beds": beds, "rent": rent, "size": size, "gas": gas, "water": water, 
                    "electricity": elec, "visit_time": v_time, "status": h_status, "details": other, "added_by": user_name
                }).execute()
                st.success(f"Ghar save ho gaya as {h_status}!")

    # --- 7. NEW CLIENT ENTRY FORM ---
    elif menu == "👤 Client ki Entry (New)":
        st.subheader("👨‍👩‍👧‍👦 New Client Requirements")
        with st.form("client_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                c_name = st.text_input("Client Name")
                c_contact = st.text_input("Contact Number")
                c_beds = st.selectbox("Beds Required", ["1", "2", "3", "4", "5+", "Any"])
            with c2:
                c_budget = st.number_input("Budget (Max)", min_value=0)
                c_loc = st.text_input("Location Required")
                c_status = st.selectbox("Ghar Mila?", ["Still Searching", "Got House"]) # Naya Option
            if st.form_submit_button("Save Client"):
                supabase.table('client_leads').insert({
                    "client_name": c_name, "contact": c_contact, "req_location": c_loc, 
                    "budget": c_budget, "beds_required": c_beds, "status": c_status, "added_by": user_name
                }).execute()
                st.success("Client Requirement Save ho gayi!")

    # --- 10. DEAL DONE ENTRY FORM ---
    elif menu == "✅ Deal Done Entry":
        st.subheader("✅ Deal Done Details")
        st.info(f"Dealing Admin: **{user_name}**") # Ye batayega ke kaun entry kar raha hai
        with st.form("done_form", clear_on_submit=True):
            done_c = st.text_input("Client Name")
            done_o = st.text_input("Owner Name")
            done_prop = st.text_input("Property Address (Jo Rent Out hui)") # Naya Field
            done_rent = st.number_input("Final Rent", min_value=0)
            done_comm = st.number_input("Commission Earned", min_value=0)
            if st.form_submit_button("Save Final Deal"):
                supabase.table('deals_done').insert({
                    "client_name": done_c, "owner_name": done_o, "property_address": done_prop,
                    "final_rent": done_rent, "commission": done_comm, "agent_name": user_name
                }).execute()
                st.success(f"Mubarak ho! Deal Done by {user_name} save ho gayi.")

    # --- 11. HISTORY SECTIONS ---
    elif menu == "📋 Gharon ki History":
        st.subheader("📋 House Inventory History")
        res = supabase.table('house_inventory').select("*").order('id', desc=True).execute()
        if res.data:
            df = pd.DataFrame(res.data)
            for _, row in df.iterrows():
                # Color code for Available vs Rent Out
                status_color = "🟢" if row['status'] == "Available" else "🔴"
                with st.expander(f"{status_color} ID: {row['id']} | {row['owner_name']} - {row['location']}"):
                    st.write(f"**Status:** {row['status']} | **Rent:** {row['rent']} | **Beds:** {row['beds']}")
                    st.write(f"**Added By:** {row['added_by']}")
                    if st.button(f"🗑️ Delete ID {row['id']}", key=f"del_h_{row['id']}"):
                        delete_record('house_inventory', row['id'])
        else: st.info("Abhi koi data nahi hai.")

    elif menu == "💰 Done Deals History":
        st.subheader("💰 Closed Deals History")
        res = supabase.table('deals_done').select("*").order('id', desc=True).execute()
        if res.data:
            df = pd.DataFrame(res.data)
            for _, row in df.iterrows():
                with st.expander(f"✅ ID: {row['id']} | Client: {row['client_name']} (Admin: {row['agent_name']})"):
                    st.write(f"**Property Out:** {row['property_address']}")
                    st.write(f"**Owner:** {row['owner_name']} | **Final Rent:** {row['final_rent']}")
                    st.write(f"**Deal Closed By:** {row['agent_name']}")
                    if st.button(f"🗑️ Delete ID {row['id']}", key=f"del_done_{row['id']}"):
                        delete_record('deals_done', row['id'])

    # Dashboard or other sections...
    elif menu == "🏠 Dashboard":
        st.subheader(f"Welcome back, {user_name}!")
        # Basic Stats
        h_data = supabase.table('house_inventory').select("status").execute().data
        rent_out = len([x for x in h_data if x['status'] == 'Rent Out'])
        available = len([x for x in h_data if x['status'] == 'Available'])
        
        col1, col2 = st.columns(2)
        col1.metric("Ghar Available", available)
        col2.metric("Ghar Rent Out", rent_out)

else:
    if pwd != "": st.error("Access Code Ghalat Hai!")

st.divider()
st.caption(f"© {datetime.now().year} Deewary.com | System Active")
