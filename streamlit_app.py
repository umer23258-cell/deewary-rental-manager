import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
from fpdf import FPDF
import io

# --- 1. SUPABASE SETUP ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Deewary | Property Management System", layout="wide", page_icon="🏢")

# Modern CSS Styling
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    header {visibility: hidden;}
    .main-header {
        text-align: center; 
        background-color: #1E1E1E; 
        padding: 30px; 
        border-radius: 15px; 
        border-bottom: 4px solid #FF4B4B;
        margin-bottom: 25px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. PROFESSIONAL PDF GENERATION ---
def generate_pdf(df, title):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, txt=title, ln=True, align='C')
    pdf.ln(5)
    
    # Table Header
    pdf.set_font("Helvetica", 'B', 10)
    pdf.set_fill_color(240, 240, 240)
    
    col_width = [15, 40, 60, 25, 25, 30, 30, 52]
    headers = ["ID", "Contact/Name", "Location", "Type", "Beds", "Price/Rent", "Size", "Status/Job"]
    
    for i in range(len(headers)):
        pdf.cell(col_width[i], 10, headers[i], 1, 0, 'C', 1)
    pdf.ln()
    
    # Table Body
    pdf.set_font("Helvetica", size=9)
    for index, row in df.iterrows():
        vals = [
            str(row.get('id', '')),
            str(row.get('owner_name', row.get('client_name', '')))[:18],
            str(row.get('location', row.get('req_location', '')))[:25],
            str(row.get('portion', row.get('req_portion', ''))),
            str(row.get('beds', row.get('beds_required', ''))),
            str(row.get('rent', row.get('budget', ''))),
            str(row.get('size', row.get('marla', ''))),
            str(row.get('status', row.get('job', '')))[:25]
        ]
        for i in range(len(vals)):
            clean_text = vals[i].encode('latin-1', 'ignore').decode('latin-1')
            pdf.cell(col_width[i], 10, clean_text, 1)
        pdf.ln()
        
    return pdf.output(dest='S')

# --- 4. HEADER ---
st.markdown("""
    <div class="main-header">
        <h1 style="color: #FF4B4B; margin: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">DEEWARY PROPERTY MANAGER</h1>
        <p style="color: #BBBBBB; letter-spacing: 3px; font-weight: bold;">PREMIUM INVENTORY & CLIENT DATABASE</p>
    </div>
""", unsafe_allow_html=True)

# --- 5. SIDEBAR NAVIGATION ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/609/609803.png", width=100)
st.sidebar.title("Staff Authentication")
user_name = st.sidebar.selectbox("Authorized Personnel", ["Anas", "Sawer Khan", "Tariq Hussain"])
access_code = st.sidebar.text_input("Access Code", type="password")

