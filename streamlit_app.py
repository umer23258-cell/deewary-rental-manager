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

# Hide Streamlit UI
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# --- 3. PROFESSIONAL TABLE PDF FUNCTION ---
def generate_pdf(df, title):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, txt=title, ln=True, align='C')
    pdf.ln(5)
    
    # Table Header
    pdf.set_font("Helvetica", 'B', 10)
    pdf.set_fill_color(200, 200, 200)
    
    # Column Widths (Total ~277mm for A4 Landscape)
    col_width = [15, 40, 60, 25, 25, 30, 30, 52]
    headers = ["ID", "Owner/Client", "Location", "Type", "Beds", "Rent/Budget", "Size", "Status/Job"]
    
    for i in range(len(headers)):
        pdf.cell(col_width[i], 10, headers[i], 1, 0, 'C', 1)
    pdf.ln()
    
    # Table Body
    pdf.set_font("Helvetica", size=9)
    for index, row in df.iterrows():
        # Data mapping
        id_val = str(row.get('id', ''))
        name = str(row.get('owner_name', row.get('client_name', '')))[:18]
        loc = str(row.get('location', row.get('req_location', '')))[:25]
        portion = str(row.get('portion', row.get('req_portion', '')))
        beds = str(row.get('beds', row.get('beds_required', '')))
        money = str(row.get('rent', row.get('budget', '')))
        size = str(row.get('size', row.get('marla', '')))
        extra = str(row.get('status', row.get('job', '')))[:25]

        vals = [id_val, name, loc, portion, beds, money, size, extra]
        
        for i in range(len(vals)):
            # Encoding fix for special characters
            clean_text = vals[i].encode('latin-1', 'ignore').decode('latin-1')
            pdf.cell(col_width[i], 10, clean_text, 1)
        pdf.ln()
        
    return pdf.output(dest='S')

# --- 4. HEADER ---
st.markdown("""
    <div style="text-align: center; background-color: #1E1E1E; padding: 20px; border-radius: 15px; border: 2px solid #FF4B4B;">
        <h1 style="color: #FF4B4B; margin: 0; font-family: 'Arial Black';">DEEWARY PROPERTY MANAGER</h1>
        <p style="color: white; letter-spacing: 2px;">OWNER INVENTORY & CLIENT DATABASE</p>
    </div>
""", unsafe_allow_html=True)

