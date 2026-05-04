import streamlit as st
from supabase import create_client
import pandas as pd

# Page Config
st.set_page_config(page_title="Deewary Property Manager", layout="wide")

# Supabase Setup (Apni details secrets.toml mein dalein)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# Sidebar Navigation
st.sidebar.title("🏢 Deewary CRM")
staff_id = st.sidebar.text_input("Enter Staff ID", value="STAFF01")
menu = ["Dashboard", "Add Property", "Client Visits", "Staff Performance"]
choice = st.sidebar.selectbox("Menu", menu)

# --- 1. DASHBOARD VIEW ---
if choice == "Dashboard":
    st.title("Property Dashboard")
    
    # Metrics fetch karna
    props = supabase.table("properties").select("*").execute()
    deals = supabase.table("deals").select("*").execute()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Properties", len(props.data))
    col2.metric("Active Deals", len([d for d in deals.data if d['status'] != 'Closed']))
    col3.metric("Staff Active", "4")

    st.subheader("Recent Listings")
    df = pd.DataFrame(props.data)
    if not df.empty:
        # Display as cards or table
        st.dataframe(df[['title', 'type', 'price', 'status', 'added_by']], use_container_width=True)

# --- 2. ADD PROPERTY ---
elif choice == "Add Property":
    st.title("Add New Property")
    with st.form("prop_form"):
        title = st.text_input("Property Title (e.g. 5 Marla House)")
        p_type = st.selectbox("Type", ["Sale", "Rent"])
        price = st.number_input("Price / Rent")
        address = st.text_area("Address")
        submitted = st.form_submit_button("Save Property")
        
        if submitted:
            data = {"title": title, "type": p_type, "price": price, "address": address, "added_by": staff_id}
            supabase.table("properties").insert(data).execute()
            st.success("Property Added Successfully!")

# --- 3. CLIENT VISITS & DEALS ---
elif choice == "Client Visits":
    st.title("Manage Client Deals")
    
    # Form for new deal/visit
    with st.expander("➕ Register New Visit/Interest"):
        with st.form("deal_form"):
            c_name = st.text_input("Client Name")
            c_phone = st.text_input("Phone Number")
            # Properties ki list fetch karna dropdown ke liye
            props = supabase.table("properties").select("id, title").execute()
            p_options = {p['title']: p['id'] for p in props.data}
            selected_p = st.selectbox("Select Property", list(p_options.keys()))
            status = st.selectbox("Current Status", ["Interested", "Visit Done", "Pending", "Closed"])
            
            if st.form_submit_button("Log Deal"):
                deal_data = {
                    "client_name": c_name, 
                    "client_phone": c_phone, 
                    "property_id": p_options[selected_p],
                    "status": status,
                    "staff_id": staff_id
                }
                supabase.table("deals").insert(deal_data).execute()
                st.info("Deal Logged!")

    # Display Pipeline
    st.subheader("Current Deal Pipeline")
    deals_data = supabase.table("deals").select("*, properties(title)").execute()
    if deals_data.data:
        deals_df = pd.DataFrame(deals_data.data)
        st.table(deals_df[['client_name', 'status', 'staff_id']])

# --- 4. STAFF PERFORMANCE ---
elif choice == "Staff Performance":
    st.title("Staff Leaderboard")
    # Query to count deals per staff
    performance = supabase.table("deals").select("staff_id").execute()
    if performance.data:
        perf_df = pd.DataFrame(performance.data)
        st.bar_chart(perf_df['staff_id'].value_counts())
