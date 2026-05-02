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

# Hide Streamlit UI (Aapka Style)
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# --- 3. PDF FUNCTION (Original) ---
def generate_pdf(df, title):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, txt=title, ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Helvetica", 'B', 10)
    pdf.set_fill_color(200, 200, 200)
    col_width = [15, 40, 60, 25, 25, 30, 30, 52]
    headers = ["ID", "Name", "Location", "Type", "Beds", "Rent", "Size", "Status"]
    for i in range(len(headers)):
        pdf.cell(col_width[i], 10, headers[i], 1, 0, 'C', 1)
    pdf.ln()
    pdf.set_font("Helvetica", size=9)
    for index, row in df.iterrows():
        name = str(row.get('owner_name', row.get('client_name', '')))[:18]
        loc = str(row.get('location', row.get('req_location', '')))[:25]
        vals = [str(row.get('id', '')), name, loc, str(row.get('portion', row.get('req_portion', ''))), 
                str(row.get('beds', row.get('beds_required', ''))), str(row.get('rent', row.get('budget', ''))), 
                str(row.get('size', row.get('marla', ''))), str(row.get('status', ''))]
        for i in range(len(vals)):
            clean_text = vals[i].encode('latin-1', 'ignore').decode('latin-1')
            pdf.cell(col_width[i], 10, clean_text, 1)
        pdf.ln()
    return pdf.output(dest='S')

# --- 4. HEADER (Original) ---
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
        "🏠 Dashboard",
        "--- NAYI ENTRY ---",
        "🏠 Ghar ki Entry (Owners)", 
        "👤 Client ki Entry (Tenants)", 
        "⏳ Deal Pending Entry",
        "✅ Deal Done Entry",
        "--- RECORDS & HISTORY ---",
        "📋 Gharon ki History",
        "👥 Clients ki History",
        "📂 Pending Deals History",
        "💰 Done Deals History",
        "🛠️ Manage & Edit",
        "🔍 Search & Print PDF"
    ])

    # --- 6. DASHBOARD ---
    if menu == "🏠 Dashboard":
        st.subheader(f"📊 Office Stats - {user_name}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Properties", len(supabase.table('house_inventory').select("id").execute().data))
        c2.metric("Total Clients", len(supabase.table('client_leads').select("id").execute().data))
        c3.metric("System Status", "Active")

    # --- 7. GHAR KI ENTRY (With Gas, Water, Elec, Time) ---
    elif menu == "🏠 Ghar ki Entry (Owners)":
        st.subheader("🏡 Naye Ghar ya Shop ki Detail")
        with st.form("house_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                o_name = st.text_input("Owner ka Naam")
                o_contact = st.text_input("Owner Contact")
                loc = st.text_input("Location / Address")
                portion = st.selectbox("Portion", ["Full House", "Ground Floor", "First Floor", "Basement", "Shop", "Office"])
                size = st.text_input("Size (Marla/Kanal)")
            with col2:
                beds = st.selectbox("Bedrooms", ["1", "2", "3", "4", "5", "6+", "N/A"])
                rent = st.number_input("Demand Rent (PKR)", min_value=0)
                v_time = st.text_input("Visit Time")
                gas = st.radio("Gas?", ["Yes", "No"], horizontal=True)
                water = st.radio("Water?", ["Yes", "No"], horizontal=True)
                elec = st.radio("Electricity?", ["Yes", "No"], horizontal=True)
            
            other = st.text_area("Other Details")
            if st.form_submit_button("Save House Record"):
                payload = {
                    "owner_name": o_name, "contact": o_contact, "location": loc, 
                    "portion": portion, "beds": beds, "rent": rent, "size": size, 
                    "gas": gas, "water": water, "electricity": elec, "visit_time": v_time,
                    "status": "Available", "details": other, "added_by": user_name
                }
                supabase.table('house_inventory').insert(payload).execute()
                st.success("House Saved!")

    # --- 8. HISTORY SECTIONS ---
    elif menu == "📋 Gharon ki History":
        st.subheader("📋 Gharon ka Record")
        res = supabase.table('house_inventory').select("*").execute()
        if res.data: st.dataframe(pd.DataFrame(res.data), use_container_width=True)

    elif menu == "📂 Pending Deals History":
        st.subheader("⏳ Pending Deals")
        res = supabase.table('deals_pending').select("*").execute()
        if res.data: st.dataframe(pd.DataFrame(res.data), use_container_width=True)

    elif menu == "💰 Done Deals History":
        st.subheader("✅ Closed Deals")
        res = supabase.table('deals_done').select("*").execute()
        if res.data: st.dataframe(pd.DataFrame(res.data), use_container_width=True)

    # (Yahan baqi forms (Client Entry, Pending/Done Entry) bhi isi pattern par add honge)

else:
    if pwd != "":
        st.error("Access Code Ghalat Hai!")

st.divider()
st.caption(f"© {datetime.now().year} Deewary.com | System Active")
