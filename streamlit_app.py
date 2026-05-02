import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# --- SETUP ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Deewary Real Estate", layout="wide")

# --- UI HEADER ---
st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🏠 DEEWARY REAL ESTATE MANAGER</h1>", unsafe_allow_html=True)

# --- SIDEBAR LOGIN ---
st.sidebar.title("🔐 Staff Login")
user_name = st.sidebar.selectbox("Apna Naam Select Karen", ["Sawer Khan", "Tariq Hussain", "Admin"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "admin786":
    menu = st.sidebar.radio("MENU", [
        "🏠 Ghar ki Entry", 
        "👤 Client ki Entry", 
        "🤝 Deals Tracker (Pending/Done)",
        "📊 View All Records"
    ])

    # 1. GHAR KI ENTRY
    if menu == "🏠 Ghar ki Entry":
        st.subheader("Naye Ghar ki Detail")
        with st.form("house_form"):
            col1, col2 = st.columns(2)
            with col1:
                o_name = st.text_input("Owner Name")
                o_phone = st.text_input("Owner Contact")
                loc = st.text_input("Location")
            with col2:
                rent = st.number_input("Demand Rent", min_value=0)
                beds = st.selectbox("Beds", ["1","2","3","4","5+"])
                portion = st.selectbox("Type", ["Full House", "Upper", "Lower", "Shop"])
            
            if st.form_submit_button("Save House"):
                data = {"owner_name": o_name, "contact": o_phone, "location": loc, "rent": rent, "beds": beds, "portion": portion, "added_by": user_name}
                supabase.table('house_inventory').insert(data).execute()
                st.success("Ghar save ho gaya!")

    # 2. CLIENT ENTRY
    elif menu == "👤 Client ki Entry":
        st.subheader("Client ki Requirement")
        with st.form("client_form"):
            c_name = st.text_input("Client Name")
            c_phone = st.text_input("Client Contact")
            budget = st.number_input("Budget", min_value=0)
            req_loc = st.text_input("Area Required")
            
            if st.form_submit_button("Save Client"):
                data = {"client_name": c_name, "contact": c_phone, "budget": budget, "req_location": req_loc, "added_by": user_name}
                supabase.table('client_leads').insert(data).execute()
                st.success("Client detail save ho gayi!")

    # 3. DEALS TRACKER (Pending/Done)
    elif menu == "🤝 Deals Tracker (Pending/Done)":
        st.subheader("Deals ki Surat-e-haal")
        
        # New Deal Entry
        with st.expander("➕ New Deal Add Karen"):
            # Fetch lists for dropdowns
            houses = supabase.table('house_inventory').select("id, location").eq("status", "Available").execute()
            clients = supabase.table('client_leads').select("id, client_name").execute()
            
            h_list = {f"ID: {r['id']} - {r['location']}": r['id'] for r in houses.data}
            c_list = {f"ID: {r['id']} - {r['client_name']}": r['id'] for r in clients.data}
            
            sel_h = st.selectbox("Ghar Select Karen", list(h_list.keys()))
            sel_c = st.selectbox("Client Select Karen", list(c_list.keys()))
            d_status = st.selectbox("Deal Status", ["Pending", "Done"])
            comm = st.number_input("Commission (Expected/Earned)", min_value=0)
            
            if st.button("Save Deal"):
                deal_payload = {
                    "house_id": h_list[sel_h],
                    "client_id": c_list[sel_c],
                    "deal_status": d_status,
                    "commission_earned": comm,
                    "agent_name": user_name
                }
                supabase.table('deals_tracker').insert(deal_payload).execute()
                st.success("Deal Record Update ho gaya!")

        # Display Deals
        st.divider()
        deals_res = supabase.table('deals_tracker').select("*, house_inventory(location), client_leads(client_name)").execute()
        if deals_res.data:
            df_deals = pd.DataFrame(deals_res.data)
            st.write("### Sab Deals ki List")
            st.dataframe(df_deals)

    # 4. VIEW ALL
    elif menu == "📊 View All Records":
        tab1, tab2 = st.tabs(["Ghar", "Clients"])
        with tab1:
            res = supabase.table('house_inventory').select("*").execute()
            st.dataframe(pd.DataFrame(res.data))
        with tab2:
            res = supabase.table('client_leads').select("*").execute()
            st.dataframe(pd.DataFrame(res.data))

else:
    if pwd: st.error("Ghalat Password!")
