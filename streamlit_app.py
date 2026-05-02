import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# --- CONNECT TO SUPABASE ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Deewary Office Manager", layout="wide", page_icon="📑")

# --- UI STYLE ---
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6; border-radius: 5px; padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #FF4B4B !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
st.sidebar.title("🏢 Deewary Office")
user_name = st.sidebar.selectbox("Kon kaam kar raha hai?", ["Anas", "Sawer Khan", "Tariq Hussain"])
pin = st.sidebar.text_input("Daftar Code", type="password")

if pin == "admin786":
    # Main Tabs for Entry and History
    tab_entry, tab_history = st.tabs(["➕ Nayi Entry (Input)", "📜 Purani History (Records)"])

    # --- SECTION 1: NAYI ENTRY ---
    with tab_entry:
        entry_mode = st.radio("Kya Enter Karna Hai?", ["Ghar", "Client", "Pending Deal", "Done Deal"], horizontal=True)
        
        if entry_mode == "Ghar":
            with st.form("h_form"):
                st.subheader("🏡 Ghar/Shop ki Detail")
                col1, col2 = st.columns(2)
                with col1:
                    o_name = st.text_input("Owner Name")
                    o_contact = st.text_input("Contact")
                    floor = st.text_input("Floor")
                with col2:
                    marla = st.text_input("Marla")
                    rent = st.number_input("Rent", min_value=0)
                    visit = st.text_input("Visit Time")
                
                details = f"Gas: {st.checkbox('Gas')} | Water: {st.checkbox('Water')} | Elec: {st.checkbox('Electricity')}"
                
                if st.form_submit_button("Save House"):
                    supabase.table('house_inventory').insert({
                        "owner_name": o_name, "contact_number": o_contact, "floor": floor,
                        "marla": marla, "rent": rent, "visit_time": visit, "details": details, "added_by": user_name
                    }).execute()
                    st.success("Ghar ki entry ho gayi!")

        elif entry_mode == "Client":
            with st.form("c_form"):
                st.subheader("👤 Client ki Requirement")
                c_name = st.text_input("Client Name")
                c_contact = st.text_input("Client Contact")
                c_budget = st.number_input("Budget", min_value=0)
                c_area = st.text_input("Area Location")
                if st.form_submit_button("Save Client"):
                    supabase.table('client_leads').insert({
                        "client_name": c_name, "contact_number": c_contact, "budget": c_budget, "preferred_area": c_area, "added_by": user_name
                    }).execute()
                    st.success("Client save ho gaya!")

        # Pending and Done deals forms (Same as before but under this tab)
        # ... [Deals logic remains consistent]

    # --- SECTION 2: HISTORY (ALAG BUTTONS) ---
    with tab_history:
        st.subheader("📂 Office Ka Sara Record")
        
        # Row of Buttons for History
        h_col1, h_col2, h_col3, h_col4 = st.columns(4)
        
        with h_col1:
            if st.button("🏠 Gharon ki History"):
                st.session_state.view = "houses"
        with h_col2:
            if st.button("👥 Client ki History"):
                st.session_state.view = "clients"
        with h_col3:
            if st.button("⏳ Pending Deals History"):
                st.session_state.view = "pending"
        with h_col4:
            if st.button("✅ Done Deals History"):
                st.session_state.view = "done"

        st.divider()

        # Display Logic Based on Button Click
        current_view = st.session_state.get('view', 'houses')

        if current_view == "houses":
            st.write("### 🏠 Registered Houses")
            data = supabase.table('house_inventory').select("*").execute()
            if data.data:
                df = pd.DataFrame(data.data)
                st.dataframe(df.style.highlight_max(axis=0), use_container_width=True)
            
        elif current_view == "clients":
            st.write("### 👥 Client Leads History")
            data = supabase.table('client_leads').select("*").execute()
            if data.data:
                st.dataframe(pd.DataFrame(data.data), use_container_width=True)

        elif current_view == "pending":
            st.write("### ⏳ Pending Deals (Token Received)")
            data = supabase.table('deals_pending').select("*").execute()
            if data.data:
                st.table(pd.DataFrame(data.data))

        elif current_view == "done":
            st.write("### ✅ Closed Deals (Money Earned)")
            data = supabase.table('deals_done').select("*").execute()
            if data.data:
                st.dataframe(pd.DataFrame(data.data), use_container_width=True)

else:
    st.warning("Daftar ka Access Code enter karen.")
