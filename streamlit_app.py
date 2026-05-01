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

# --- 2. PAGE CONFIG & DARK ORANGE THEME ---
st.set_page_config(page_title="Deewary Pro Admin", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #0E1117; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #30363D; }
    
    /* Stats Cards */
    .metric-card {
        background-color: #1C2128;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363D;
        border-top: 4px solid #FF8C00;
        text-align: center;
    }
    
    /* Performance Table Styling */
    .perf-row {
        background-color: #161B22;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        border-left: 4px solid #FF8C00;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .stButton>button {
        background-color: #FF8C00;
        color: #000;
        font-weight: bold;
        border-radius: 5px;
        border: none;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. PDF FUNCTION ---
def generate_pdf(df, title):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_fill_color(255, 140, 0)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=title, ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    headers = ["ID", "Owner", "Location", "Portion", "Beds", "Rent", "Status", "Staff"]
    col_width = [15, 35, 60, 30, 20, 30, 40, 35]
    for i in range(len(headers)):
        pdf.cell(col_width[i], 10, headers[i], 1, 0, 'C', 1)
    pdf.ln()
    pdf.set_font("Arial", size=9)
    for _, row in df.iterrows():
        pdf.cell(col_width[0], 10, str(row.get('id', '')), 1)
        pdf.cell(col_width[1], 10, str(row.get('owner_name', ''))[:12], 1)
        pdf.cell(col_width[2], 10, str(row.get('location', ''))[:22], 1)
        pdf.cell(col_width[3], 10, str(row.get('portion', '')), 1)
        pdf.cell(col_width[4], 10, str(row.get('beds', '')), 1)
        pdf.cell(col_width[5], 10, str(row.get('rent', '')), 1)
        pdf.cell(col_width[6], 10, str(row.get('status', '')), 1)
        pdf.cell(col_width[7], 10, str(row.get('added_by', '')), 1)
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 4. HEADER ---
st.markdown("""
    <div style="background-color: #161B22; padding: 15px; border-radius: 10px; border-bottom: 2px solid #FF8C00; margin-bottom: 25px;">
        <h2 style="color: #FF8C00; margin: 0; font-family: 'Segoe UI';">DEEWARY<span style="color: white;">.PRO</span></h2>
        <p style="color: #8B949E; margin: 0; font-size: 12px; letter-spacing: 1.5px;">ADMIN PERFORMANCE DASHBOARD</p>
    </div>
""", unsafe_allow_html=True)

# --- 5. AUTH & NAVIGATION ---
user_name = st.sidebar.selectbox("User Account", ["Anas", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Security Pin", type="password")

if pwd == "admin786":
    menu = st.sidebar.radio("NAVIGATE", [
        "📊 Master Dashboard", 
        "📥 New Entry", 
        "📂 Database Records",
        "🛠️ Admin Tools",
        "🖨️ Export Reports"
    ])

    # --- 6. MASTER DASHBOARD (The Core Request) ---
    if menu == "📊 Master Dashboard":
        st.markdown(f"### 📈 Real-Time Performance: {date.today().strftime('%d %b, %Y')}")
        
        today = date.today().isoformat()
        h_today = supabase.table('house_inventory').select("*").gte('created_at', today).execute()
        c_today = supabase.table('client_leads').select("*").gte('created_at', today).execute()
        
        df_h = pd.DataFrame(h_today.data)
        df_c = pd.DataFrame(c_today.data)

        # Top Stats Row
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.markdown(f'<div class="metric-card"><h2>{len(df_h)}</h2><p style="color:#8B949E;">Houses Added Today</p></div>', unsafe_allow_html=True)
        with s2:
            st.markdown(f'<div class="metric-card"><h2>{len(df_c)}</h2><p style="color:#8B949E;">Leads Added Today</p></div>', unsafe_allow_html=True)
        with s3:
            # Check for Deals Closed (Status changed to Rent Out today)
            closed_today = len(df_h[df_h['status'] == 'Rent Out']) if not df_h.empty else 0
            st.markdown(f'<div class="metric-card"><h2 style="color:#00FF00;">{closed_today}</h2><p style="color:#8B949E;">Deals Closed Today</p></div>', unsafe_allow_html=True)
        with s4:
            total_active = len(supabase.table('house_inventory').select("*").eq('status', 'Available').execute().data)
            st.markdown(f'<div class="metric-card"><h2 style="color:#FF8C00;">{total_active}</h2><p style="color:#8B949E;">Total Available Stock</p></div>', unsafe_allow_html=True)

        st.markdown("<br>#### 👤 Staff-Wise Work Report (Today)", unsafe_allow_html=True)
        staff_members = ["Anas", "Sawer Khan", "Tariq Hussain"]
        
        # Display Staff Table
        for staff in staff_members:
            s_h = len(df_h[df_h['added_by'] == staff]) if not df_h.empty else 0
            s_c = len(df_c[df_c['added_by'] == staff]) if not df_c.empty else 0
            s_deals = len(df_h[(df_h['added_by'] == staff) & (df_h['status'] == 'Rent Out')]) if not df_h.empty else 0
            
            st.markdown(f"""
            <div class="perf-row">
                <span style="font-size:18px; font-weight:bold; color:white;">{staff}</span>
                <span style="color:#8B949E;">Properties: <b style="color:#FF8C00;">{s_h}</b></span>
                <span style="color:#8B949E;">Clients: <b style="color:#FF8C00;">{s_c}</b></span>
                <span style="color:#8B949E;">Deals Closed: <b style="color:#00FF00;">{s_deals}</b></span>
            </div>
            """, unsafe_allow_html=True)

    # --- 7. DATA ENTRY ---
    elif menu == "📥 New Entry":
        st.markdown("### 📝 Register Data")
        t_h, t_c = st.tabs(["🏠 Property Entry", "👤 Client Lead"])
        with t_h:
            with st.form("h_form", clear_on_submit=True):
                c_a, c_b = st.columns(2)
                with c_a:
                    o_name = st.text_input("Owner Name")
                    o_contact = st.text_input("Phone")
                    loc = st.text_input("Area")
                with c_b:
                    beds = st.selectbox("Beds", ["1","2","3","4","5+","N/A"])
                    rent = st.number_input("Demand", min_value=0)
                    status = st.selectbox("Status", ["Available", "Rent Out"])
                if st.form_submit_button("Save Property"):
                    supabase.table('house_inventory').insert({"owner_name":o_name, "contact":o_contact, "location":loc, "beds":beds, "rent":rent, "status":status, "added_by":user_name}).execute()
                    st.success("Saved!")
        with t_c:
            with st.form("c_form", clear_on_submit=True):
                cc1, cc2 = st.columns(2)
                with cc1:
                    cl_n = st.text_input("Client Name")
                    cl_p = st.text_input("Phone")
                with cc2:
                    cl_b = st.number_input("Budget", min_value=0)
                    cl_l = st.text_input("Target Area")
                if st.form_submit_button("Save Client Lead"):
                    supabase.table('client_leads').insert({"client_name":cl_n, "contact":cl_p, "budget":cl_b, "req_location":cl_l, "added_by":user_name}).execute()
                    st.success("Lead Recorded!")

    # --- 8. DATABASE RECORDS ---
    elif menu == "📂 Database Records":
        st.markdown("#### 📁 System Inventory")
        data = supabase.table('house_inventory').select("*").execute()
        st.dataframe(pd.DataFrame(data.data), use_container_width=True)

    # --- 9. ADMIN TOOLS ---
    elif menu == "🛠️ Admin Tools":
        st.markdown("### ⚙️ Management Console")
        db_type = st.radio("Select Table", ["house_inventory", "client_leads"], horizontal=True)
        target_id = st.number_input("Enter ID", min_value=1, step=1)
        if st.button("Delete Record Permanently"):
            supabase.table(db_type).delete().eq("id", target_id).execute()
            st.error(f"Record {target_id} deleted.")

    # --- 10. EXPORT ---
    elif menu == "🖨️ Export Reports":
        st.markdown("### 📄 Professional Reporting")
        sq = st.text_input("Search Location/Status")
        raw = supabase.table('house_inventory').select("*").execute()
        df_r = pd.DataFrame(raw.data)
        if sq: df_r = df_r[df_r.astype(str).apply(lambda x: x.str.contains(sq, case=False)).any(axis=1)]
        st.dataframe(df_r, use_container_width=True)
        if st.button("Generate PDF Report"):
            pdf = generate_pdf(df_r, "DEEWARY PRO - SYSTEM REPORT")
            st.download_button("📥 Download PDF", pdf, "Deewary_Report.pdf")

else:
    st.info("🔒 Security Pin Required.")

st.markdown("<br><p style='text-align:center; color:#30363D;'>System Admin: Anas | Real Estate & Construction Management</p>", unsafe_allow_html=True)
