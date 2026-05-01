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

# --- 3. UPDATED PDF FUNCTION (Proper Table Format) ---
def generate_pdf(df, title):
    pdf = FPDF(orientation='L', unit='mm', format='A4') # Landscape format taake table fit aaye
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=title, ln=True, align='C')
    pdf.ln(5)
    
    # Table Header Settings
    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(200, 200, 200) # Gray background for header
    
    # Columns Width (Adjusted for A4 Landscape)
    col_width = [15, 40, 60, 25, 25, 30, 30, 40]
    headers = ["ID", "Owner", "Location", "Portion", "Beds", "Rent", "Size", "Status"]
    
    for i in range(len(headers)):
        pdf.cell(col_width[i], 10, headers[i], 1, 0, 'C', 1)
    pdf.ln()
    
    # Table Body
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

# --- 4. HEADER ---
st.markdown("""
    <div style="text-align: center; background-color: #1E1E1E; padding: 20px; border-radius: 15px; border: 2px solid #FF4B4B;">
        <h1 style="color: #FF4B4B; margin: 0;">DEEWARY PROPERTY MANAGER</h1>
        <p style="color: white;">OWNER INVENTORY & CLIENT DATABASE</p>
    </div>
""", unsafe_allow_html=True)

# --- LOGIN & MENU (Same as before) ---
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

    # (Entries and History sections same as previous code)
    # ... [Code for Ghar Entry, Client Entry, History, and Manage Records] ...

    # --- 9. SEARCH & PRINT (UPDATED) ---
    if menu == "🔍 Search & Print PDF":
        st.subheader("🔍 Search & Download Table Report")
        search = st.text_input("Search Location, Owner or Status")
        
        res = supabase.table('house_inventory').select("*").execute()
        df = pd.DataFrame(res.data)
        
        if search and not df.empty:
            df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
        
        st.write(f"### Total Records Found: {len(df)}")
        st.dataframe(df, use_container_width=True)
        
        if not df.empty:
            if st.button("Generate Professional Table PDF"):
                pdf_bytes = generate_pdf(df, "DEEWARY PROPERTY INVENTORY REPORT")
                st.download_button(
                    label="📥 Download Now (Professional PDF)",
                    data=pdf_bytes,
                    file_name=f"Deewary_Report_{datetime.now().strftime('%d-%m-%y')}.pdf",
                    mime="application/pdf"
                )

else:
    st.warning("Access Code 'admin786' istemal karen.")
