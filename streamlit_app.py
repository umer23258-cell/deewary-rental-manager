import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# --- 1. SUPABASE SETUP ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. PAGE CONFIG & UI ---
st.set_page_config(page_title="Deewary Property Manager", layout="wide", page_icon="🏢")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 3. HEADER ---
st.markdown("""
    <div style="text-align: center; background-color: #1E1E1E; padding: 20px; border-radius: 15px; border: 2px solid #FF4B4B;">
        <h1 style="color: #FF4B4B; margin: 0; font-family: 'Arial Black';">DEEWARY PROPERTY MANAGER</h1>
        <p style="color: white; letter-spacing: 2px;">OWNER INVENTORY & CLIENT DATABASE</p>
    </div>
""", unsafe_allow_html=True)

# --- 4. STAFF LOGIN ---
st.sidebar.title("🔐 Staff Access")
# Aapke office ke larkon ke naam update kar diye hain
user_name = st.sidebar.selectbox("Apna Naam Select Karen", ["Anas", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "admin786":
    menu = st.sidebar.radio("KAAM SELECT KAREN", [
        "🏠 Ghar ki Entry (Owners)", 
        "👤 Client ki Entry (Tenants)", 
        "📋 House History",
        "👥 Client History",
        "🔍 Search All Data"
    ])

    # --- 5. GHAR KI ENTRY ---
    if menu == "🏠 Ghar ki Entry (Owners)":
        st.subheader("🏡 Naye Ghar ya Shop ki Detail Darj Karen")
        with st.form("house_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                o_name = st.text_input("Owner ka Naam")
                o_contact = st.text_input("Owner ka Contact Number")
                loc = st.text_input("Location / Address")
                size = st.text_input("Size (Marla/Kanal)")
                portion = st.selectbox("Portion", ["Full House", "Ground Floor", "First Floor", "Basement", "Shop", "Office"])
            with col2:
                rent = st.number_input("Demand Rent (PKR)", min_value=0)
                v_time = st.text_input("Visit Time")
                st.write("**Sahuliyat:**")
                c1, c2, c3 = st.columns(3)
                w = c1.checkbox("Pani")
                g = c2.checkbox("Gas")
                e = c3.checkbox("Bijli")
                status = st.selectbox("Status", ["Available", "Rent Out"])
            other = st.text_area("Other Details")
            if st.form_submit_button("Save House Record"):
                payload = {"owner_name": o_name, "contact": o_contact, "location": loc, "size": size, "portion": portion, "rent": rent, "visit_time": v_time, "water": w, "gas": g, "electricity": e, "status": status, "details": other, "added_by": user_name}
                supabase.table('house_inventory').insert(payload).execute()
                st.success("House Record Saved!")

    # --- 6. CLIENT KI ENTRY ---
    elif menu == "👤 Client ki Entry (Tenants)":
        st.subheader("👨‍👩‍👧‍👦 Client Requirement Register Karen")
        with st.form("client_form", clear_on_submit=True):
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                c_name = st.text_input("Client ka Naam")
                c_contact = st.text_input("Client Contact")
                c_loc = st.text_input("Required Location")
                c_budget = st.number_input("Monthly Budget (PKR)", min_value=0)
            with c_col2:
                c_portion = st.selectbox("Requirement", ["Full House", "Portion", "Flat", "Shop", "Office"])
                c_family = st.text_input("Family Members")
                c_job = st.text_input("Job / Business")
            c_req = st.text_area("Extra Requirements")
            if st.form_submit_button("Save Client Lead"):
                payload = {"client_name": c_name, "contact": c_contact, "req_location": c_loc, "budget": c_budget, "req_portion": c_portion, "family": c_family, "job": c_job, "requirements": c_req, "added_by": user_name}
                supabase.table('client_leads').insert(payload).execute()
                st.success("Client Lead Saved!")

    # --- 7. HOUSE HISTORY ---
    elif menu == "📋 House History":
        st.subheader("🏠 Registered Houses & Shops")
        res = supabase.table('house_inventory').select("*").execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else: st.info("No records found.")

    # --- 8. CLIENT HISTORY ---
    elif menu == "👥 Client History":
        st.subheader("👥 Tenant Requirements History")
        res = supabase.table('client_leads').select("*").execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else: st.info("No client records found.")

    # --- 9. SEARCH ALL DATA ---
    elif menu == "🔍 Search All Data":
        st.subheader("🔍 Master Search")
        search_query = st.text_input("Search by Location, Name or Contact...")
        
        col_h, col_c = st.tabs(["🏠 Houses", "👥 Clients"])
        
        with col_h:
            res_h = supabase.table('house_inventory').select("*").execute()
            df_h = pd.DataFrame(res_h.data)
            if not df_h.empty:
                if search_query:
                    df_h = df_h[df_h.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
                st.dataframe(df_h, use_container_width=True)
        
        with col_c:
            res_c = supabase.table('client_leads').select("*").execute()
            df_c = pd.DataFrame(res_c.data)
            if not df_c.empty:
                if search_query:
                    df_c = df_c[df_c.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
                st.dataframe(df_c, use_container_width=True)

else:
    st.warning("Please enter correct access code.")

st.divider()
st.caption(f"© {datetime.now().year} Deewary.com | Property Management System")
