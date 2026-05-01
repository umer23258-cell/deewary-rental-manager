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

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Deewary Admin", layout="wide", page_icon="🏢")

# Professional CSS
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .report-box {
        background-color: #f0f2f6; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #FF4B4B;
        margin-bottom: 10px;
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
    pdf.set_fill_color(200, 200, 200)
    col_width = [15, 40, 60, 25, 25, 30, 30, 40]
    headers = ["ID", "Owner", "Location", "Portion", "Beds", "Rent", "Size", "Status"]
    for i in range(len(headers)):
        pdf.cell(col_width[i], 10, headers[i], 1, 0, 'C', 1)
    pdf.ln()
    pdf.set_font("Arial", size=9)
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

# --- 4. PROFESSIONAL HEADER (Size Reduced) ---
st.markdown("""
    <div style="display: flex; align-items: center; justify-content: center; background-color: #1E1E1E; padding: 10px; border-radius: 8px; border-bottom: 3px solid #FF4B4B;">
        <h2 style="color: #FF4B4B; margin: 0; font-size: 24px; font-weight: bold; letter-spacing: 1px;">DEEWARY.COM</h2>
        <span style="color: white; margin-left: 15px; font-size: 14px; border-left: 1px solid grey; padding-left: 15px;">PROPERTY MANAGEMENT SYSTEM</span>
    </div>
""", unsafe_allow_html=True)

# --- 5. STAFF LOGIN ---
st.sidebar.title("🔐 Login")
user_name = st.sidebar.selectbox("User", ["Anas", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "admin786":
    menu = st.sidebar.radio("MENU", [
        "📊 Daily Performance Report", # New Section
        "🏠 House Entry", 
        "👤 Client Entry", 
        "📋 View History",
        "🛠️ Edit/Delete (By ID)",
        "🔍 Search & PDF"
    ])

    # --- 6. DAILY PERFORMANCE REPORT ---
    if menu == "📊 Daily Performance Report":
        st.subheader(f"📅 Today's Report ({date.today().strftime('%d %B, %Y')})")
        
        # Data Fetching
        today_date = date.today().isoformat()
        houses_today = supabase.table('house_inventory').select("*").gte('created_at', today_date).execute()
        clients_today = supabase.table('client_leads').select("*").gte('created_at', today_date).execute()
        
        df_h = pd.DataFrame(houses_today.data)
        df_c = pd.DataFrame(clients_today.data)

        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("New Houses Added", len(df_h))
        with col_b:
            st.metric("New Clients Registered", len(df_c))

        st.markdown("### 👤 Staff Wise Activity")
        staff_list = ["Anas", "Sawer Khan", "Tariq Hussain"]
        
        for staff in staff_list:
            staff_h = df_h[df_h['added_by'] == staff] if not df_h.empty else pd.DataFrame()
            staff_c = df_c[df_c['added_by'] == staff] if not df_c.empty else pd.DataFrame()
            
            with st.container():
                st.markdown(f"""
                <div class="report-box">
                    <h4 style="margin:0;">{staff}</h4>
                    <p style="margin:5px 0;">🏠 Houses Entered: <b>{len(staff_h)}</b> | 👥 Clients Handled: <b>{len(staff_c)}</b></p>
                </div>
                """, unsafe_allow_html=True)

    # --- 7. HOUSE ENTRY ---
    elif menu == "🏠 House Entry":
        st.subheader("🏡 Register New Property")
        with st.form("h_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                o_name = st.text_input("Owner Name")
                o_contact = st.text_input("Contact")
                loc = st.text_input("Location")
            with c2:
                beds = st.selectbox("Beds", ["1", "2", "3", "4", "5+", "N/A"])
                rent = st.number_input("Rent", min_value=0)
                status = st.selectbox("Status", ["Available", "Rent Out"])
            if st.form_submit_button("Save Record"):
                supabase.table('house_inventory').insert({
                    "owner_name": o_name, "contact": o_contact, "location": loc, 
                    "beds": beds, "rent": rent, "status": status, "added_by": user_name
                }).execute()
                st.success("Saved!")

    # --- 8. CLIENT ENTRY ---
    elif menu == "👤 Client Entry":
        st.subheader("👥 Register Client Requirement")
        with st.form("c_form", clear_on_submit=True):
            cc1, cc2 = st.columns(2)
            with cc1:
                c_name = st.text_input("Client Name")
                c_contact = st.text_input("Contact")
            with cc2:
                c_budget = st.number_input("Budget", min_value=0)
                c_loc = st.text_input("Preferred Location")
            if st.form_submit_button("Save Client"):
                supabase.table('client_leads').insert({
                    "client_name": c_name, "contact": c_contact, 
                    "budget": c_budget, "req_location": c_loc, "added_by": user_name
                }).execute()
                st.success("Client Saved!")

    # --- 9. VIEW HISTORY ---
    elif menu == "📋 View History":
        t1, t2 = st.tabs(["Houses", "Clients"])
        with t1:
            st.dataframe(pd.DataFrame(supabase.table('house_inventory').select("*").execute().data), use_container_width=True)
        with t2:
            st.dataframe(pd.DataFrame(supabase.table('client_leads').select("*").execute().data), use_container_width=True)

    # --- 10. EDIT/DELETE BY ID ---
    elif menu == "🛠️ Edit/Delete (By ID)":
        target = st.radio("Table", ["house_inventory", "client_leads"], horizontal=True)
        s_id = st.number_input("Enter ID", min_value=1, step=1)
        if st.button("Search"):
            res = supabase.table(target).select("*").eq("id", s_id).execute()
            if res.data:
                st.write(res.data[0])
                if st.button("Delete Permanently"):
                    supabase.table(target).delete().eq("id", s_id).execute()
                    st.warning("Deleted!")
            else: st.error("Not Found")

    # --- 11. SEARCH & PDF ---
    elif menu == "🔍 Search & PDF":
        search = st.text_input("Search Location/Status")
        data = supabase.table('house_inventory').select("*").execute()
        df = pd.DataFrame(data.data)
        if search: df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
        st.dataframe(df, use_container_width=True)
        if st.button("Download PDF Report"):
            st.download_button("Download Now", generate_pdf(df, "Deewary Inventory Report"), "report.pdf")

else:
    st.warning("Please Enter Code.")
