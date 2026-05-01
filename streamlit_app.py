import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime, date
from fpdf import FPDF
import io

# --- 1. SUPABASE SETUP ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. PAGE CONFIG & PREMIUM THEME ---
st.set_page_config(page_title="Deewary Admin Portal", layout="wide", page_icon="🏢")

# Custom CSS for Premium Dashboard Look
st.markdown("""
    <style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* Global Background and Font */
    [data-testid="stAppViewContainer"] {
        background-color: #f8f9fa;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #111;
        color: white;
    }
    
    /* Professional Cards for Metrics */
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-bottom: 4px solid #cc0000;
        text-align: center;
    }
    
    /* Staff Performance Boxes */
    .staff-card {
        background: linear-gradient(135deg, #1e1e1e 0%, #333 100%);
        color: #fff;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 12px;
        border-left: 6px solid #cc0000;
    }
    
    /* Success/Button Styling */
    .stButton>button {
        background-color: #cc0000;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #ff3333;
        box-shadow: 0 4px 12px rgba(204,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. PDF FUNCTION ---
def generate_pdf(df, title):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=title, ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(204, 0, 0) # Dark Red Header
    pdf.set_text_color(255, 255, 255)
    
    col_width = [15, 40, 60, 25, 25, 30, 30, 40]
    headers = ["ID", "Owner", "Location", "Portion", "Beds", "Rent", "Size", "Status"]
    for i in range(len(headers)):
        pdf.cell(col_width[i], 10, headers[i], 1, 0, 'C', 1)
    pdf.ln()
    
    pdf.set_font("Arial", size=9)
    pdf.set_text_color(0, 0, 0)
    for index, row in df.iterrows():
        pdf.cell(col_width[0], 10, str(row.get('id', '')), 1)
        pdf.cell(col_width[1], 10, str(row.get('owner_name', ''))[:15], 1)
        pdf.cell(col_width[2], 10, str(row.get('location', ''))[:25], 1)
        pdf.cell(col_width[3], 10, str(row.get('portion', '')), 1)
        pdf.cell(col_width[4], 10, str(row.get('beds', '')), 1)
        pdf.cell(col_width[5], 10, str(row.get('rent', '')), 1)
        pdf.cell(col_width[6], 10, str(row.get('size', '')), 1)
        pdf.cell(col_width[7], 10, str(row.get('status', '')), 1)
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 4. SLEEK HEADER ---
st.markdown("""
    <div style="background-color: #111; padding: 15px; border-radius: 10px; border-left: 8px solid #cc0000; margin-bottom: 25px;">
        <h2 style="color: white; margin: 0; font-family: 'Trebuchet MS';">DEEWARY<span style="color: #cc0000;">.COM</span></h2>
        <p style="color: #bbb; margin: 0; font-size: 13px; text-transform: uppercase; letter-spacing: 2px;">Real Estate & Construction Management</p>
    </div>
""", unsafe_allow_html=True)

# --- 5. STAFF LOGIN ---
st.sidebar.markdown("### 🏢 Admin Access")
user_name = st.sidebar.selectbox("Select User", ["Anas", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "admin786":
    menu = st.sidebar.radio("DASHBOARD MENU", [
        "📊 Daily Performance", 
        "🏠 Property Inventory", 
        "👤 Client Leads", 
        "📋 Database History",
        "🛠️ Admin Control (Edit/Delete)",
        "🔍 Report Generator"
    ])

    # --- 6. DAILY PERFORMANCE ---
    if menu == "📊 Daily Performance":
        st.markdown("### 📈 Today's Activity Overview")
        today_date = date.today().isoformat()
        
        # Fetching data
        h_res = supabase.table('house_inventory').select("*").gte('created_at', today_date).execute()
        c_res = supabase.table('client_leads').select("*").gte('created_at', today_date).execute()
        
        df_h = pd.DataFrame(h_res.data)
        df_c = pd.DataFrame(c_res.data)

        # Metrics Row
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f'<div class="metric-card"><h2 style="color:#cc0000;">{len(df_h)}</h2><p>New Properties</p></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><h2 style="color:#cc0000;">{len(df_c)}</h2><p>New Leads</p></div>', unsafe_allow_html=True)
        with m3:
            rent_outs = len(df_h[df_h['status'] == 'Rent Out']) if not df_h.empty else 0
            st.markdown(f'<div class="metric-card"><h2 style="color:#28a745;">{rent_outs}</h2><p>Units Rented Out</p></div>', unsafe_allow_html=True)

        st.markdown("<br>### 👤 Staff Performance Report", unsafe_allow_html=True)
        for staff in ["Anas", "Sawer Khan", "Tariq Hussain"]:
            s_h = len(df_h[df_h['added_by'] == staff]) if not df_h.empty else 0
            s_c = len(df_c[df_c['added_by'] == staff]) if not df_c.empty else 0
            st.markdown(f"""
            <div class="staff-card">
                <table style="width:100%; border:none;">
                    <tr>
                        <td style="font-size:18px; font-weight:bold;">{staff}</td>
                        <td style="text-align:right;">🏠 Inventory: <b>{s_h}</b> | 👥 Leads: <b>{s_c}</b></td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

    # --- 7. PROPERTY ENTRY ---
    elif menu == "🏠 Property Inventory":
        st.markdown("### 🏡 Register Property")
        with st.container():
            with st.form("prop_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    o_name = st.text_input("Owner Name")
                    o_contact = st.text_input("Contact Number")
                    loc = st.text_input("Full Address/Location")
                with col2:
                    beds = st.selectbox("Beds", ["1", "2", "3", "4", "5+", "N/A"])
                    rent = st.number_input("Demand Rent", min_value=0)
                    status = st.selectbox("Current Status", ["Available", "Rent Out"])
                if st.form_submit_button("Add to Inventory"):
                    supabase.table('house_inventory').insert({
                        "owner_name": o_name, "contact": o_contact, "location": loc, 
                        "beds": beds, "rent": rent, "status": status, "added_by": user_name
                    }).execute()
                    st.success("Property Added Successfully!")

    # --- 8. CLIENT LEADS ---
    elif menu == "👤 Client Leads":
        st.markdown("### 👥 Register Lead")
        with st.form("lead_form", clear_on_submit=True):
            lc1, lc2 = st.columns(2)
            with lc1:
                c_name = st.text_input("Client Name")
                c_contact = st.text_input("Contact")
            with lc2:
                c_budget = st.number_input("Budget (PKR)", min_value=0)
                c_loc = st.text_input("Target Location")
            if st.form_submit_button("Save Lead"):
                supabase.table('client_leads').insert({
                    "client_name": c_name, "contact": c_contact, 
                    "budget": c_budget, "req_location": c_loc, "added_by": user_name
                }).execute()
                st.success("Lead Registered!")

    # --- 9. DATABASE HISTORY ---
    elif menu == "📋 Database History":
        t1, t2 = st.tabs(["🏠 Property Records", "👥 Client Leads"])
        with t1:
            data = supabase.table('house_inventory').select("*").execute()
            st.dataframe(pd.DataFrame(data.data), use_container_width=True)
        with t2:
            data_c = supabase.table('client_leads').select("*").execute()
            st.dataframe(pd.DataFrame(data_c.data), use_container_width=True)

    # --- 10. ADMIN CONTROL ---
    elif menu == "🛠️ Admin Control (Edit/Delete)":
        st.markdown("### 🛠️ Record Management")
        target = st.radio("Select Database", ["house_inventory", "client_leads"], horizontal=True)
        search_id = st.number_input("Search ID", min_value=1, step=1)
        if st.button("Search Record"):
            res = supabase.table(target).select("*").eq("id", search_id).execute()
            if res.data:
                st.write(res.data[0])
                if st.button("Confirm Permanent Delete"):
                    supabase.table(target).delete().eq("id", search_id).execute()
                    st.error("Record Permanently Removed.")
                    st.rerun()
            else: st.error("ID Not Found.")

    # --- 11. REPORT GENERATOR ---
    elif menu == "🔍 Report Generator":
        st.markdown("### 🔍 Search & Export")
        search_term = st.text_input("Filter by Location, Owner, or Status")
        raw_data = supabase.table('house_inventory').select("*").execute()
        df_final = pd.DataFrame(raw_data.data)
        if search_term and not df_final.empty:
            df_final = df_final[df_final.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)]
        st.dataframe(df_final, use_container_width=True)
        if st.button("Export to Professional PDF"):
            pdf_out = generate_pdf(df_final, "DEEWARY.COM - INVENTORY REPORT")
            st.download_button("📥 Download Report", pdf_out, "Deewary_Report.pdf")

else:
    st.info("👋 Welcome! Please enter your admin code to access the portal.")

st.markdown("<br><hr><p style='text-align:center; color:grey;'>© 2026 Deewary.com Portal | System Admin: Anas</p>", unsafe_allow_html=True)
