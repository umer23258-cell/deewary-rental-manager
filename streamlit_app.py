import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
import plotly.express as px # Dashboard ke liye

# --- 1. SUPABASE SETUP ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Deewary CRM", layout="wide", page_icon="🏢")

# Hide Streamlit UI
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
def get_data(table):
    res = supabase.table(table).select("*").execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()

# --- 4. HEADER ---
st.markdown("""
    <div style="text-align: center; background-color: #1E1E1E; padding: 10px; border-radius: 15px; border-bottom: 5px solid #FF4B4B;">
        <h1 style="color: #FF4B4B; margin: 0;">DEEWARY PROPERTY MANAGER</h1>
        <p style="color: white;">Deals Tracking & Staff Performance Dashboard</p>
    </div>
""", unsafe_allow_html=True)

# --- 5. STAFF LOGIN ---
st.sidebar.title("🔐 Staff Access")
user_name = st.sidebar.selectbox("Apna Naam Select Karen", ["Anas", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "admin786":
    menu = st.sidebar.radio("MAIN MENU", [
        "📊 Dashboard (Progress)",
        "🏠 Inventory Entry",
        "🤝 Deals Management",
        "📋 All History Records"
    ])

    # --- 6. DASHBOARD (PROGRESS) ---
    if menu == "📊 Dashboard (Progress)":
        st.subheader(f"🚀 Daily Progress Dashboard - {datetime.now().strftime('%d %B %Y')}")
        
        df_h = get_data('house_inventory')
        df_d = get_data('deals') # Make sure this table exists in Supabase
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Properties", len(df_h))
        with col2:
            pending = len(df_d[df_d['deal_status'] == 'Pending']) if not df_d.empty else 0
            st.metric("Pending Deals", pending)
        with col3:
            done = len(df_d[df_d['deal_status'] == 'Done']) if not df_d.empty else 0
            st.metric("Deals Closed", done)

        st.divider()
        st.subheader("👨‍💻 Staff Performance (Entries per Person)")
        if not df_h.empty:
            perf_df = df_h.groupby('added_by').size().reset_index(name='Total Entries')
            fig = px.bar(perf_df, x='added_by', y='Total Entries', color='added_by', title="Ghar ki Entries by Staff")
            st.plotly_chart(fig, use_container_width=True)

    # --- 7. INVENTORY ENTRY ---
    elif menu == "🏠 Inventory Entry":
        st.subheader("🏡 Naye Ghar ya Shop ki Detail")
        with st.form("house_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                o_name = st.text_input("Owner Name")
                loc = st.text_input("Location")
                portion = st.selectbox("Portion", ["Full House", "Portion", "Shop", "Office"])
            with c2:
                rent = st.number_input("Demand Rent", min_value=0)
                size = st.text_input("Size (Marla)")
                status = st.selectbox("Status", ["Available", "Rent Out"])
            
            if st.form_submit_button("Save Property"):
                payload = {"owner_name": o_name, "location": loc, "portion": portion, "rent": rent, "size": size, "status": status, "added_by": user_name}
                supabase.table('house_inventory').insert(payload).execute()
                st.success("Property Saved!")

    # --- 8. DEALS MANAGEMENT ---
    elif menu == "🤝 Deals Management":
        st.subheader("🤝 New Deal Entry (Pending/Done)")
        with st.form("deal_form", clear_on_submit=True):
            d1, d2 = st.columns(2)
            with d1:
                c_name = st.text_input("Client/Tenant Name")
                h_id = st.text_input("House ID (Jis ghar ki deal hai)")
                d_type = st.selectbox("Deal Type", ["Rent", "Sale", "Token"])
            with d2:
                amt = st.number_input("Final Amount", min_value=0)
                d_status = st.selectbox("Deal Status", ["Pending", "Done"])
            
            if st.form_submit_button("Save Deal Record"):
                deal_payload = {
                    "client_name": c_name, "house_id": h_id, "deal_type": d_type, 
                    "amount": amt, "deal_status": d_status, "staff_name": user_name
                }
                supabase.table('deals').insert(deal_payload).execute()
                st.success(f"Deal {d_status} Entry Saved!")

    # --- 9. ALL HISTORY RECORDS ---
    elif menu == "📋 All History Records":
        st.subheader("📋 Records History")
        h_tab, p_tab, d_tab = st.tabs(["🏠 All Properties", "⏳ Pending Deals", "✅ Done Deals"])
        
        df_deals = get_data('deals')
        
        with h_tab:
            st.dataframe(get_data('house_inventory'), use_container_width=True)
            
        with p_tab:
            if not df_deals.empty:
                pending_df = df_deals[df_deals['deal_status'] == 'Pending']
                st.dataframe(pending_df, use_container_width=True)
            else: st.write("No Pending Deals.")
            
        with d_tab:
            if not df_deals.empty:
                done_df = df_deals[df_deals['deal_status'] == 'Done']
                st.dataframe(done_df, use_container_width=True)
            else: st.write("No Closed Deals.")

else:
    if pwd != "": st.error("Access Code Ghalat Hai!")

st.divider()
st.caption(f"© {datetime.now().year} Deewary.com | Performance Tracking System")
