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

    # --- 6. GHAR KI ENTRY FORM ---
    if menu == "🏠 Ghar ki Entry (Owners)":
        st.subheader("🏡 Naye Ghar ya Shop ki Detail")
        with st.form("house_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                o_name = st.text_input("Owner ka Naam")
                o_contact = st.text_input("Owner Contact")
                loc = st.text_input("Location / Address")
                portion = st.selectbox("Portion", ["Full House", "Ground Floor", "First Floor", "Basement", "Shop", "Office"])
                size = st.text_input("Size (Marla/Kanal)")
            with c2:
                beds = st.selectbox("Bedrooms", ["1", "2", "3", "4", "5", "6+", "N/A"])
                rent = st.number_input("Demand Rent", min_value=0)
                v_time = st.text_input("Visit Time")
                h_status = st.selectbox("Ghar ka Status", ["Available", "Rent Out"])
                gas = st.selectbox("Gas", ["Yes", "No", "Single Meter", "Combine Meter"])
                water = st.selectbox("Water", ["Water Supply", "Boor", "Yes", "No"])
                elec = st.selectbox("Electricity", ["Separate Meter", "Combine Meter", "Yes", "No"])
            if st.form_submit_button("Save House Record"):
                supabase.table('house_inventory').insert({
                    "owner_name": o_name, "contact": o_contact, "location": loc, "portion": portion, 
                    "beds": beds, "rent": rent, "size": size, "gas": gas, "water": water, 
                    "electricity": elec, "visit_time": v_time, "status": h_status, "added_by": user_name
                }).execute()
                st.success("Ghar save ho gaya!")

    # --- 7-10: (Other Entry Forms Remain Same as your original code) ---
    # ... (Keep your Client, Discussion, Pending, Done forms here) ...

    # --- 11. IMPROVED HISTORY WITH EDIT & DELETE ---
    
    # 📋 House History
    elif menu == "📋 Gharon ki History":
        st.subheader("📋 Gharon ki History")
        res = supabase.table('house_inventory').select("*").order('id', desc=True).execute()
        if res.data:
            df = pd.DataFrame(res.data)
            for _, row in df.iterrows():
                sc = "🟢" if row['status'] == "Available" else "🔴"
                with st.expander(f"{sc} ID: {row['id']} | {row['owner_name']} - {row['location']}"):
                    # Edit Form inside Expander
                    with st.form(f"edit_house_{row['id']}"):
                        e1, e2 = st.columns(2)
                        with e1:
                            new_o_name = st.text_input("Owner Name", value=row['owner_name'])
                            new_rent = st.number_input("Rent", value=int(row['rent']))
                            new_stat = st.selectbox("Status", ["Available", "Rent Out"], index=0 if row['status']=="Available" else 1)
                        with e2:
                            new_contact = st.text_input("Contact", value=row['contact'])
                            new_loc = st.text_input("Location", value=row['location'])
                        
                        btn_c1, btn_c2 = st.columns(2)
                        if btn_c1.form_submit_button("🔄 Update Data"):
                            update_record('house_inventory', row['id'], {
                                "owner_name": new_o_name, "rent": new_rent, 
                                "status": new_stat, "contact": new_contact, "location": new_loc
                            })
                    
                    if st.button(f"🗑️ Delete ID {row['id']}", key=f"del_h_{row['id']}"):
                        delete_record('house_inventory', row['id'])

    # 👥 New Clients History
    elif menu == "👥 New Clients History":
        res = supabase.table('client_leads').select("*").order('id', desc=True).execute()
        if res.data:
            df = pd.DataFrame(res.data)
            for _, row in df.iterrows():
                with st.expander(f"ID: {row['id']} | {row['client_name']} ({row['status']})"):
                    with st.form(f"edit_client_{row['id']}"):
                        new_cn = st.text_input("Client Name", value=row['client_name'])
                        new_bud = st.number_input("Budget", value=int(row['budget']))
                        new_s = st.selectbox("Status", ["Still Searching", "Got House"], index=0 if row['status']=="Still Searching" else 1)
                        if st.form_submit_button("🔄 Update Client"):
                            update_record('client_leads', row['id'], {"client_name": new_cn, "budget": new_bud, "status": new_s})
                    
                    if st.button(f"🗑️ Delete ID {row['id']}", key=f"del_c_{row['id']}"):
                        delete_record('client_leads', row['id'])

    # 🗣️ Discussion History
    elif menu == "🗣️ Discussion History":
        res = supabase.table('client_discussions').select("*").order('id', desc=True).execute()
        if res.data:
            df = pd.DataFrame(res.data)
            for _, row in df.iterrows():
                with st.expander(f"ID: {row['id']} | {row['client_name']}"):
                    with st.form(f"edit_disc_{row['id']}"):
                        new_notes = st.text_area("Update Notes", value=row['notes'])
                        if st.form_submit_button("Update Notes"):
                            update_record('client_discussions', row['id'], {"notes": new_notes})
                    
                    if st.button(f"🗑️ Delete ID {row['id']}", key=f"del_d_{row['id']}"):
                        delete_record('client_discussions', row['id'])

    # Note: Isi tarah baqi sections (Pending/Done) mein bhi hum update ka logic add kar sakte hain.

    elif menu == "🏠 Dashboard":
        st.subheader(f"Welcome, {user_name}")
        st.write("Kaam shuru karne ke liye side menu se option select karen.")

else:
    if pwd != "": st.error("Code Ghalat Hai!")

st.divider()
st.caption(f"© {datetime.now().year} Deewary.com | System Active")