if access_code == "admin786":
    st.sidebar.divider()
    
    st.sidebar.subheader("📥 DATA ENTRY")
    entry_menu = st.sidebar.button("🏠 Property Entry (Owner)")
    client_menu = st.sidebar.button("👤 Client Requirement")
    
    st.sidebar.subheader("📊 MANAGEMENT & REPORTS")
    history_menu = st.sidebar.button("📋 View Database")
    manage_menu = st.sidebar.button("🛠️ Edit/Delete Records")
    search_menu = st.sidebar.button("🔍 Search & Export PDF")

    # Persistent State for Menu
    if entry_menu: st.session_state.menu = "entry"
    if client_menu: st.session_state.menu = "client"
    if history_menu: st.session_state.menu = "history"
    if manage_menu: st.session_state.menu = "manage"
    if search_menu: st.session_state.menu = "search"
    
    # Default selection
    if "menu" not in st.session_state:
        st.session_state.menu = "history"

    # --- 6. PROPERTY ENTRY ---
    if st.session_state.menu == "entry":
        st.subheader("🏡 New Property Registration (Owners)")
        with st.form("house_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                o_name = st.text_input("Owner Name")
                o_contact = st.text_input("Contact Number")
                loc = st.text_input("Location / Address")
                portion = st.selectbox("Property Type", ["Full House", "Ground Floor", "First Floor", "Basement", "Shop", "Office"])
            with col2:
                beds = st.selectbox("Bedrooms", ["1", "2", "3", "4", "5", "6+", "N/A"])
                rent = st.number_input("Asking Price/Rent (PKR)", min_value=0)
                size = st.text_input("Size (e.g., 5 Marla, 1 Kanal)")
                status = st.selectbox("Listing Status", ["Available", "Rented Out", "Sold"])
            
            other = st.text_area("Additional Details & Features")
            if st.form_submit_button("Submit Property Record"):
                payload = {
                    "owner_name": o_name, "contact": o_contact, "location": loc, 
                    "portion": portion, "beds": beds, "rent": rent, 
                    "size": size, "status": status, "details": other, "added_by": user_name
                }
                supabase.table('house_inventory').insert(payload).execute()
                st.success("Success: Property record has been added to the database.")

    # --- 7. CLIENT ENTRY ---
    elif st.session_state.menu == "client":
        st.subheader("👨‍👩‍👧‍👦 Client Requirement Leads")
        with st.form("client_form", clear_on_submit=True):
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                c_name = st.text_input("Client Name")
                c_contact = st.text_input("Phone Number")
                c_loc = st.text_input("Target Location")
                c_job = st.text_input("Profession/Business")
            with c_col2:
                c_budget = st.number_input("Budget Range (PKR)", min_value=0)
                c_portion = st.selectbox("Preferred Type", ["Full House", "Portion", "Flat", "Shop", "Office"])
                c_beds = st.selectbox("Beds Required", ["1", "2", "3", "4", "5", "6+", "Any"])
                c_marla = st.text_input("Required Size")
            
            c_req = st.text_area("Specific Requirements (e.g., Parking, Corner)")
            if st.form_submit_button("Register Client Lead"):
                payload = {
                    "client_name": c_name, "contact": c_contact, "req_location": c_loc, 
                    "budget": c_budget, "req_portion": c_portion, "job": c_job, 
                    "beds_required": c_beds, "marla": c_marla, "requirements": c_req, "added_by": user_name
                }
                supabase.table('client_leads').insert(payload).execute()
                st.success("Success: Client lead captured successfully.")

    # --- 8. DATABASE VIEW ---
    elif st.session_state.menu == "history":
        st.subheader("📋 System Database")
        tab1, tab2 = st.tabs(["🏠 Property Inventory", "👥 Client Database"])
        with tab1:
            res_h = supabase.table('house_inventory').select("*").execute()
            if res_h.data:
                st.dataframe(pd.DataFrame(res_h.data), use_container_width=True)
            else: st.info("Inventory is currently empty.")
        with tab2:
            res_c = supabase.table('client_leads').select("*").execute()
            if res_c.data:
                st.dataframe(pd.DataFrame(res_c.data), use_container_width=True)
            else: st.info("No client leads found.")

    # --- 9. MANAGE RECORDS ---
    elif st.session_state.menu == "manage":
        st.subheader("🛠️ Record Management")
        col_m1, col_m2 = st.columns([1, 2])
        with col_m1:
            target_table = st.radio("Select Category", ["house_inventory", "client_leads"])
            search_id = st.number_input("Enter Record ID", min_value=1, step=1)
            find_btn = st.button("Fetch Record")

        if find_btn:
            res = supabase.table(target_table).select("*").eq("id", search_id).execute()
            if res.data:
                st.session_state.found_record = res.data[0]
                st.session_state.target_table = target_table
                st.session_state.active_id = search_id
            else:
                st.error("Record ID not found.")

        if "found_record" in st.session_state:
            with st.expander("Update / Delete Selected Record", expanded=True):
                st.json(st.session_state.found_record)
                if st.session_state.target_table == "house_inventory":
                    new_st = st.selectbox("Change Status", ["Available", "Rented Out", "Sold"])
                    if st.button("Update Listing Status"):
                        supabase.table(st.session_state.target_table).update({"status": new_st}).eq("id", st.session_state.active_id).execute()
                        st.success("Record Updated.")
                
                st.divider()
                if st.button("🚨 Permanently Delete Record"):
                    supabase.table(st.session_state.target_table).delete().eq("id", st.session_state.active_id).execute()
                    st.warning("Record deleted.")
                    del st.session_state.found_record

    # --- 10. SEARCH & EXPORT ---
    elif st.session_state.menu == "search":
        st.subheader("🔍 Search Engine & Export Center")
        report_type = st.radio("Select Data Type", ["Properties", "Clients"], horizontal=True)
        search_q = st.text_input("Search keywords (Location, Name, etc.)")
        
        table_name = 'house_inventory' if report_type == "Properties" else 'client_leads'
        res = supabase.table(table_name).select("*").execute()
        
        if res.data:
            df_all = pd.DataFrame(res.data)
            if search_q:
                df_all = df_all[df_all.astype(str).apply(lambda x: x.str.contains(search_q, case=False)).any(axis=1)]
            
            st.dataframe(df_all, use_container_width=True)
            
            if not df_all.empty:
                pdf_bytes = generate_pdf(df_all, f"DEEWARY {report_type.upper()} REPORT")
                st.download_button(
                    label="📥 Download Professional PDF",
                    data=pdf_bytes,
                    file_name=f"Deewary_{report_type}_{datetime.now().strftime('%d-%m-%y')}.pdf",
                    mime="application/pdf"
                )
        else:
            st.warning("No data found in the selected category.")

else:
    if access_code != "":
        st.error("Invalid Access Code. Please contact administration.")

# --- FOOTER ---
st.divider()
st.markdown(f"""
    <div style="text-align: center; color: #888;">
        © {datetime.now().year} Deewary.com | Enterprise Property Management System | Connected to Supabase Cloud
    </div>
""", unsafe_allow_html=True)
