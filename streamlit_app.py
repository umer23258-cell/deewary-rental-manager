import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
import plotly.express as px  # Dashboard graphs ke liye
from fpdf import FPDF
import io

# --- 1. SUPABASE SETUP ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Deewary CRM", layout="wide", page_icon="🏢")

# Hide Streamlit UI
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# --- 3. DATA FETCHING HELPERS ---
def get_data(table):
    try:
        res = supabase.table(table).select("*").execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

# --- 4. HEADER ---
st.markdown("""
    <div style="text-align: center; background-color: #1E1E1E; padding: 20px; border-radius: 15px; border: 2px solid #FF4B4B;">
        <h1 style="color: #FF4B4B; margin: 0; font-family: 'Arial Black';">DEEWARY PROPERTY MANAGER</h1>
        <p style="color: white; letter-spacing: 2px;">STAFF PROGRESS & DEALS TRACKING</p>
    </div>
""", unsafe_allow_html=True)

# --- 5. STAFF LOGIN ---
st.sidebar.title("🔐 Staff Access")
user_name = st.sidebar.selectbox("Apna Naam Select Karen", ["Anas", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "admin786":
    menu = st.sidebar.radio("KAAM SELECT KAREN", [
        "📊 Dashboard (Daily Progress)",
        "🏠 Ghar ki Entry (Owners)", 
        "👤 Client ki Entry (Tenants)", 
        "🤝 Deals (Pending/Done)",
        "📋 Full History (View Only)"
    ])

    # --- 6. DASHBOARD (DAILY PROGRESS) ---
    if menu == "📊 Dashboard (Daily Progress)":
        st.subheader(f"📅 Daily Progress Report - {datetime.now().strftime('%d %b %Y')}")
        
        # Fetching all data
        df_h = get_data('house_inventory')
        df_d = get_data('deals') # Ensure 'deals' table is in Supabase
        
        # Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Properties", len(df_h))
        m2.metric("Total Deals", len(df_d))
        m3.metric("Pending Deals", len(df_d[df_d['deal_status'] == 'Pending']) if not df_d.empty else 0)
        m4.metric("Closed Deals", len(df_d[df_d['deal_status'] == 'Done']) if not df_d.empty else 0)

        st.divider()
        col_left, col_right = st.columns(2)
        
        with col_left:
            if not df_h.empty:
                st.write("### 👨‍💻 Staff Wise Activity (House Entries)")
                fig = px.bar(df_h, x='added_by', title="Total Entries per Person", color='added_by', template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
        
        with col_right:
            if not df_d.empty:
                st.write("### 💹 Deals Success Ratio")
                fig2 = px.pie(df_d, names='deal_status', title="Pending vs Done", hole=0.4)
                st.plotly_chart(fig2, use_container_width=True)

    # --- 7. DEALS (PENDING / DONE) ---
    elif menu == "🤝 Deals (Pending/Done)":
        st.subheader("🤝 Nayi Deal ki Entry Karen")
        
        with st.form("deals_form", clear_on_submit=True):
            d1, d2 = st.columns(2)
            with d1:
                client_n = st.text_input("Client ka Naam")
                property_id = st.text_input("House ID / Reference")
                deal_type = st.selectbox("Deal ki Qisam", ["Rent", "Sale", "Token"])
            with d2:
                deal_amt = st.number_input("Final Amount (PKR)", min_value=0)
                deal_st = st.selectbox("Status", ["Pending", "Done"])
                deal_date = str(datetime.now().date())
            
            if st.form_submit_button("Save Deal Record"):
                payload = {
                    "client_name": client_n, "house_id": property_id, "deal_type": deal_type,
                    "amount": deal_amt, "deal_status": deal_st, "deal_date": deal_date, "staff_name": user_name
                }
                supabase.table('deals').insert(payload).execute()
                st.success(f"Deal ({deal_st}) record save ho gaya!")

        st.divider()
        st.write("### 🛠️ Deal Update Karen (Pending to Done)")
        pending_deals = get_data('deals')
        if not pending_deals.empty:
            pending_list = pending_deals[pending_deals['deal_status'] == 'Pending']
            if not pending_list.empty:
                deal_to_update = st.selectbox("Select Pending Deal to Mark Done", pending_list['id'])
                if st.button("Mark as DONE ✅"):
                    supabase.table('deals').update({"deal_status": "Done"}).eq("id", deal_to_update).execute()
                    st.success("Deal Mukammal (Done) ho gayi!")
            else:
                st.info("Koi Pending deal nahi hai.")

    # --- 8. ORIGINAL ENTRIES SECTIONS ---
    elif menu == "🏠 Ghar ki Entry (Owners)":
        st.subheader("🏡 Naye Ghar ya Shop ki Detail Darj Karen")
        with st.form("house_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                o_name = st.text_input("Owner ka Naam")
                o_contact = st.text_input("Owner ka Contact Number")
                loc = st.text_input("Location / Address")
                portion = st.selectbox("Portion", ["Full House", "Ground Floor", "First Floor", "Basement", "Shop", "Office"])
            with col2:
                beds = st.selectbox("Bedrooms (Beds)", ["1", "2", "3", "4", "5", "6+", "N/A"])
                rent = st.number_input("Demand Rent (PKR)", min_value=0)
                size = st.text_input("Size (Marla/Kanal)")
                status = st.selectbox("Status", ["Available", "Rent Out"])
            
            other = st.text_area("Other Details")
            if st.form_submit_button("Save House Record"):
                payload = {
                    "owner_name": o_name, "contact": o_contact, "location": loc, 
                    "portion": portion, "beds": beds, "rent": rent, 
                    "size": size, "status": status, "details": other, "added_by": user_name
                }
                supabase.table('house_inventory').insert(payload).execute()
                st.success("House Record Saved!")

    elif menu == "👤 Client ki Entry (Tenants)":
        st.subheader("👨‍👩‍👧‍👦 Client Requirement Register Karen")
        with st.form("client_form", clear_on_submit=True):
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                c_name = st.text_input("Client ka Naam")
                c_contact = st.text_input("Client Contact")
                c_loc = st.text_input("Required Location")
            with c_col2:
                c_budget = st.number_input("Monthly Budget (PKR)", min_value=0)
                c_portion = st.selectbox("Requirement", ["Full House", "Portion", "Flat", "Shop", "Office"])
                c_marla = st.text_input("Required Size")
            
            if st.form_submit_button("Save Client Lead"):
                payload = {
                    "client_name": c_name, "contact": c_contact, "req_location": c_loc, 
                    "budget": c_budget, "req_portion": c_portion, "marla": c_marla, "added_by": user_name
                }
                supabase.table('client_leads').insert(payload).execute()
                st.success("Client Lead Saved!")

    # --- 9. FULL HISTORY ---
    elif menu == "📋 Full History (View Only)":
        tab1, tab2, tab3 = st.tabs(["🏠 House Inventory", "👥 Client Leads", "🤝 Deals History"])
        
        with tab1:
            st.dataframe(get_data('house_inventory'), use_container_width=True)
        with tab2:
            st.dataframe(get_data('client_leads'), use_container_width=True)
        with tab3:
            df_deals_all = get_data('deals')
            if not df_deals_all.empty:
                st.write("✅ **Mukammal Deals**")
                st.dataframe(df_deals_all[df_deals_all['deal_status'] == 'Done'], use_container_width=True)
                st.write("⏳ **Pending Deals**")
                st.dataframe(df_deals_all[df_deals_all['deal_status'] == 'Pending'], use_container_width=True)

else:
    if pwd != "":
        st.error("Please enter correct access code.")

st.divider()
st.caption(f"© {datetime.now().year} Deewary.com | Performance Tracking System Active")
