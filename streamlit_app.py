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

# Custom CSS for clean tables
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stButton>button {width: 100%; border-radius: 5px; height: 1.5em; line-height: 1em; padding: 0;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER ---
st.markdown("""
    <div style="text-align: center; background-color: #1E1E1E; padding: 20px; border-radius: 15px; border: 2px solid #FF4B4B;">
        <h1 style="color: #FF4B4B; margin: 0;">DEEWARY PROPERTY MANAGER</h1>
        <p style="color: white;">OWNER INVENTORY & CLIENT DATABASE</p>
    </div>
""", unsafe_allow_html=True)

# --- 4. STAFF LOGIN ---
st.sidebar.title("🔐 Staff Access")
user_name = st.sidebar.selectbox("Apna Naam Select Karen", ["Anas", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "admin786":
    menu = st.sidebar.radio("KAAM SELECT KAREN", [
        "🏠 Ghar ki Entry", 
        "👤 Client ki Entry", 
        "📋 House History (Edit/Delete)",
        "👥 Client History (Edit/Delete)",
        "🔍 Search & Search by ID"
    ])

    # --- 5. HOUSE HISTORY WITH TABLE BUTTONS ---
    if menu == "📋 House History (Edit/Delete)":
        st.subheader("🏠 Property Records")
        res = supabase.table('house_inventory').select("*").order('id').execute()
        data = res.data
        
        if data:
            # Table Header
            cols = st.columns([0.5, 1.5, 1.5, 1, 1, 1, 1])
            cols[0].write("**ID**")
            cols[1].write("**Owner**")
            cols[2].write("**Location**")
            cols[3].write("**Rent**")
            cols[4].write("**Status**")
            cols[5].write("**Edit**")
            cols[6].write("**Delete**")
            st.divider()

            for row in data:
                c = st.columns([0.5, 1.5, 1.5, 1, 1, 1, 1])
                c[0].write(row['id'])
                c[1].write(row['owner_name'])
                c[2].write(row['location'])
                c[3].write(row['rent'])
                c[4].write(row['status'])
                
                # Edit Button
                if c[5].button("📝", key=f"ed_{row['id']}"):
                    st.session_state.edit_id = row['id']
                    st.info(f"ID {row['id']} select ho gayi hai. Niche details update karen.")

                # Delete Button
                if c[6].button("🗑️", key=f"del_{row['id']}"):
                    supabase.table('house_inventory').delete().eq("id", row['id']).execute()
                    st.rerun()

    # --- 6. CLIENT HISTORY WITH TABLE BUTTONS ---
    elif menu == "👥 Client History (Edit/Delete)":
        st.subheader("👥 Client Records")
        res = supabase.table('client_leads').select("*").order('id').execute()
        data = res.data
        
        if data:
            cols = st.columns([0.5, 1.5, 1.5, 1, 1, 1])
            cols[0].write("**ID**")
            cols[1].write("**Client**")
            cols[2].write("**Area**")
            cols[3].write("**Budget**")
            cols[4].write("**Edit**")
            cols[5].write("**Delete**")
            st.divider()

            for row in data:
                c = st.columns([0.5, 1.5, 1.5, 1, 1, 1])
                c[0].write(row['id'])
                c[1].write(row['client_name'])
                c[2].write(row['req_location'])
                c[3].write(row['budget'])
                
                if c[4].button("📝", key=f"ced_{row['id']}"):
                    st.info(f"Client ID {row['id']} edit mode active.")
                
                if c[5].button("🗑️", key=f"cdel_{row['id']}"):
                    supabase.table('client_leads').delete().eq("id", row['id']).execute()
                    st.rerun()

    # --- 7. SEARCH BY ID (Special Feature) ---
    elif menu == "🔍 Search & Search by ID":
        st.subheader("🔍 Search via ID or Details")
        search_id = st.number_input("Enter Record ID to Action", min_value=0, step=1)
        if st.button("Find & Action"):
            # Yahan ID se specific record nikaal kar edit/delete dikhayen
            st.write(f"Searching for ID: {search_id}...")

    # (Ghar aur Client ki Entry wale section purane hi rahenge)
    elif menu == "🏠 Ghar ki Entry":
        st.subheader("🏡 Naye Ghar ki Entry")
        with st.form("h_form"):
            o = st.text_input("Owner Name")
            l = st.text_input("Location")
            r = st.number_input("Rent")
            if st.form_submit_button("Save"):
                supabase.table('house_inventory').insert({"owner_name":o, "location":l, "rent":r, "added_by":user_name}).execute()
                st.success("Saved!")

else:
    st.warning("Access Code 'admin786' lagayen.")
