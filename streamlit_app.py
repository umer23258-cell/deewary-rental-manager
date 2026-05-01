import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime, date
from fpdf import FPDF
import plotly.express as px # Charts ke liye

# --- 1. SUPABASE SETUP ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Deewary Property Manager", layout="wide", page_icon="🏢")

# --- 3. RESPONSIVE CSS ---
st.markdown("""
    <style>
    .block-container { max-width: 1200px; padding-top: 2rem; margin: auto; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    .sidebar-header { color: #FF4B4B; font-weight: bold; font-size: 14px; margin-top: 15px; text-transform: uppercase; }
    
    .stButton>button { width: 100%; border-radius: 4px; background-color: white; color: #2f3640; transition: 0.3s; }
    .stButton>button:hover { border-color: #FF4B4B; color: #FF4B4B; }

    .metric-card {
        background-color: #ffffff; padding: 20px; border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); text-align: center; border-top: 4px solid #FF4B4B;
    }
    .main-header { text-align: center; background-color: #2c3e50; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- 4. PDF ENGINE ---
def generate_pdf(df, title):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, txt=title, ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Helvetica", 'B', 10)
    pdf.set_fill_color(200, 200, 200)
    headers = ["ID", "Owner/Client", "Location", "Type", "Beds", "Rent/Budget", "Size", "Status/Job"]
    col_width = [15, 40, 60, 25, 25, 30, 30, 52]
    for i in range(len(headers)):
        pdf.cell(col_width[i], 10, headers[i], 1, 0, 'C', 1)
    pdf.ln()
    pdf.set_font("Helvetica", size=9)
    for index, row in df.iterrows():
        vals = [str(row.get('id','')), str(row.get('owner_name', row.get('client_name','')))[:18], str(row.get('location', row.get('req_location','')))[:25],
                str(row.get('portion', row.get('req_portion',''))), str(row.get('beds', row.get('beds_required',''))),
                str(row.get('rent', row.get('budget',''))), str(row.get('size', row.get('marla',''))), str(row.get('status', row.get('job','')))[:25]]
        for i in range(len(vals)):
            pdf.cell(col_width[i], 10, vals[i].encode('latin-1','ignore').decode('latin-1'), 1)
        pdf.ln()
    return pdf.output(dest='S')

# --- 5. HEADER ---
st.markdown('<div class="main-header"><h2 style="color: white; margin: 0;">DEEWARY CRM</h2><p style="color: #FF4B4B; margin: 0; font-size: 12px; font-weight: bold;">MANAGEMENT DASHBOARD</p></div>', unsafe_allow_html=True)

# --- 6. SIDEBAR NAVIGATION ---
st.sidebar.markdown("### 🔐 User Login")
user_name = st.sidebar.selectbox("Authorized User", ["Anas", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "admin786":
    st.sidebar.markdown('<p class="sidebar-header">🏠 Main View</p>', unsafe_allow_html=True)
    if st.sidebar.button("📊 Daily Dashboard"):
        st.session_state.page = "dashboard"

    st.sidebar.markdown('<p class="sidebar-header">📥 Data Entry</p>', unsafe_allow_html=True)
    if st.sidebar.button("🏠 Property Registration"):
        st.session_state.page = "property"
    if st.sidebar.button("👤 Client Requirement"):
        st.session_state.page = "client"
        
    st.sidebar.markdown('<p class="sidebar-header">📊 Management</p>', unsafe_allow_html=True)
    if st.sidebar.button("📋 Full Inventory List"):
        st.session_state.page = "history"
    if st.sidebar.button("🛠️ Update/Delete"):
        st.session_state.page = "manage"
    if st.sidebar.button("🔍 Search & Reports"):
        st.session_state.page = "search"

    if "page" not in st.session_state: st.session_state.page = "dashboard"

    # --- 7. DASHBOARD PAGE ---
    if st.session_state.page == "dashboard":
        st.subheader(f"📅 Daily Working Progress - {date.today().strftime('%d %B, %Y')}")
        
        # Fetch Data
        h_data = supabase.table('house_inventory').select("*").execute()
        c_data = supabase.table('client_leads').select("*").execute()
        
        df_h = pd.DataFrame(h_data.data)
        df_c = pd.DataFrame(c_data.data)
        
        # Calculations
        total_p = len(df_h) if not df_h.empty else 0
        total_c = len(df_c) if not df_c.empty else 0
        
        # Layout: Top Metrics
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f'<div class="metric-card"><h3>🏠 {total_p}</h3><p>Total Properties</p></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><h3>👥 {total_c}</h3><p>Total Clients</p></div>', unsafe_allow_html=True)
        with m3:
            # Aaj ki entry count (created_at filter depend karta hai supabase column par)
            today_str = date.today().isoformat()
            aaj_p = len(df_h[df_h['created_at'].str.contains(today_str)]) if not df_h.empty and 'created_at' in df_h else 0
            st.markdown(f'<div class="metric-card"><h3>📈 {aaj_p}</h3><p>New Entries Today</p></div>', unsafe_allow_html=True)

        st.divider()
        
        # Layout: Charts
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("### 🏠 Property Status")
            if not df_h.empty:
                fig_status = px.pie(df_h, names='status', color_discrete_sequence=['#2c3e50', '#FF4B4B'])
                st.plotly_chart(fig_status, use_container_width=True)
        
        with col_b:
            st.write("### ✍️ Performance by Staff")
            if not df_h.empty:
                staff_perf = df_h['added_by'].value_counts().reset_index()
                fig_staff = px.bar(staff_perf, x='added_by', y='count', color='added_by', labels={'count':'Entries'})
                st.plotly_chart(fig_staff, use_container_width=True)

        st.write("### 🕒 Recent Activity (Last 5 Entries)")
        if not df_h.empty:
            st.table(df_h[['owner_name', 'location', 'rent', 'added_by']].tail(5))

    # --- (Baki Pages: Property, Client, History, Manage, Search - Same as before) ---
    elif st.session_state.page == "property":
        st.subheader("Add New Property")
        with st.form("h_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                o_name = st.text_input("Owner Name"); o_contact = st.text_input("Phone Number"); loc = st.text_input("Location")
                portion = st.selectbox("Type", ["Full House", "Ground Floor", "First Floor", "Basement", "Shop", "Office"])
            with c2:
                beds = st.selectbox("Beds", ["1", "2", "3", "4", "5", "6+", "N/A"]); rent = st.number_input("Demand", min_value=0)
                size = st.text_input("Area"); status = st.selectbox("Status", ["Available", "Rent Out"])
            if st.form_submit_button("Save Record"):
                supabase.table('house_inventory').insert({"owner_name": o_name, "contact": o_contact, "location": loc, "portion": portion, "beds": beds, "rent": rent, "size": size, "status": status, "added_by": user_name}).execute()
                st.success("Saved!")

    elif st.session_state.page == "client":
        st.subheader("Add Client Requirement")
        with st.form("c_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                c_name = st.text_input("Client Name"); c_contact = st.text_input("Phone"); c_loc = st.text_input("Area")
            with c2:
                c_budget = st.number_input("Budget", min_value=0); c_portion = st.selectbox("Type", ["Full House", "Portion", "Flat", "Shop", "Office"]); c_marla = st.text_input("Size")
            if st.form_submit_button("Register Client"):
                supabase.table('client_leads').insert({"client_name": c_name, "contact": c_contact, "req_location": c_loc, "budget": c_budget, "req_portion": c_portion, "marla": c_marla, "added_by": user_name}).execute()
                st.success("Registered!")

    elif st.session_state.page == "history":
        st.subheader("Database History")
        t1, t2 = st.tabs(["🏠 All Properties", "👥 Client Database"])
        with t1:
            res = supabase.table('house_inventory').select("*").execute()
            st.dataframe(pd.DataFrame(res.data), use_container_width=True)
        with t2:
            res = supabase.table('client_leads').select("*").execute()
            st.dataframe(pd.DataFrame(res.data), use_container_width=True)

    elif st.session_state.page == "manage":
        st.subheader("Manage Records")
        tbl = st.radio("Select Table", ["house_inventory", "client_leads"], horizontal=True)
        sid = st.number_input("Record ID", min_value=1, step=1)
        if st.button("Fetch Data"):
            res = supabase.table(tbl).select("*").eq("id", sid).execute()
            if res.data: st.session_state.found = res.data[0]
            else: st.error("No record found.")
        if "found" in st.session_state:
            st.json(st.session_state.found)
            if st.button("🗑️ Delete Permanently"):
                supabase.table(tbl).delete().eq("id", sid).execute()
                st.warning("Deleted!")
                del st.session_state.found

    elif st.session_state.page == "search":
        st.subheader("Search & Export")
        mode = st.radio("Category", ["Houses", "Clients"], horizontal=True)
        q = st.text_input("Keywords...")
        tbl_name = 'house_inventory' if mode == "Houses" else 'client_leads'
        res = supabase.table(tbl_name).select("*").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            if q: df = df[df.astype(str).apply(lambda x: x.str.contains(q, case=False)).any(axis=1)]
            st.dataframe(df, use_container_width=True)
            if not df.empty and st.button("Download PDF"):
                pdf_bytes = generate_pdf(df, f"DEEWARY {mode.upper()} REPORT")
                st.download_button("📥 Download", pdf_bytes, f"{mode}_Report.pdf", "application/pdf")

else:
    if pwd != "": st.error("Access Denied.")

st.markdown("---")
st.caption(f"© {datetime.now().year} Deewary.com | Dashboard Active")
