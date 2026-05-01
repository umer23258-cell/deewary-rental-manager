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

# Custom CSS
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .sidebar-header { color: #FF4B4B; font-weight: bold; font-size: 18px; margin-top: 20px; border-bottom: 1px solid #444; }
    .stButton>button { width: 100%; background-color: #2c3e50; color: white; border-radius: 5px; }
    .stButton>button:hover { border-color: #FF4B4B; color: #FF4B4B; }
    </style>
""", unsafe_allow_html=True)

# --- 3. PDF FUNCTION (Updated for multiple reports) ---
def generate_pdf(df, title):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, txt=title, ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Helvetica", 'B', 10)
    pdf.set_fill_color(200, 200, 200)
    
    # Dynamic columns based on dataframe
    cols = df.columns.tolist()
    for col in cols:
        pdf.cell(35, 10, str(col)[:10], 1, 0, 'C', 1)
    pdf.ln()
    
    pdf.set_font("Helvetica", size=9)
    for _, row in df.iterrows():
        for col in cols:
            text = str(row[col]).encode('latin-1', 'ignore').decode('latin-1')
            pdf.cell(35, 10, text[:20], 1)
        pdf.ln()
    return pdf.output(dest='S')

# --- 4. HEADER ---
st.markdown("""
    <div style="text-align: center; background-color: #2c3e50; padding: 20px; border-radius: 15px;">
        <h1 style="color: white; margin: 0;">DEEWARY PROPERTY MANAGER</h1>
        <p style="color: #FF4B4B; font-weight: bold;">OFFICIAL DATABASE SYSTEM</p>
    </div>
""", unsafe_allow_html=True)

# --- 5. SIDEBAR LOGIN ---
st.sidebar.title("🔐 Access Control")
user_name = st.sidebar.selectbox("Personnel", ["Anas", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "admin786":
    # Sidebar Navigation
    st.sidebar.markdown('<p class="sidebar-header">📥 DATA ENTRY</p>', unsafe_allow_html=True)
    if st.sidebar.button("🏠 Register Property"): st.session_state.menu = "property_entry"
    if st.sidebar.button("👤 Register Client"): st.session_state.menu = "client_entry"
    if st.sidebar.button("⏳ Pending Tasks"): st.session_state.menu = "pending_entry"
    if st.sidebar.button("📍 Site Visit Log"): st.session_state.menu = "visit_entry"
        
    st.sidebar.markdown('<p class="sidebar-header">📊 RECORDS & REPORTS</p>', unsafe_allow_html=True)
    if st.sidebar.button("📋 View All Records"): st.session_state.menu = "history"
    if st.sidebar.button("🛠️ Manage Records"): st.session_state.menu = "manage"
    if st.sidebar.button("🔍 Search & PDF"): st.session_state.menu = "search"

    if "menu" not in st.session_state: st.session_state.menu = "history"

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

    # --- 8. NEW: PENDING TASKS FORM ---
    elif st.session_state.menu == "pending_entry":
        st.subheader("⏳ Add Pending Task/Follow-up")
        with st.form("p_form", clear_on_submit=True):
            task_desc = st.text_area("Task Description")
            c1, c2 = st.columns(2)
            with c1:
                due_date = st.date_input("Due Date")
                priority = st.selectbox("Priority", ["Normal", "High", "Urgent"])
            with c2:
                related_to = st.text_input("Client/Owner Name (Reference)")
            
            if st.form_submit_button("Add Task"):
                supabase.table('pending_tasks').insert({
                    "task": task_desc, "due_date": str(due_date), 
                    "priority": priority, "reference": related_to, 
                    "status": "Pending", "added_by": user_name
                }).execute()
                st.success("Task Added to Pending List!")

    # --- 9. NEW: SITE VISIT LOG ---
    elif st.session_state.menu == "visit_entry":
        st.subheader("📍 Record Site Visit")
        with st.form("v_form", clear_on_submit=True):
            v_client = st.text_input("Client Name")
            v_property = st.text_input("Property Visited (Address/ID)")
            v_date = st.date_input("Visit Date")
            v_feedback = st.text_area("Client Feedback")
            v_status = st.selectbox("Outcome", ["Interested", "Not Interested", "Token Given", "Thinking"])
            
            if st.form_submit_button("Save Visit Record"):
                supabase.table('site_visits').insert({
                    "client_name": v_client, "property_details": v_property,
                    "visit_date": str(v_date), "feedback": v_feedback,
                    "outcome": v_status, "agent": user_name
                }).execute()
                st.success("Visit Logged Successfully!")

    # --- 10. HISTORY (Updated with new tabs) ---
    elif st.session_state.menu == "history":
        st.subheader("📋 System Database")
        t1, t2, t3, t4 = st.tabs(["🏠 Properties", "👥 Clients", "⏳ Tasks", "📍 Visits"])
        
        with t1:
            data = supabase.table('house_inventory').select("*").execute()
            st.dataframe(pd.DataFrame(data.data), use_container_width=True)
        with t2:
            data = supabase.table('client_leads').select("*").execute()
            st.dataframe(pd.DataFrame(data.data), use_container_width=True)
        with t3:
            data = supabase.table('pending_tasks').select("*").execute()
            st.dataframe(pd.DataFrame(data.data), use_container_width=True)
        with t4:
            data = supabase.table('site_visits').select("*").execute()
            st.dataframe(pd.DataFrame(data.data), use_container_width=True)

    # --- 11. MANAGE & DELETE ---
    elif st.session_state.menu == "manage":
        st.subheader("🛠️ Edit or Delete Records")
        tbl = st.radio("Select Table", ["house_inventory", "client_leads", "pending_tasks", "site_visits"], horizontal=True)
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
                if "found" in st.session_state: del st.session_state.found

    # --- 12. SEARCH & PDF ---
    elif st.session_state.menu == "search":
        st.subheader("🔍 Search & Download Report")
        mode = st.radio("Report For", ["house_inventory", "client_leads", "pending_tasks", "site_visits"])
        q = st.text_input("Search Anything...")
        res = supabase.table(mode).select("*").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            if q:
                df = df[df.astype(str).apply(lambda x: x.str.contains(q, case=False)).any(axis=1)]
            st.dataframe(df, use_container_width=True)
            if st.button("Download Professional PDF"):
                pdf_bytes = generate_pdf(df, f"DEEWARY {mode.upper()} REPORT")
                st.download_button("📥 Click to Download", pdf_bytes, f"{mode}_report.pdf", "application/pdf")

else:
    if pwd != "":
        st.error("Access Denied")

st.divider()
st.caption(f"© {datetime.now().year} Deewary.com | Data Protection Active")
