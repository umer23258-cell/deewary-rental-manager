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
st.set_page_config(page_title="Deewary | Property Portal", layout="wide", page_icon="🏡")

# --- ZAMEEN STYLE CSS ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Header Style */
    .main-header {
        background-color: #28a745;
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Zameen Green Button */
    div.stButton > button {
        background-color: #28a745 !important;
        color: white !important;
        border-radius: 5px !important;
        border: none !important;
        width: 100%;
        font-weight: bold;
    }
    
    /* Search Box Look */
    .search-container {
        background-color: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        margin-top: -50px;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #1a1a1a;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- PDF GENERATOR ---
def generate_pdf(df, title):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    
    # Simple Table logic
    pdf.set_font("Arial", 'B', 10)
    cols = list(df.columns)[:8] # Pehle 8 columns
    for col in cols:
        pdf.cell(35, 10, str(col).upper(), 1)
    pdf.ln()
    
    pdf.set_font("Arial", size=9)
    for _, row in df.iterrows():
        for col in cols:
            val = str(row[col])[:20]
            pdf.cell(35, 10, val.encode('latin-1', 'ignore').decode('latin-1'), 1)
        pdf.ln()
    return pdf.output(dest='S')

# --- UI HEADER ---
st.markdown('<div class="main-header"><h1>DEEWARY PROPERTY PORTAL</h1><p>Pakistan\'s Professional Inventory System</p></div>', unsafe_allow_html=True)

# --- LOGIN ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/609/609803.png", width=100)
st.sidebar.title("🔐 Staff Portal")
user_name = st.sidebar.selectbox("User", ["Anas", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "admin786":
    menu = st.sidebar.selectbox("MAIN MENU", [
        "🔍 Search Properties",
        "🏠 Add New Property", 
        "👤 Add New Client", 
        "📋 Database View",
        "🛠️ Manage Records"
    ])

    # --- 1. SEARCH INTERFACE (Zameen Style) ---
    if menu == "🔍 Search Properties":
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            city_search = st.text_input("Location / Society", placeholder="e.g. DHA Phase 6")
        with col2:
            type_search = st.selectbox("Property Type", ["All", "Full House", "Portion", "Shop", "Office"])
        with col3:
            st.write("##")
            do_search = st.button("FIND NOW")
        st.markdown('</div>', unsafe_allow_html=True)

        # Search Results
        res = supabase.table('house_inventory').select("*").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            if city_search:
                df = df[df['location'].str.contains(city_search, case=False, na=False)]
            if type_search != "All":
                df = df[df['portion'] == type_search]
            
            st.subheader(f"Found {len(df)} Results")
            st.dataframe(df, use_container_width=True)
            
            if st.button("Download Report (PDF)"):
                pdf_out = generate_pdf(df, "DEEWARY SEARCH RESULTS")
                st.download_button("Click to Download", pdf_out, "Report.pdf", "application/pdf")

    # --- 2. ADD PROPERTY ---
    elif menu == "🏠 Add New Property":
        st.subheader("📝 List New Property (Owner)")
        with st.form("house_form"):
            c1, c2 = st.columns(2)
            with c1:
                o_name = st.text_input("Owner Name")
                o_num = st.text_input("Contact Number")
                loc = st.text_input("Exact Address")
            with c2:
                portion = st.selectbox("Type", ["Full House", "Ground Floor", "First Floor", "Basement", "Shop", "Office"])
                beds = st.selectbox("Beds", ["1","2","3","4","5","6+"])
                rent = st.number_input("Demand Rent", min_value=0)
            
            details = st.text_area("Extra Details (Facilities etc.)")
            if st.form_submit_button("PUBLISH PROPERTY"):
                data = {"owner_name": o_name, "contact": o_num, "location": loc, "portion": portion, "beds": beds, "rent": rent, "details": details, "added_by": user_name}
                supabase.table('house_inventory').insert(data).execute()
                st.success("Property Added Successfully!")

    # --- 3. ADD CLIENT ---
    elif menu == "👤 Add New Client":
        st.subheader("🎯 Register Client Requirement")
        with st.form("client_form"):
            c1, c2 = st.columns(2)
            with c1:
                cl_name = st.text_input("Client Name")
                cl_cont = st.text_input("Contact")
                cl_loc = st.text_input("Required Area")
            with c2:
                cl_bug = st.number_input("Budget", min_value=0)
                cl_type = st.selectbox("Required Type", ["Full House", "Portion", "Flat", "Commercial"])
            
            if st.form_submit_button("SAVE CLIENT"):
                data = {"client_name": cl_name, "contact": cl_cont, "req_location": cl_loc, "budget": cl_bug, "req_portion": cl_type, "added_by": user_name}
                supabase.table('client_leads').insert(data).execute()
                st.balloons()

    # --- 4. DATABASE VIEW ---
    elif menu == "📋 Database View":
        tab1, tab2 = st.tabs(["🏠 All Houses", "👥 All Clients"])
        with tab1:
            data = supabase.table('house_inventory').select("*").execute()
            st.dataframe(pd.DataFrame(data.data), use_container_width=True)
        with tab2:
            data = supabase.table('client_leads').select("*").execute()
            st.dataframe(pd.DataFrame(data.data), use_container_width=True)

    # --- 5. MANAGE (EDIT/DELETE) ---
    elif menu == "🛠️ Manage Records":
        target = st.radio("Select Table", ["house_inventory", "client_leads"], horizontal=True)
        id_to_act = st.number_input("Enter ID to Delete/Update", min_value=1)
        
        if st.button("🗑️ DELETE RECORD"):
            supabase.table(target).delete().eq("id", id_to_act).execute()
            st.error(f"Record {id_to_act} Deleted.")
            st.rerun()

else:
    if pwd:
        st.error("Ghalat Code! Dobara koshish karen.")
    st.info("Please Login via Sidebar to access the system.")

st.divider()
st.caption(f"Deewary CMS v2.0 | Developed for {user_name} | {datetime.now().strftime('%Y')}")
