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
        <h1 style="color: #FF4B4B; margin: 0; font-family: 'Arial Black';">DEEWARY.COM RENTER PROPERTY MANAGEMENT</h1>
        <p style="color: white; letter-spacing: 2px;">MANAGER PORTAL - WELCOME UMER</p>
    </div>
""", unsafe_allow_html=True)

# --- 5. SIDEBAR & MENU ---
st.sidebar.title("🔐 Staff Access")
# Manager set to Umer as per instruction
user_name = st.sidebar.selectbox("Apna Naam Select Karen", ["Umer (Manager)", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "admin786":
    st.sidebar.markdown("---")
    
    if "menu" not in st.session_state:
        st.session_state.menu = "🏠 Dashboard"

    def set_menu(name):
        st.session_state.menu = name

    # Sidebar Buttons Style
    if st.sidebar.button("🏠 Dashboard", use_container_width=True): set_menu("🏠 Dashboard")
    
    st.sidebar.markdown("### **--- NAYI ENTRY ---**")
    if st.sidebar.button("🏠 Ghar ki Entry", use_container_width=True): set_menu("🏠 Ghar ki Entry (Owners)")
    if st.sidebar.button("👤 Client ki Entry", use_container_width=True): set_menu("👤 Client ki Entry (New)")
    if st.sidebar.button("💬 Client Discussion", use_container_width=True): set_menu("💬 Client in Discussion")
    if st.sidebar.button("⏳ Deal Pending", use_container_width=True): set_menu("⏳ Deal Pending Entry")
    if st.sidebar.button("✅ Deal Done", use_container_width=True): set_menu("✅ Deal Done Entry")

    st.sidebar.markdown("### **--- HISTORY ---**")
    if st.sidebar.button("📋 Gharon ki History", use_container_width=True): set_menu("📋 Gharon ki History")
    if st.sidebar.button("👥 New Clients History", use_container_width=True): set_menu("👥 New Clients History")
    if st.sidebar.button("🗣️ Discussion History", use_container_width=True): set_menu("🗣️ Discussion History")
    if st.sidebar.button("📂 Pending History", use_container_width=True): set_menu("📂 Pending Deals History")
    if st.sidebar.button("💰 Done History", use_container_width=True): set_menu("💰 Done Deals History")

    menu = st.session_state.menu

    # --- 6. DASHBOARD LOGIC ---
    if menu == "🏠 Dashboard":
        st.subheader(f"📊 Business Overview - Manager: {user_name}")
        
        # Fetching Stats
        h_res = supabase.table('house_inventory').select("*").execute()
        c_res = supabase.table('client_leads').select("*").execute()
        d_res = supabase.table('deals_done').select("*").execute()
        p_res = supabase.table('deals_pending').select("*").execute()

        df_h = pd.DataFrame(h_res.data) if h_res.data else pd.DataFrame()
        df_c = pd.DataFrame(c_res.data) if c_res.data else pd.DataFrame()
        df_d = pd.DataFrame(d_res.data) if d_res.data else pd.DataFrame()
        df_p = pd.DataFrame(p_res.data) if p_res.data else pd.DataFrame()

        # Top Metric Cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Renter Houses", len(df_h))
        col2.metric("Available", len(df_h[df_h['status'] == 'Available']) if not df_h.empty else 0)
        col3.metric("Deals Pending", len(df_p))
        col4.metric("Deals Done", len(df_d))

        st.markdown("---")
        st.subheader("📅 Daily Progress")
        prog1, prog2 = st.columns(2)
        
        with prog1:
            st.write("### 🏠 Recent Houses Added")
            if not df_h.empty:
                st.dataframe(df_h[['owner_name', 'location', 'rent', 'status']].head(10), use_container_width=True)
            else:
                st.info("No houses listed yet.")

        with prog2:
            st.write("### 👤 New Clients Today")
            if not df_c.empty:
                st.dataframe(df_c[['client_name', 'budget', 'req_location', 'status']].head(10), use_container_width=True)
            else:
                st.info("No new clients recorded today.")

    # --- 7. ENTRY FORMS ---
    elif menu == "🏠 Ghar ki Entry (Owners)":
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
            dp_a = st.text_input("Property Address")
            dr = st.number_input("Final Rent", min_value=0)
            dcom = st.number_input("Commission", min_value=0)
            if st.form_submit_button("Save Done Deal"):
                supabase.table('deals_done').insert({"client_name": dc_n, "owner_name": do_n, "property_address": dp_a, "final_rent": dr, "commission": dcom, "agent_name": user_name}).execute()
                st.success("Deal Done save!")

    # --- 8. HISTORY LOGIC (FIXED Syntax from image_a2b4c6.png) ---
    def show_history(table_name):
        res = supabase.table(table_name).select("*").order('id', desc=True).execute()
        if res.data:
            df = pd.DataFrame(res.data)
            st.dataframe(df, use_container_width=True)
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                del_id = st.number_input(f"Delete ID from {table_name}", min_value=0, step=1, key=f"del_{table_name}")
                if st.button(f"🗑️ Confirm Delete ID {del_id}", key=f"btn_del_{table_name}"):
                    delete_record(table_name, del_id)
            with col2:
                edit_id = st.number_input(f"Edit ID from {table_name}", min_value=0, step=1, key=f"edit_{table_name}")
                if edit_id > 0:
                    rec = next((item for item in res.data if item["id"] == edit_id), None)
                    if rec:
                        with st.expander(f"Editing ID: {edit_id}"):
                            with st.form(f"form_edit_{table_name}_{edit_id}"):
                                updated_data = {}
                                for k, v in rec.items():
                                    if k not in ['id', 'created_at', 'added_by', 'agent', 'agent_name']:
                                        if isinstance(v, int):
                                            updated_data[k] = st.number_input(f"{k}", value=v)
                                        else:
                                            updated_data[k] = st.text_input(f"{k}", value=str(v))
                                if st.form_submit_button("Update"):
                                    update_record(table_name, edit_id, updated_data)
        else:
            st.info("No records found.")

    if menu == "📋 Gharon ki History":
        show_history('house_inventory')
    elif menu == "👥 New Clients History":
        show_history('client_leads')
    elif menu == "🗣️ Discussion History":
        show_history('client_discussions')
    elif menu == "📂 Pending Deals History":
        show_history('deals_pending')
    elif menu == "💰 Done Deals History":
        show_history('deals_done')

else:
    if pwd != "": 
        st.error("Code Ghalat Hai!")

st.divider()
st.caption(f"© {datetime.now().year} Deewary.com | System Active | Manager: Umer")
