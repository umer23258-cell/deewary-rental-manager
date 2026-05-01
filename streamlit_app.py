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
st.set_page_config(page_title="Deewary CRM", layout="wide", page_icon="🏢")

# --- 3. PROFESSIONAL CSS ---
st.markdown("""
    <style>
    /* Main Background and Font */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Header Styling */
    .main-header {
        text-align: center; 
        background: linear-gradient(135deg, #1e1e1e 0%, #3a3a3a 100%);
        padding: 25px; 
        border-radius: 10px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 30px;
    }
    
    /* Input Box Focus */
    .stTextInput>div>div>input:focus {
        border-color: #FF4B4B;
    }
    
    /* Professional Table */
    .stDataFrame {
        border: 1px solid #e6e9ef;
        border-radius: 10px;
    }
    
    /* Clean Divider */
    hr {
        margin-top: 2rem;
        margin-bottom: 2rem;
        border-top: 1px solid #ddd;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. PDF ENGINE ---
def generate_pdf(df, title):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 15, txt=title, ln=True, align='C')
    
    pdf.set_font("Helvetica", 'B', 10)
    pdf.set_fill_color(240, 240, 240)
    
    col_width = [15, 45, 55, 25, 20, 30, 25, 62]
    headers = ["ID", "Name/Contact", "Location", "Type", "Beds", "Price", "Size", "Notes/Status"]
    
    for i in range(len(headers)):
        pdf.cell(col_width[i], 10, headers[i], 1, 0, 'C', 1)
    pdf.ln()
    
    pdf.set_font("Helvetica", size=9)
    for index, row in df.iterrows():
        vals = [
            str(row.get('id', '')),
            str(row.get('owner_name', row.get('client_name', '')))[:20],
            str(row.get('location', row.get('req_location', '')))[:25],
            str(row.get('portion', row.get('req_portion', ''))),
            str(row.get('beds', row.get('beds_required', ''))),
            str(row.get('rent', row.get('budget', ''))),
            str(row.get('size', row.get('marla', ''))),
            str(row.get('status', row.get('job', '')))[:30]
        ]
        for i in range(len(vals)):
            clean_text = vals[i].encode('latin-1', 'ignore').decode('latin-1')
            pdf.cell(col_width[i], 10, clean_text, 1)
        pdf.ln()
    return pdf.output(dest='S')

# --- 5. HEADER ---
st.markdown("""
    <div class="main-header">
        <h1 style="color: #FF4B4B; margin: 0; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; letter-spacing: 1px;">DEEWARY PROPERTY MANAGER</h1>
        <p style="color: #ffffff; opacity: 0.8; margin-top: 5px; font-weight: 300;">Enterprise Inventory & Database System</p>
    </div>
""", unsafe_allow_html=True)

# --- 6. SIDEBAR NAVIGATION ---
st.sidebar.header("🔐 Staff Authentication")
user_name = st.sidebar.selectbox("Select User", ["Anas", "Sawer Khan", "Tariq Hussain"])
access_code = st.sidebar.text_input("Access Code", type="password")

if access_code == "admin786":
    st.sidebar.divider()
    
    # Using a clean radio selector for better UX
    category = st.sidebar.radio("MAIN MENU", ["📥 Data Entry", "📋 View Records", "🛠️ Management", "🔍 Search & Export"])

    # --- 7. DATA ENTRY ---
    if category == "📥 Data Entry":
        sub_menu = st.radio("Entry Type", ["Property (Owner)", "Requirement (Client)"], horizontal=True)
        
        if sub_menu == "Property (Owner)":
            st.subheader("Add New Property Listing")
            with st.form("property_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    o_name = st.text_input("Owner Full Name")
                    o_contact = st.text_input("Contact Number")
                    loc = st.text_input("Property Address/Location")
                with c2:
                    portion = st.selectbox("Property Type", ["Full House", "Ground Floor", "First Floor", "Basement", "Shop", "Office"])
                    rent = st.number_input("Demand Rent/Price (PKR)", min_value=0)
                    size = st.text_input("Size (e.g. 5 Marla)")
                
                beds = st.select_slider("Bedrooms", options=["N/A", "1", "2", "3", "4", "5", "6+"])
                status = st.selectbox("Current Status", ["Available", "Rented Out", "Sold"])
                details = st.text_area("Additional Remarks")
                
                if st.form_submit_button("Save Property"):
                    supabase.table('house_inventory').insert({
                        "owner_name": o_name, "contact": o_contact, "location": loc, 
                        "portion": portion, "beds": beds, "rent": rent, 
                        "size": size, "status": status, "details": details, "added_by": user_name
                    }).execute()
                    st.success("Property record secured.")

        else:
            st.subheader("Add New Client Requirement")
            with st.form("client_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    c_name = st.text_input("Client Name")
                    c_contact = st.text_input("Phone Number")
                    c_loc = st.text_input("Preferred Location")
                with c2:
                    c_budget = st.number_input("Monthly Budget (PKR)", min_value=0)
                    c_type = st.selectbox("Requirement Type", ["Full House", "Portion", "Flat", "Shop", "Office"])
                    c_size = st.text_input("Size Required")
                
                c_job = st.text_input("Client Profession")
                c_req = st.text_area("Specific Requests")
                
                if st.form_submit_button("Save Client Lead"):
                    supabase.table('client_leads').insert({
                        "client_name": c_name, "contact": c_contact, "req_location": c_loc, 
                        "budget": c_budget, "req_portion": c_type, "job": c_job, 
                        "marla": c_size, "requirements": c_req, "added_by": user_name
                    }).execute()
                    st.success("Client lead registered.")

    # --- 8. VIEW RECORDS ---
    elif category == "📋 View Records":
        st.subheader("Database Overview")
        view_tab1, view_tab2 = st.tabs(["🏠 Property Inventory", "👥 Client Leads"])
        
        with view_tab1:
            data_h = supabase.table('house_inventory').select("*").execute()
            if data_h.data:
                st.dataframe(pd.DataFrame(data_h.data), use_container_width=True)
            else: st.info("No property data found.")
            
        with view_tab2:
            data_c = supabase.table('client_leads').select("*").execute()
            if data_c.data:
                st.dataframe(pd.DataFrame(data_c.data), use_container_width=True)
            else: st.info("No client leads found.")

    # --- 9. MANAGEMENT ---
    elif category == "🛠️ Management":
        st.subheader("Edit or Remove Records")
        col1, col2 = st.columns([1, 2])
        with col1:
            m_table = st.selectbox("Select Table", ["house_inventory", "client_leads"])
            m_id = st.number_input("Record ID", min_value=1, step=1)
            if st.button("Fetch Data"):
                res = supabase.table(m_table).select("*").eq("id", m_id).execute()
                if res.data: st.session_state.edit_item = res.data[0]
                else: st.error("ID not found.")
        
        if "edit_item" in st.session_state:
            with col2:
                st.markdown(f"**Managing ID: {m_id}**")
                if m_table == "house_inventory":
                    new_status = st.selectbox("Update Status", ["Available", "Rented Out", "Sold"])
                    if st.button("Update Status"):
                        supabase.table(m_table).update({"status": new_status}).eq("id", m_id).execute()
                        st.success("Updated successfully.")
                
                st.divider()
                if st.button("Delete Permanently", type="secondary"):
                    supabase.table(m_table).delete().eq("id", m_id).execute()
                    st.warning("Record deleted.")
                    del st.session_state.edit_item

    # --- 10. SEARCH & EXPORT ---
    elif category == "🔍 Search & Export":
        st.subheader("Search Engine")
        s_type = st.radio("Search In:", ["Properties", "Clients"], horizontal=True)
        query = st.text_input("Type to filter (Location, Name, etc.)")
        
        target = 'house_inventory' if s_type == "Properties" else 'client_leads'
        res = supabase.table(target).select("*").execute()
        
        if res.data:
            df = pd.DataFrame(res.data)
            if query:
                df = df[df.astype(str).apply(lambda x: x.str.contains(query, case=False)).any(axis=1)]
            
            st.dataframe(df, use_container_width=True)
            
            if not df.empty:
                if st.button("Generate PDF Report"):
                    pdf_data = generate_pdf(df, f"DEEWARY {s_type.upper()} REPORT")
                    st.download_button("Download PDF", pdf_data, f"Report_{datetime.now().date()}.pdf", "application/pdf")

elif access_code != "":
    st.sidebar.error("Incorrect Access Code")

st.markdown("---")
st.caption(f"© {datetime.now().year} Deewary.com | Authorized Access Only")
