import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
from fpdf import FPDF
import io

# --- SUPABASE SETUP ---
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# --- PAGE CONFIG ---
st.set_page_config(page_title="Deewary Premium", layout="wide", page_icon="🏢")

# --- LUXURY DARK THEME CSS ---
st.markdown("""
    <style>
    /* Main App Background */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    
    /* Luxury Header */
    .premium-header {
        background: linear-gradient(90deg, #FF4B4B 0%, #8B0000 100%);
        padding: 30px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 40px;
        border-bottom: 5px solid #333;
        box-shadow: 0 10px 30px rgba(255, 75, 75, 0.2);
    }

    /* Cards for Forms/Search */
    .stForm, .search-box {
        background-color: #1E2129 !important;
        border: 1px solid #3E4452 !important;
        border-radius: 15px !important;
        padding: 25px !important;
    }

    /* Red Premium Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #FF4B4B 0%, #D32F2F 100%) !important;
        color: white !important;
        border: none !important;
        padding: 12px 24px !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 75, 75, 0.4);
    }

    /* Sidebar Customization */
    [data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 1px solid #222;
    }

    /* Dataframe Table Style */
    .stDataFrame {
        border: 1px solid #333;
        border-radius: 10px;
    }
    
    /* Text Inputs */
    input, select, textarea {
        background-color: #16191F !important;
        color: white !important;
        border: 1px solid #333 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- PDF GENERATOR ---
def generate_pdf(df, title):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 15, txt=title, ln=True, align='C')
    pdf.ln(5)
    
    # Header Colors
    pdf.set_fill_color(255, 75, 75)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 10)
    
    cols = ["ID", "Owner/Client", "Location", "Type", "Beds", "Rent/Budget", "Status"]
    col_widths = [15, 45, 60, 30, 20, 35, 40]
    
    for i in range(len(cols)):
        pdf.cell(col_widths[i], 10, cols[i], 1, 0, 'C', True)
    pdf.ln()
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=9)
    for _, row in df.iterrows():
        # Mapping values
        v1 = str(row.get('id', ''))
        v2 = str(row.get('owner_name', row.get('client_name', '')))[:20]
        v3 = str(row.get('location', row.get('req_location', '')))[:25]
        v4 = str(row.get('portion', row.get('req_portion', '')))
        v5 = str(row.get('beds', row.get('beds_required', '')))
        v6 = str(row.get('rent', row.get('budget', '')))
        v7 = str(row.get('status', 'Active'))
        
        vals = [v1, v2, v3, v4, v5, v6, v7]
        for i in range(len(vals)):
            clean = vals[i].encode('latin-1', 'ignore').decode('latin-1')
            pdf.cell(col_widths[i], 10, clean, 1)
        pdf.ln()
    return pdf.output(dest='S')

# --- MAIN UI ---
st.markdown('<div class="premium-header"><h1>DEEWARY PRO</h1><p>Luxury Real Estate Management System</p></div>', unsafe_allow_html=True)

# --- SIDEBAR LOGIN ---
st.sidebar.markdown("<h2 style='text-align: center; color: #FF4B4B;'>DEEWARY</h2>", unsafe_allow_html=True)
user_name = st.sidebar.selectbox("Operator", ["Anas", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Security Code", type="password")

if pwd == "admin786":
    menu = st.sidebar.radio("NAVIGATION", [
        "🏢 Dashboard & Search",
        "➕ Add Property", 
        "➕ Add Client", 
        "📑 Database View",
        "⚙️ System Settings"
    ])

    # --- DASHBOARD & SEARCH ---
    if menu == "🏢 Dashboard & Search":
        st.subheader("🔍 Master Search")
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                q = st.text_input("Enter Area, Name or ID...", placeholder="Search anything...")
            with col2:
                cat = st.selectbox("Category", ["Houses", "Clients"])
            with col3:
                st.write("##")
                search_btn = st.button("RUN SEARCH")

        table = 'house_inventory' if cat == "Houses" else 'client_leads'
        res = supabase.table(table).select("*").execute()
        
        if res.data:
            df = pd.DataFrame(res.data)
            if q:
                df = df[df.astype(str).apply(lambda x: x.str.contains(q, case=False)).any(axis=1)]
            
            st.markdown(f"**Results Found:** `{len(df)}`")
            st.dataframe(df, use_container_width=True)
            
            if not df.empty:
                if st.button("Generate Professional PDF"):
                    pdf_bytes = generate_pdf(df, f"DEEWARY {cat.upper()} REPORT")
                    st.download_button("Download Report", pdf_bytes, "Deewary_Report.pdf", "application/pdf")

    # --- ADD RECORD (Unified Styling) ---
    elif menu == "➕ Add Property":
        st.subheader("🏠 New Property Listing")
        with st.form("property_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                o_name = st.text_input("Owner Name")
                o_num = st.text_input("Contact")
                loc = st.text_input("Location")
            with c2:
                ptype = st.selectbox("Type", ["Full House", "Portion", "Shop", "Office", "Plot"])
                rent = st.number_input("Demand", min_value=0)
                beds = st.selectbox("Beds", ["1","2","3","4","5","6+"])
            
            det = st.text_area("Notes")
            if st.form_submit_button("SUBMIT LISTING"):
                data = {"owner_name": o_name, "contact": o_num, "location": loc, "portion": ptype, "rent": rent, "beds": beds, "details": det, "added_by": user_name}
                supabase.table('house_inventory').insert(data).execute()
                st.success("Listing Published!")

    # --- MANAGE / SETTINGS ---
    elif menu == "⚙️ System Settings":
        st.subheader("🛠️ Record Management")
        t_select = st.radio("Target Table", ["house_inventory", "client_leads"], horizontal=True)
        id_val = st.number_input("Enter Record ID", min_value=1)
        
        col_del, col_up = st.columns(2)
        with col_del:
            if st.button("🗑️ DELETE PERMANENTLY"):
                supabase.table(t_select).delete().eq("id", id_val).execute()
                st.error(f"ID {id_val} removed.")
                st.rerun()
        with col_up:
             st.info("Edit features can be added here as per need.")

else:
    if pwd: st.error("Access Denied!")
    st.warning("Please enter your security code in the sidebar.")

st.markdown("<br><hr><p style='text-align: center; color: #555;'>DEEWARY PREMIUM CMS | © 2026</p>", unsafe_allow_html=True)
