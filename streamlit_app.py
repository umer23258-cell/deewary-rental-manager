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
st.set_page_config(page_title="Deewary Property Manager", layout="wide", page_icon="🏢")

# Custom CSS for Professional Look
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* Sidebar Section Headers */
    .sidebar-header {
        color: #FF4B4B;
        font-weight: bold;
        font-size: 18px;
        margin-top: 20px;
        border-bottom: 1px solid #444;
    }
    
    /* Button Styling */
    .stButton>button {
        width: 100%;
        background-color: #2c3e50;
        color: white;
        border-radius: 5px;
    }
    .stButton>button:hover {
        border-color: #FF4B4B;
        color: #FF4B4B;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. PDF FUNCTION ---
def generate_pdf(df, title):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, txt=title, ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Helvetica", 'B', 10)
    pdf.set_fill_color(200, 200, 200)
    
    col_width = [15, 40, 60, 25, 25, 30, 30, 52]
    headers = ["ID", "Owner/Client", "Location", "Type", "Beds", "Rent/Budget", "Size", "Status/Job"]
    
    for i in range(len(headers)):
        pdf.cell(col_width[i], 10, headers[i], 1, 0, 'C', 1)
    pdf.ln()
    
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
    <div style="text-align: center; background-color: #2c3e50; padding: 20px; border-radius: 15px;">
        <h1 style="color: white; margin: 0;">DEEWARY PROPERTY MANAGER</h1>
        <p style="color: #FF4B4B; font-weight: bold;">OFFICIAL DATABASE SYSTEM</p>
    </div>
""", unsafe_allow_html=True)

# --- 5. SIDEBAR LOGIN & SECTIONS ---
st.sidebar.title("🔐 Access Control")
user_name = st.sidebar.selectbox("Personnel", ["Anas", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "admin786":
    
    # --- ALAG ALAG BUTTON SECTIONS ---
    st.sidebar.markdown('<p class="sidebar-header">📥 DATA ENTRY</p>', unsafe_allow_html=True)
    if st.sidebar.button("🏠 Register Property"):
        st.session_state.menu = "property_entry"
    if st.sidebar.button("👤 Register Client"):
        st.session_state.menu = "client_entry"
        
    st.sidebar.markdown('<p class="sidebar-header">📊 RECORDS & REPORTS</p>', unsafe_allow_html=True)
    if st.sidebar.button("📋 View Full History"):
        st.session_state.menu = "history"
    if st.sidebar.button("🛠️ Edit/Delete Records"):
        st.session_state.menu = "manage"
    if st.sidebar.button("🔍 Search & Print PDF"):
        st.session_state.menu = "search"

    # Default view
    if "menu" not in st.session_state:
        st.session_state.menu = "history"

    # --- 6. PROPERTY ENTRY ---
    if st.session_state.menu == "property_entry":
        st.subheader("🏡 New Property Registration")
        with st.form("h_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                o_name = st.text_input("Owner Name")
                o_contact = st.text_input("Contact")
                loc = st.text_input("Address")
                portion = st.selectbox("Type", ["Full House", "Ground Floor", "First Floor", "Basement", "Shop", "Office"])
            with c2:
                beds = st.selectbox("Beds", ["1", "2", "3", "4", "5", "6+", "N/A"])
                rent = st.number_input("Demand (PKR)", min_value=0)
                size = st.text_input("Size (Marla/Kanal)")
                status = st.selectbox("Status", ["Available", "Rent Out"])
            
            if st.form_submit_button("Save Property"):
                supabase.table('house_inventory').insert({
                    "owner_name": o_name, "contact": o_contact, "location": loc, 
                    "portion": portion, "beds": beds, "rent": rent, "size": size, 
                    "status": status, "added_by": user_name
                }).execute()
                st.success("Property Saved!")

    # --- 7. CLIENT ENTRY ---
    elif st.session_state.menu == "client_entry":
        st.subheader("👨‍👩‍👧‍👦 New Client Requirement")
        with st.form("c_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                c_name = st.text_input("Client Name")
                c_contact = st.text_input("Contact")
                c_loc = st.text_input("Required Area")
            with c2:
                c_budget = st.number_input("Budget (PKR)", min_value=0)
                c_portion = st.selectbox("Type Required", ["Full House", "Portion", "Flat", "Shop", "Office"])
                c_marla = st.text_input("Marla Required")
            
            if st.form_submit_button("Save Client Lead"):
                supabase.table('client_leads').insert({
                    "client_name": c_name, "contact": c_contact, "req_location": c_loc, 
                    "budget": c_budget, "req_portion": c_portion, "marla": c_marla, "added_by": user_name
                }).execute()
                st.success("Client Saved!")

    # --- 8. HISTORY ---
    elif st.session_state.menu == "history":
        st.subheader("📋 System Database")
        t1, t2 = st.tabs(["🏠 Properties", "👥 Clients"])
        with t1:
            res = supabase.table('house_inventory').select("*").execute()
            st.dataframe(pd.DataFrame(res.data), use_container_width=True)
        with t2:
            res = supabase.table('client_leads').select("*").execute()
            st.dataframe(pd.DataFrame(res.data), use_container_width=True)

    # --- 9. MANAGE ---
    elif st.session_state.menu == "manage":
        st.subheader("🛠️ Edit or Delete Records")
        tbl = st.radio("Select Table", ["house_inventory", "client_leads"], horizontal=True)
        sid = st.number_input("Enter ID", min_value=1, step=1)
        if st.button("Find Record"):
            res = supabase.table(tbl).select("*").eq("id", sid).execute()
            if res.data: st.session_state.found = res.data[0]
            else: st.error("Not Found")
        
        if "found" in st.session_state:
            st.write(st.session_state.found)
            if st.button("🗑️ Delete Permanently"):
                supabase.table(tbl).delete().eq("id", sid).execute()
                st.warning("Deleted!")
                del st.session_state.found

    # --- 10. SEARCH & PDF ---
    elif st.session_state.menu == "search":
        st.subheader("🔍 Search & Download Report")
        mode = st.radio("Report For", ["Houses", "Clients"])
        q = st.text_input("Search Anything...")
        tbl_name = 'house_inventory' if mode == "Houses" else 'client_leads'
        res = supabase.table(tbl_name).select("*").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            if q:
                df = df[df.astype(str).apply(lambda x: x.str.contains(q, case=False)).any(axis=1)]
            st.dataframe(df, use_container_width=True)
            if st.button("Download Professional PDF"):
                pdf_bytes = generate_pdf(df, f"DEEWARY {mode.upper()} REPORT")
                st.download_button("📥 Click to Download", pdf_bytes, "Report.pdf", "application/pdf")

else:
    if pwd != "":
        st.error("Access Denied")

st.divider()
st.caption(f"© {datetime.now().year} Deewary.com | Data Protection Active")
