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

def update_record(table_name, record_id, data_dict):
    supabase.table(table_name).update(data_dict).eq("id", record_id).execute()
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

    # [Note: Sections 6 to 10 (Entry Forms) will remain exactly as your original code]
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

    elif menu == "👤 Client ki Entry (New)":
        st.subheader("👨‍👩‍👧‍👦 Client Requirement")
        with st.form("client_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                cn = st.text_input("Client Name")
                cc = st.text_input("Contact")
                cb = st.selectbox("Beds Required", ["1", "2", "3", "4", "5+", "Any"])
            with c2:
                cbud = st.number_input("Budget", min_value=0)
                cloc = st.text_input("Location Required")
                c_stat = st.selectbox("Ghar Mila?", ["Still Searching", "Got House"])
            if st.form_submit_button("Save Client"):
                supabase.table('client_leads').insert({"client_name": cn, "contact": cc, "req_location": cloc, "budget": cbud, "beds_required": cb, "status": c_stat, "added_by": user_name}).execute()
                st.success("Client requirement save ho gayi!")

    elif menu == "💬 Client in Discussion":
        st.subheader("💬 Conversations")
        with st.form("disc_form", clear_on_submit=True):
            dc = st.text_input("Client Name")
            dp = st.text_input("Phone Number")
            ds = st.text_area("Update/Notes")
            if st.form_submit_button("Save Discussion"):
                supabase.table('client_discussions').insert({"client_name": dc, "contact": dp, "notes": ds, "agent": user_name}).execute()
                st.success("Discussion save ho gayi!")

    elif menu == "⏳ Deal Pending Entry":
        st.subheader("⏳ Pending (Token)")
        with st.form("pend_form", clear_on_submit=True):
            pc = st.text_input("Client Name")
            pp = st.text_area("Property Details")
            pt = st.number_input("Token Amount", min_value=0)
            pd_date = st.date_input("Closing Date")
            if st.form_submit_button("Save Pending"):
                supabase.table('deals_pending').insert({"client_name": pc, "property_details": pp, "token_amount": pt, "expected_date": str(pd_date), "agent_name": user_name}).execute()
                st.success("Pending record save!")

    elif menu == "✅ Deal Done Entry":
        st.subheader("✅ Deal Done")
        with st.form("done_form", clear_on_submit=True):
            dc_n = st.text_input("Client Name")
            do_n = st.text_input("Owner Name")
            dp_a = st.text_input("Property Address (Jo Rent Out hui)")
            dr = st.number_input("Final Rent", min_value=0)
            dcom = st.number_input("Commission", min_value=0)
            if st.form_submit_button("Save Done Deal"):
                supabase.table('deals_done').insert({"client_name": dc_n, "owner_name": do_n, "property_address": dp_a, "final_rent": dr, "commission": dcom, "agent_name": user_name}).execute()
                st.success("Deal Done save!")

    # --- 11. HISTORY SECTIONS (WITH TABLES & EDIT) ---
    def show_history(table_name):
        res = supabase.table(table_name).select("*").order('id', desc=True).execute()
        if res.data:
            df = pd.DataFrame(res.data)
            st.dataframe(df, use_container_width=True)
            
            st.markdown("---")
            col_del, col_edit = st.columns(2)
            
            with col_del:
                st.write("🗑️ **Delete Record**")
                del_id = st.number_input(f"ID to delete", min_value=0, step=1, key=f"del_in_{table_name}")
                if st.button(f"Confirm Delete ID {del_id}", key=f"del_btn_{table_name}"):
                    delete_record(table_name, del_id)
            
            with col_edit:
                st.write("✏️ **Edit Record**")
                edit_id = st.number_input(f"ID to edit", min_value=0, step=1, key=f"edit_in_{table_name}")
                
                # Agar edit ID input ki gayi hai to form dikhayen
                if edit_id > 0:
                    record = next((item for item in res.data if item["id"] == edit_id), None)
                    if record:
                        with st.expander(f"Editing ID: {edit_id}"):
                            with st.form(f"edit_form_{table_name}_{edit_id}"):
                                updated_values = {}
                                # Dinamic fields based on table
                                for key in record.keys():
                                    if key not in ['id', 'created_at', 'added_by', 'agent', 'agent_name']:
                                        if isinstance(record[key], int):
                                            updated_values[key] = st.number_input(f"New {key}", value=record[key])
                                        else:
                                            updated_values[key] = st.text_input(f"New {key}", value=str(record[key]))
                                
                                if st.form_submit_button("Save Changes"):
                                    update_record(table_name, edit_id, updated_values)
                    else:
                        st.error("Ye ID nahi mili.")
        else:
            st.info("Abhi koi data majood nahi hai.")

    if menu == "📋 Gharon ki History":
        st.subheader("📋 House Inventory Record")
        show_history('house_inventory')

    elif menu == "👥 New Clients History":
        st.subheader("👥 Client Leads Record")
        show_history('client_leads')

    elif menu == "🗣️ Discussion History":
        st.subheader("🗣️ Conversations History")
        show_history('client_discussions')

    elif menu == "📂 Pending Deals History":
        st.subheader("📂 Token/Pending Deals")
        show_history('deals_pending')

    elif menu == "💰 Done Deals History":
        st.subheader("💰 Closed Deals Record")
        show_history('deals_done')

    elif menu == "🏠 Dashboard":
        st.subheader(f"Welcome, {user_name}")
        st.write("Kaam shuru karne ke liye side menu se option select karen.")

else:
    if pwd != "": st.error("Code Ghalat Hai!")

st.divider()
st.caption(f"© {datetime.now().year} Deewary.com | System Active")
