import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# --- SUPABASE SETUP ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Deewary Dashboard", layout="wide")

# --- SIDEBAR CONTROL PANEL ---
st.sidebar.title("🏢 DEEWARY OFFICE")
user_name = st.sidebar.selectbox("Staff Name", ["Anas", "Sawer Khan", "Tariq Hussain"])
pin = st.sidebar.text_input("Access Code", type="password")

if pin == "admin786":
    st.sidebar.divider()
    # Dashboard Button
    if st.sidebar.button("📊 DAILY DASHBOARD"):
        st.session_state.page = "dashboard"
    
    st.sidebar.subheader("➕ NAYI ENTRY")
    if st.sidebar.button("🏠 Ghar ki Entry"): st.session_state.page = "add_house"
    if st.sidebar.button("👤 Client ki Entry"): st.session_state.page = "add_client"
    if st.sidebar.button("⏳ Deal Pending"): st.session_state.page = "add_pending"
    if st.sidebar.button("✅ Deal Done"): st.session_state.page = "add_done"

    st.sidebar.subheader("📜 HISTORY")
    if st.sidebar.button("📋 Gharon ki List"): st.session_state.page = "hist_house"
    if st.sidebar.button("👥 Clients ki List"): st.session_state.page = "hist_client"

    # --- MAIN AREA ---
    page = st.session_state.get('page', 'dashboard')

    if page == "dashboard":
        st.title("📊 Daily Business Overview")
        
        # Data Fetching for Dashboard
        h_data = supabase.table('house_inventory').select("*").execute()
        c_data = supabase.table('client_leads').select("*").execute()
        p_data = supabase.table('deals_pending').select("*").execute()
        d_data = supabase.table('deals_done').select("*").execute()

        # Metrics Columns
        m1, m2, m3, m4 = st.columns(4)
        
        # Aaj ki date
        today = datetime.now().strftime("%Y-%m-%d")
        
        with m1:
            total_h = len(h_data.data) if h_data.data else 0
            st.metric("Total Ghar", total_h)
        with m2:
            total_c = len(c_data.data) if c_data.data else 0
            st.metric("Total Clients", total_c)
        with m3:
            pending = len(p_data.data) if p_data.data else 0
            st.metric("Pending Deals", pending, delta_color="normal")
        with m4:
            done = len(d_data.data) if d_data.data else 0
            st.metric("Deals Done ✅", done)

        st.divider()
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("👨‍💻 Staff Ki Karkardagi (Entries)")
            if h_data.data:
                df_h = pd.DataFrame(h_data.data)
                staff_counts = df_h['added_by'].value_counts()
                st.bar_chart(staff_counts)
            else:
                st.write("Abhi tak koi entry nahi hui.")

        with col_right:
            st.subheader("📅 Aaj Ka Naya Record")
            # Filtering today's entries
            if h_data.data:
                df_today = pd.DataFrame(h_data.data)
                # Convert created_at to date string for comparison
                df_today['date'] = pd.to_datetime(df_today['created_at']).dt.strftime('%Y-%m-%d')
                today_entries = df_today[df_today['date'] == today]
                
                if not today_entries.empty:
                    st.write(f"Aaj {len(today_entries)} naye ghar add huay:")
                    st.dataframe(today_entries[['owner_name', 'location', 'added_by']], use_container_width=True)
                else:
                    st.info("Aaj abhi tak koi naya ghar add nahi hua.")

    # --- Baqi Pages (Forms & History) ---
    elif page == "add_house":
        st.header("🏠 Naye Ghar ki Entry")
        # [Wohi purana form jo upar banaya tha]
        with st.form("h_form"):
            o_name = st.text_input("Owner Name")
            o_contact = st.text_input("Contact")
            floor = st.text_input("Floor")
            marla = st.text_input("Marla")
            rent = st.number_input("Rent", min_value=0)
            if st.form_submit_button("Save"):
                supabase.table('house_inventory').insert({
                    "owner_name": o_name, "contact_number": o_contact, "floor": floor, 
                    "marla": marla, "rent": rent, "added_by": user_name
                }).execute()
                st.success("Save ho gaya!")

    elif page == "hist_house":
        st.header("📋 Gharon ki List")
        res = supabase.table('house_inventory').select("*").execute()
        if res.data:
            st.dataframe(pd.DataFrame(res.data), use_container_width=True)

else:
    st.title("🏠 Deewary Office Management System")
    st.warning("Ghalat Code! Meharbani kar ke sahi code enter karen.")
