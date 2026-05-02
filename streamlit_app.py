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

# --- 3. HELPER FUNCTIONS ---
def delete_record(table_name, record_id):
    supabase.table(table_name).delete().eq("id", record_id).execute()
    st.warning(f"Record ID {record_id} delete kar diya gaya hai.")
    st.rerun()

def update_record(table_name, record_id, updated_data):
    supabase.table(table_name).update(updated_data).eq("id", record_id).execute()
    st.success(f"Record ID {record_id} update ho gaya!")
    st.rerun()

# --- 4. HEADER ---
st.markdown("""
    <div style="text-align: center; background-color: #1E1E1E; padding: 20px; border-radius: 15px; border: 2px solid #FF4B4B;">
        <h1 style="color: #FF4B4B; margin: 0; font-family: 'Arial Black';">DEEWARY PROPERTY MANAGER</h1>
        <p style="color: white; letter-spacing: 2px;">MANAGEMENT PORTAL</p>
    </div>
""", unsafe_allow_html=True)

# --- 5. SIDEBAR & MENU ---
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
        "💰 Done Deals History"
    ])

    # --- (Entry Forms sections 6 to 10 are exactly same as yours) ---
    # [Yahan wahi saari entry forms ayengi jo aapne pehle likhi thin]

    # --- 11. HISTORY WITH EDIT & DELETE BUTTONS ---

    # 📋 Gharon ki History
    if menu == "📋 Gharon ki History":
        res = supabase.table('house_inventory').select("*").order('id', desc=True).execute()
        if res.data:
            df = pd.DataFrame(res.data)
            for _, row in df.iterrows():
                sc = "🟢" if row['status'] == "Available" else "🔴"
                with st.expander(f"{sc} ID: {row['id']} | {row['owner_name']} - {row['location']}"):
                    st.write(f"**Rent:** {row['rent']} | **Beds:** {row['beds']} | **Admin:** {row['added_by']}")
                    
                    col1, col2 = st.columns([1, 5])
                    with col1:
                        if st.button(f"🗑️ Delete", key=f"del_h_{row['id']}"): 
                            delete_record('house_inventory', row['id'])
                    
                    # Edit Section inside Expander
                    with st.form(key=f"edit_form_h_{row['id']}"):
                        st.markdown("### ✏️ Edit Details")
                        new_rent = st.number_input("New Rent", value=int(row['rent']))
                        new_status = st.selectbox("Status", ["Available", "Rent Out"], index=0 if row['status']=="Available" else 1)
                        new_contact = st.text_input("Contact", value=row['contact'])
                        if st.form_submit_button("Update Record"):
                            update_record('house_inventory', row['id'], {"rent": new_rent, "status": new_status, "contact": new_contact})

    # 👥 New Clients History
    elif menu == "👥 New Clients History":
        res = supabase.table('client_leads').select("*").order('id', desc=True).execute()
        if res.data:
            df = pd.DataFrame(res.data)
            for _, row in df.iterrows():
                with st.expander(f"ID: {row['id']} | {row['client_name']} ({row['status']})"):
                    st.write(f"**Budget:** {row['budget']} | **Admin:** {row['added_by']}")
                    
                    col1, col2 = st.columns([1, 5])
                    with col1:
                        if st.button(f"🗑️ Delete", key=f"del_c_{row['id']}"): 
                            delete_record('client_leads', row['id'])
                    
                    with st.form(key=f"edit_form_c_{row['id']}"):
                        new_budget = st.number_input("New Budget", value=int(row['budget']))
                        new_c_status = st.selectbox("Status", ["Still Searching", "Got House"], index=0 if row['status']=="Still Searching" else 1)
                        if st.form_submit_button("Update Client"):
                            update_record('client_leads', row['id'], {"budget": new_budget, "status": new_c_status})

    # 🗣️ Discussion History
    elif menu == "🗣️ Discussion History":
        res = supabase.table('client_discussions').select("*").order('id', desc=True).execute()
        if res.data:
            df = pd.DataFrame(res.data)
            for _, row in df.iterrows():
                with st.expander(f"ID: {row['id']} | {row['client_name']}"):
                    st.write(f"**Notes:** {row['notes']} | **Agent:** {row['agent']}")
                    
                    col1, col2 = st.columns([1, 5])
                    with col1:
                        if st.button(f"🗑️ Delete", key=f"del_d_{row['id']}"): 
                            delete_record('client_discussions', row['id'])
                    
                    with st.form(key=f"edit_form_d_{row['id']}"):
                        new_notes = st.text_area("Update Notes", value=row['notes'])
                        if st.form_submit_button("Update Notes"):
                            update_record('client_discussions', row['id'], {"notes": new_notes})

    # 🏠 Dashboard
    elif menu == "🏠 Dashboard":
        st.subheader(f"Welcome, {user_name}")
        st.write("Kaam shuru karne ke liye side menu se option select karen.")

    # [Baqi Pending aur Done deals mein bhi isi tarah form add kiya ja sakta hai]

else:
    if pwd != "": st.error("Code Ghalat Hai!")

st.divider()
st.caption(f"© {datetime.now().year} Deewary.com | System Active")
