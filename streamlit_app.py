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

# --- 3. HELPER FUNCTIONS ---
def delete_record(table_name, record_id):
    supabase.table(table_name).delete().eq("id", record_id).execute()
    st.warning(f"Record ID {record_id} delete kar diya gaya hai.")
    st.rerun()

# --- 4. SIDEBAR & MENU ---
st.sidebar.title("🔐 Staff Access")
user_name = st.sidebar.selectbox("Apna Naam Select Karen", ["Anas", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "admin786":
    menu = st.sidebar.radio("KAAM SELECT KAREN", [
        "🏠 Dashboard",
        "--- NAYI ENTRY ---",
        "🏠 Ghar ki Entry (Owners)", 
        "👤 Client ki Entry (New)",
        "--- RECORDS & HISTORY ---",
        "📋 Gharon ki History",
        "👥 New Clients History"
    ])

    # --- 5. GHAR KI HISTORY (With Edit Logic) ---
    if menu == "📋 Gharon ki History":
        st.subheader("📋 House Inventory")
        res = supabase.table('house_inventory').select("*").order('id', desc=True).execute()
        
        if res.data:
            for row in res.data:
                sc = "🟢" if row['status'] == "Available" else "🔴"
                with st.expander(f"{sc} ID: {row['id']} | {row['owner_name']} - {row['location']}"):
                    # Buttons for Edit and Delete
                    col1, col2 = st.columns(2)
                    
                    if col1.button(f"📝 Edit ID {row['id']}", key=f"edit_btn_{row['id']}"):
                        st.session_state[f"editing_{row['id']}"] = True
                    
                    if col2.button(f"🗑️ Delete ID {row['id']}", key=f"del_h_{row['id']}"):
                        delete_record('house_inventory', row['id'])

                    # If Edit is clicked, show the form
                    if st.session_state.get(f"editing_{row['id']}", False):
                        st.markdown("---")
                        st.info(f"Editing Record ID: {row['id']}")
                        with st.form(f"edit_form_{row['id']}"):
                            new_rent = st.number_input("New Rent", value=int(row['rent']))
                            new_status = st.selectbox("Update Status", ["Available", "Rent Out"], index=0 if row['status'] == "Available" else 1)
                            new_details = st.text_area("Update Details", value=row['details'])
                            
                            if st.form_submit_button("Save Changes"):
                                supabase.table('house_inventory').update({
                                    "rent": new_rent, 
                                    "status": new_status, 
                                    "details": new_details
                                }).eq("id", row['id']).execute()
                                st.success("Record Update Ho Gaya!")
                                st.session_state[f"editing_{row['id']}"] = False
                                st.rerun()
        else:
            st.info("Koi record nahi mila.")

    # --- 6. NEW CLIENTS HISTORY (With Edit Logic) ---
    elif menu == "👥 New Clients History":
        st.subheader("👥 Client Requirements")
        res = supabase.table('client_leads').select("*").order('id', desc=True).execute()
        
        if res.data:
            for row in res.data:
                with st.expander(f"ID: {row['id']} | {row['client_name']} ({row['status']})"):
                    c1, c2 = st.columns(2)
                    
                    if c1.button(f"📝 Edit ID {row['id']}", key=f"edit_c_{row['id']}"):
                        st.session_state[f"edit_c_mode_{row['id']}"] = True
                        
                    if c2.button(f"🗑️ Delete ID {row['id']}", key=f"del_c_{row['id']}"):
                        delete_record('client_leads', row['id'])

                    if st.session_state.get(f"edit_c_mode_{row['id']}", False):
                        with st.form(f"form_c_{row['id']}"):
                            up_status = st.selectbox("Ghar Mila?", ["Still Searching", "Got House"], index=0 if row['status'] == "Still Searching" else 1)
                            if st.form_submit_button("Update Client Status"):
                                supabase.table('client_leads').update({"status": up_status}).eq("id", row['id']).execute()
                                st.success("Client Status Updated!")
                                st.session_state[f"edit_c_mode_{row['id']}"] = False
                                st.rerun()

    # (Baqi forms wese hi rahenge jese pehle thay)
    elif menu == "🏠 Ghar ki Entry (Owners)":
        st.subheader("🏡 Naye Ghar ki Entry")
        # ... (Purana Entry Form)

else:
    if pwd != "": st.error("Code Ghalat Hai!")

st.caption(f"© {datetime.now().year} Deewary.com")
