import streamlit as st
from supabase import create_client

# Supabase Connection
url = "YOUR_SUPABASE_URL"
key = "YOUR_SUPABASE_KEY"
supabase = create_client(url, key)

st.set_page_config(page_title="Deewary Manager Pro", layout="wide")

# Sidebar Menu
st.sidebar.title("🏢 Deewary Manager")
menu = st.sidebar.radio("Navigation", ["Dashboard", "Inventory", "Client CRM", "Reports"])

if menu == "Dashboard":
    st.header("Dynamic Dashboard")
    
    # Dashboard Cards (Metric Rows)
    col1, col2, col3 = st.columns(3)
    col1.metric("Active Leads", "221", "+5%")
    col2.metric("Done Deals", "61", "12%")
    col3.metric("Pending Deals", "14", "-2%")

    st.divider()
    st.subheader("Recent Activity")
    # Yahan hum Supabase se data fetch karke dikhayenge

elif menu == "Inventory":
    st.header("House Inventory")
    # Form to add new house
    with st.expander("➕ Add New Property"):
        title = st.text_input("Property Name")
        price = st.number_input("Rent Price", min_value=0)
        if st.button("Save Property"):
            supabase.table("houses").insert({"title": title, "rent_price": price}).execute()
            st.success("Property Added!")

elif menu == "Client CRM":
    st.header("Leads & Visiting Tracker")
    # Tables with color coding
    st.info("Yahan Visiting, Done aur Pending deals ki list show hogi.")