# --- 5. STAFF LOGIN ---
st.sidebar.title("🔐 Staff Access")
user_name = st.sidebar.selectbox("Apna Naam Select Karen", ["Anas", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "admin786":
    menu = st.sidebar.radio("KAAM SELECT KAREN", [
        "🏠 Ghar ki Entry (Owners)", 
        "👤 Client ki Entry (Tenants)", 
        "📋 Full History (View Only)",
        "🛠️ Manage Records (Edit/Delete)",
        "🔍 Search & Print PDF"
    ])

    # --- 6. GHAR KI ENTRY ---
    if menu == "🏠 Ghar ki Entry (Owners)":
        st.subheader("🏡 Naye Ghar ya Shop ki Detail Darj Karen")
        with st.form("house_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                o_name = st.text_input("Owner ka Naam")
                o_contact = st.text_input("Owner ka Contact Number")
                loc = st.text_input("Location / Address")
                portion = st.selectbox("Portion", ["Full House", "Ground Floor", "First Floor", "Basement", "Shop", "Office"])
            with col2:
                beds = st.selectbox("Bedrooms (Beds)", ["1", "2", "3", "4", "5", "6+", "N/A"])
                rent = st.number_input("Demand Rent (PKR)", min_value=0)
                size = st.text_input("Size (Marla/Kanal)")
                status = st.selectbox("Status", ["Available", "Rent Out"])
            
            other = st.text_area("Other Details")
            if st.form_submit_button("Save House Record"):
                payload = {
                    "owner_name": o_name, "contact": o_contact, "location": loc, 
                    "portion": portion, "beds": beds, "rent": rent, 
                    "size": size, "status": status, "details": other, "added_by": user_name
                }
                supabase.table('house_inventory').insert(payload).execute()
                st.success("House Record Saved!")

    # --- 7. CLIENT KI ENTRY ---
    elif menu == "👤 Client ki Entry (Tenants)":
        st.subheader("👨‍👩‍👧‍👦 Client Requirement Register Karen")
        with st.form("client_form", clear_on_submit=True):
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                c_name = st.text_input("Client ka Naam")
                c_contact = st.text_input("Client Contact")
                c_loc = st.text_input("Required Location")
                c_job = st.text_input("Client ki Job/Business")
            with c_col2:
                c_budget = st.number_input("Monthly Budget (PKR)", min_value=0)
                c_portion = st.selectbox("Requirement", ["Full House", "Portion", "Flat", "Shop", "Office"])
                c_beds = st.selectbox("Required Beds", ["1", "2", "3", "4", "5", "6+", "Any"])
                c_marla = st.text_input("Required Size (Marla/Kanal)")
            
            c_family = st.text_input("Family Members")
            c_req = st.text_area("Extra Requirements")
            
            if st.form_submit_button("Save Client Lead"):
                payload = {
                    "client_name": c_name, "contact": c_contact, "req_location": c_loc, 
                    "budget": c_budget, "req_portion": c_portion, "family": c_family, 
                    "job": c_job, "beds_required": c_beds, "marla": c_marla, 
                    "requirements": c_req, "added_by": user_name
                }
                supabase.table('client_leads').insert(payload).execute()
                st.success("Client Lead Saved Successfully!")

    # --- 8. FULL HISTORY ---
    elif menu == "📋 Full History (View Only)":
        st.subheader("📋 Registered Data")
        tab1, tab2 = st.tabs(["🏠 Houses Inventory", "👥 Client Leads"])
        with tab1:
            res_h = supabase.table('house_inventory').select("*").execute()
            if res_h.data:
                st.dataframe(pd.DataFrame(res_h.data), use_container_width=True)
            else: st.write("No House Records.")
        with tab2:
            res_c = supabase.table('client_leads').select("*").execute()
            if res_c.data:
                st.dataframe(pd.DataFrame(res_c.data), use_container_width=True)
            else: st.write("No Client Leads.")

    # --- 9. MANAGE RECORDS (FIXED EDIT/DELETE) ---
    elif menu == "🛠️ Manage Records (Edit/Delete)":
        st.subheader("🛠️ Search by ID to Edit or Delete")
        target_table = st.radio("Select Table", ["house_inventory", "client_leads"], horizontal=True)
        search_id = st.number_input("Enter ID Number", min_value=1, step=1)
        
        if st.button("Find Record"):
            res = supabase.table(target_table).select("*").eq("id", search_id).execute()
            if res.data:
                st.session_state.found_record = res.data[0]
                st.session_state.target_table = target_table
                st.session_state.search_id = search_id
            else:
                st.session_state.found_record = None
                st.error("Is ID ka koi record nahi mila.")

        if "found_record" in st.session_state and st.session_state.found_record:
            record = st.session_state.found_record
            st.info(f"Editing ID: {st.session_state.search_id}")
            st.write(record)
            
            if st.session_state.target_table == "house_inventory":
                new_st = st.selectbox("Update Status", ["Available", "Rent Out"], 
                                     index=0 if record.get('status') == 'Available' else 1)
                if st.button("Confirm Status Update"):
                    supabase.table(st.session_state.target_table).update({"status": new_st}).eq("id", st.session_state.search_id).execute()
                    st.success("Status Updated! Refresh to see changes.")
                    del st.session_state.found_record
            
            st.divider()
            if st.button("🗑️ Delete Record Permanently"):
                supabase.table(st.session_state.target_table).delete().eq("id", st.session_state.search_id).execute()
                st.warning(f"Record ID {st.session_state.search_id} deleted.")
                del st.session_state.found_record

    # --- 10. SEARCH & PRINT PDF ---
    elif menu == "🔍 Search & Print PDF":
        st.subheader("🔍 Master Search & Table Reports")
        report_type = st.radio("Kiska Report Chahiye?", ["Houses", "Clients"])
        search_q = st.text_input("Search Anything...")
        
        table_name = 'house_inventory' if report_type == "Houses" else 'client_leads'
        res = supabase.table(table_name).select("*").execute()
        
        if res.data:
            df_all = pd.DataFrame(res.data)
            if search_q:
                df_all = df_all[df_all.astype(str).apply(lambda x: x.str.contains(search_q, case=False)).any(axis=1)]
            
            st.dataframe(df_all, use_container_width=True)
            
            if not df_all.empty:
                if st.button("Generate Professional PDF Report"):
                    pdf_bytes = generate_pdf(df_all, f"DEEWARY {report_type.upper()} REPORT")
                    st.download_button(
                        label="📥 Download Table PDF",
                        data=pdf_bytes,
                        file_name=f"Deewary_{report_type}_{datetime.now().strftime('%d-%m-%y')}.pdf",
                        mime="application/pdf"
                    )
        else:
            st.warning("Data nahi mila.")

else:
    if pwd != "":
        st.error("Please enter correct access code.")

st.divider()
st.caption(f"© {datetime.now().year} Deewary.com | System Active")
