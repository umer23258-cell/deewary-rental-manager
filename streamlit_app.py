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
        "👤 Client ki Entry (New)",
        "💬 Client in Discussion",
        "⏳ Deal Pending Entry",
        "✅ Deal Done Entry",
        "--- RECORDS & HISTORY ---",
        "📋 Gharon ki History",
        "👥 New Clients History",
        "🗣️ Discussion History",
        "📂 Pending Deals History",
        "💰 Done Deals History",
        "🔍 Search & Print PDF"
    ])

    # --- 5. GHAR KI ENTRY ---
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
                gas = st.selectbox("Gas Connection", ["Yes", "No", "Single Meter", "Combine Meter"])
                water = st.selectbox("Water Facility", ["Water Supply", "Boor", "Yes", "No"])
                elec = st.selectbox("Electricity", ["Separate Meter", "Combine Meter", "Yes", "No"])
            other = st.text_area("Other Details")
            if st.form_submit_button("Save House Record"):
                supabase.table('house_inventory').insert({"owner_name": o_name, "contact": o_contact, "location": loc, "portion": portion, "beds": beds, "rent": rent, "size": size, "gas": gas, "water": water, "electricity": elec, "visit_time": v_time, "details": other, "added_by": user_name}).execute()
                st.success("House Saved!")

    # --- 6. CLIENT IN DISCUSSION (Naya Button) ---
    elif menu == "💬 Client in Discussion":
        st.subheader("💬 Jin Clients se Baat Chal rahi hai")
        with st.form("discussion_form", clear_on_submit=True):
            d_client = st.text_input("Client Name")
            d_phone = st.text_input("Phone Number")
            d_prop = st.text_input("Kis Property pe baat ho rahi hai?")
            d_status = st.text_area("Kya baat hui? (Update)")
            if st.form_submit_button("Save Discussion"):
                supabase.table('client_discussions').insert({"client_name": d_client, "contact": d_phone, "property": d_prop, "notes": d_status, "agent": user_name}).execute()
                st.success("Discussion Saved!")

    # --- 7. DEAL PENDING ENTRY ---
    elif menu == "⏳ Deal Pending Entry":
        st.subheader("⏳ Pending Deal (Token Received)")
        with st.form("pending_form", clear_on_submit=True):
            p_client = st.text_input("Client Name")
            p_prop = st.text_area("Property Detail")
            p_token = st.number_input("Token Amount", min_value=0)
            p_date = st.date_input("Closing Date")
            if st.form_submit_button("Save Pending"):
                supabase.table('deals_pending').insert({"client_name": p_client, "property_details": p_prop, "token_amount": p_token, "expected_date": str(p_date), "agent_name": user_name}).execute()
                st.success("Pending Deal Recorded!")

    # --- 8. DEAL DONE ENTRY ---
    elif menu == "✅ Deal Done Entry":
        st.subheader("✅ Deal Done (Mubarak ho!)")
        with st.form("done_form", clear_on_submit=True):
            done_c = st.text_input("Client Name")
            done_o = st.text_input("Owner Name")
            done_rent = st.number_input("Final Rent", min_value=0)
            done_comm = st.number_input("Commission", min_value=0)
            if st.form_submit_button("Save Done Deal"):
                supabase.table('deals_done').insert({"client_name": done_c, "owner_name": done_o, "final_rent": done_rent, "commission": done_comm, "agent_name": user_name}).execute()
                st.success("Deal Done Saved!")

    # --- 9. CLIENT ENTRY (New) ---
    elif menu == "👤 Client ki Entry (New)":
        st.subheader("👨‍👩‍👧‍👦 New Client Requirements")
        with st.form("client_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                c_name = st.text_input("Client Name")
                c_contact = st.text_input("Contact")
                c_beds = st.selectbox("Beds Required", ["1", "2", "3", "4", "5+", "Any"])
            with c2:
                c_budget = st.number_input("Budget", min_value=0)
                c_loc = st.text_input("Location Required")
            if st.form_submit_button("Save Client"):
                supabase.table('client_leads').insert({"client_name": c_name, "contact": c_contact, "req_location": c_loc, "budget": c_budget, "beds_required": c_beds, "added_by": user_name}).execute()
                st.success("Client Saved!")

    # --- 10. HISTORY SECTIONS ---
    elif menu == "📋 Gharon ki History":
        res = supabase.table('house_inventory').select("*").execute()
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)

    elif menu == "🗣️ Discussion History":
        res = supabase.table('client_discussions').select("*").execute()
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
