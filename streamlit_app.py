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
    /* Main Dark Background */
    [data-testid="stAppViewContainer"] {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    
    /* Sidebar Dark Styling */
    [data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }

    /* Professional Orange Metrics */
    .metric-card {
        background-color: #1C2128;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30363D;
        border-top: 4px solid #FF8C00; /* Electric Orange */
        text-align: center;
        transition: 0.3s;
    }
    .metric-card:hover {
        border-color: #FF8C00;
        transform: translateY(-5px);
    }
    
    /* Staff Performance Cards */
    .staff-card {
        background-color: #1C2128;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 5px solid #FF8C00;
        color: #E6EDF3;
    }

    /* Orange Buttons */
    .stButton>button {
        background-color: #FF8C00;
        color: #000;
        font-weight: bold;
        border-radius: 5px;
        border: none;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #FFA500;
        color: #000;
    }

    /* Inputs Styling */
    input, select, textarea {
        background-color: #0D1117 !important;
        color: white !important;
        border: 1px solid #30363D !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. PDF FUNCTION (Table Format) ---
def generate_pdf(df, title):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_fill_color(255, 140, 0) # Orange Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=title, ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 10)
    headers = ["ID", "Owner", "Location", "Portion", "Beds", "Rent", "Size", "Status"]
    col_width = [15, 40, 60, 25, 25, 30, 30, 40]
    
    for i in range(len(headers)):
        pdf.cell(col_width[i], 10, headers[i], 1, 0, 'C', 1)
    pdf.ln()
    
    pdf.set_font("Arial", size=9)
    for _, row in df.iterrows():
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

# --- 4. HEADER ---
st.markdown("""
    <div style="background-color: #161B22; padding: 15px; border-radius: 10px; border-bottom: 2px solid #FF8C00; margin-bottom: 20px;">
        <h2 style="color: #FF8C00; margin: 0; font-family: 'Segoe UI';">DEEWARY<span style="color: white;">.PRO</span></h2>
        <p style="color: #8B949E; margin: 0; font-size: 12px; letter-spacing: 1px;">MANAGEMENT INTERFACE v2.0</p>
    </div>
""", unsafe_allow_html=True)

# --- 5. AUTH & NAVIGATION ---
user_name = st.sidebar.selectbox("User Account", ["Anas", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Security Pin", type="password")

if pwd == "admin786":
    menu = st.sidebar.radio("NAVIGATE", [
        "📈 Daily Insights", 
        "📥 Data Entry", 
        "📂 Database History",
        "🛠️ Admin Tools",
        "🖨️ Export Reports"
    ])

    # --- 6. DAILY INSIGHTS ---
    if menu == "📈 Daily Insights":
        st.markdown("### 📊 Today's Performance Metrics")
        today = date.today().isoformat()
        
        h_data = supabase.table('house_inventory').select("*").gte('created_at', today).execute()
        c_data = supabase.table('client_leads').select("*").gte('created_at', today).execute()
        
        df_h = pd.DataFrame(h_data.data)
        df_c = pd.DataFrame(c_data.data)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="metric-card"><h3>{len(df_h)}</h3><p style="color:#8B949E;">Houses Added</p></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><h3>{len(df_c)}</h3><p style="color:#8B949E;">Leads Created</p></div>', unsafe_allow_html=True)
        with c3:
            closed = len(df_h[df_h['status'] == 'Rent Out']) if not df_h.empty else 0
            st.markdown(f'<div class="metric-card"><h3 style="color:#00FF00;">{closed}</h3><p style="color:#8B949E;">Deals Closed</p></div>', unsafe_allow_html=True)

        st.markdown("<br>#### 👤 Staff Contribution", unsafe_allow_html=True)
        for staff in ["Anas", "Sawer Khan", "Tariq Hussain"]:
            count_h = len(df_h[df_h['added_by'] == staff]) if not df_h.empty else 0
            count_c = len(df_c[df_c['added_by'] == staff]) if not df_c.empty else 0
            st.markdown(f"""
            <div class="staff-card">
                <b>{staff}</b>: &nbsp;&nbsp; {count_h} Properties &nbsp; | &nbsp; {count_c} Client Leads
            </div>
            """, unsafe_allow_html=True)

    # --- 7. DATA ENTRY (Houses & Clients) ---
    elif menu == "📥 Data Entry":
        st.markdown("### 📝 New Registration")
        tab_h, tab_c = st.tabs(["🏠 Property Entry", "👤 Client Lead"])
        
        with tab_h:
            with st.form("h_form"):
                col_a, col_b = st.columns(2)
                with col_a:
                    o_name = st.text_input("Owner Name")
                    o_contact = st.text_input("Contact")
                    loc = st.text_input("Location")
                with col_b:
                    beds = st.selectbox("Bedrooms", ["1", "2", "3", "4", "5+", "N/A"])
                    rent = st.number_input("Demand Rent", min_value=0)
                    status = st.selectbox("Status", ["Available", "Rent Out"])
                if st.form_submit_button("Submit Property"):
                    supabase.table('house_inventory').insert({"owner_name": o_name, "contact": o_contact, "location": loc, "beds": beds, "rent": rent, "status": status, "added_by": user_name}).execute()
                    st.success("Property Saved!")

        with tab_c:
            with st.form("c_form"):
                cc1, cc2 = st.columns(2)
                with cc1:
                    cl_name = st.text_input("Client Name")
                    cl_contact = st.text_input("Phone")
                with cc2:
                    cl_budget = st.number_input("Budget", min_value=0)
                    cl_loc = st.text_input("Area Preference")
                if st.form_submit_button("Submit Lead"):
                    supabase.table('client_leads').insert({"client_name": cl_name, "contact": cl_contact, "budget": cl_budget, "req_location": cl_loc, "added_by": user_name}).execute()
                    st.success("Lead Recorded!")

    # --- 8. DATABASE HISTORY ---
    elif menu == "📂 Database History":
        h_res = supabase.table('house_inventory').select("*").execute()
        st.markdown("#### 🏠 Full Property List")
        st.dataframe(pd.DataFrame(h_res.data), use_container_width=True)

    # --- 9. ADMIN TOOLS (Delete by ID) ---
    elif menu == "🛠️ Admin Tools":
        st.markdown("### ⚠️ Remove Records")
        target_db = st.radio("Table", ["house_inventory", "client_leads"], horizontal=True)
        del_id = st.number_input("Record ID", min_value=1, step=1)
        if st.button("Delete Record"):
            supabase.table(target_db).delete().eq("id", del_id).execute()
            st.error(f"ID {del_id} deleted.")

    # --- 10. EXPORT REPORTS ---
    elif menu == "🖨️ Export Reports":
        st.markdown("### 🔍 Filter & Print")
        sq = st.text_input("Search Location or Status")
        raw = supabase.table('house_inventory').select("*").execute()
        df_r = pd.DataFrame(raw.data)
        if sq: df_r = df_r[df_r.astype(str).apply(lambda x: x.str.contains(sq, case=False)).any(axis=1)]
        st.dataframe(df_r, use_container_width=True)
        if st.button("Generate Professional PDF"):
            pdf_bytes = generate_pdf(df_r, "DEEWARY PRO INVENTORY")
            st.download_button("📥 Download PDF", pdf_bytes, "Deewary_Pro_Report.pdf")

else:
    st.markdown("<h4 style='text-align:center;'>🔒 Unauthorized Access. Please enter the Pin.</h4>", unsafe_allow_html=True)

st.markdown("<br><p style='text-align:center; color:#30363D;'>System Admin: Anas | Version 2.0</p>", unsafe_allow_html=True)
