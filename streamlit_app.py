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

# Custom CSS for Clean UI
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stButton>button {width: 100%; border-radius: 5px; height: 2em;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. PDF GENERATION FUNCTION ---
def generate_pdf(df, title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.ln(10)
    # Adding Table Headers
    pdf.cell(10, 10, "ID", 1)
    pdf.cell(40, 10, "Owner/Client", 1)
    pdf.cell(60, 10, "Location", 1)
    pdf.cell(30, 10, "Beds/Type", 1)
    pdf.cell(30, 10, "Rent/Budget", 1)
    pdf.ln()
    
    for i, row in df.iterrows():
        pdf.cell(10, 10, str(row.get('id', i)), 1)
        name = str(row.get('owner_name', row.get('client_name', 'N/A')))[:15]
        pdf.cell(40, 10, name, 1)
        loc = str(row.get('location', row.get('req_location', 'N/A')))[:25]
        pdf.cell(60, 10, loc, 1)
        beds = str(row.get('beds', row.get('req_portion', 'N/A')))
        pdf.cell(30, 10, beds, 1)
        val = str(row.get('rent', row.get('budget', '0')))
        pdf.cell(30, 10, val, 1)
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 4. HEADER ---
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
        "🏠 Ghar ki Entry (Owners)", 
        "👤 Client ki Entry (Tenants)", 
        "📋 House History (Edit/Delete)",
        "👥 Client History (Edit/Delete)",
        "🔍 Search & Print PDF"
    ])

    # --- 6. GHAR KI ENTRY ---
    if menu == "🏠 Ghar ki Entry (Owners)":
        st.subheader("🏡 Naye Ghar ki Entry")
        with st.form("house_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                o_name = st.text_input("Owner ka Naam")
                o_contact = st.text_input("Contact Number")
                loc = st.text_input("Location / Address")
                portion = st.selectbox("Portion", ["Full House", "Ground Floor", "First Floor", "Shop", "Office"])
            with col2:
                beds = st.selectbox("Bedrooms (Beds)", ["1", "2", "3", "4", "5", "6+", "N/A"])
                rent = st.number_input("Demand Rent (PKR)", min_value=0)
                size = st.text_input("Size (Marla/Kanal)")
                status = st.selectbox("Status", ["Available", "Rent Out"])
            if st.form_submit_button("Save House Record"):
                payload = {"owner_name": o_name, "contact": o_contact, "location": loc, "portion": portion, "beds": beds, "rent": rent, "size": size, "status": status, "added_by": user_name}
                supabase.table('house_inventory').insert(payload).execute()
                st.success(f"Record saved by {user_name}!")

    # --- 7. HOUSE HISTORY (Table Style with Edit/Delete) ---
    elif menu == "📋 House History (Edit/Delete)":
        st.subheader("🏠 Registered Houses")
        res = supabase.table('house_inventory').select("*").order('id').execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            cols = st.columns([0.5, 1.5, 2, 1, 1, 1, 1])
            cols[0].write("**ID**")
            cols[1].write("**Owner**")
            cols[2].write("**Location**")
            cols[3].write("**Beds**")
            cols[4].write("**Rent**")
            cols[5].write("**Update**")
            cols[6].write("**Delete**")
            st.divider()

            for i, row in df.iterrows():
                c = st.columns([0.5, 1.5, 2, 1, 1, 1, 1])
                c[0].write(row['id'])
                c[1].write(row['owner_name'])
                c[2].write(row['location'])
                c[3].write(row['beds'])
                c[4].write(row['rent'])
                
                # Simple Edit (Toggle Status)
                new_st = "Rent Out" if row['status'] == "Available" else "Available"
                if c[5].button("🔄", key=f"up_{row['id']}"):
                    supabase.table('house_inventory').update({"status": new_st}).eq("id", row['id']).execute()
                    st.rerun()
                
                # Delete
                if c[6].button("🗑️", key=f"del_{row['id']}"):
                    supabase.table('house_inventory').delete().eq("id", row['id']).execute()
                    st.rerun()

    # --- 8. CLIENT HISTORY ---
    elif menu == "👥 Client History (Edit/Delete)":
        st.subheader("👥 Client Requirements")
        res = supabase.table('client_leads').select("*").order('id').execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            for i, row in df.iterrows():
                with st.expander(f"👤 {row['client_name']} - {row['req_location']}"):
                    st.write(f"Contact: {row['contact']} | Budget: {row['budget']}")
                    if st.button(f"🗑️ Delete ID {row['id']}", key=f"cdel_{row['id']}"):
                        supabase.table('client_leads').delete().eq("id", row['id']).execute()
                        st.rerun()

    # --- 9. SEARCH & PRINT PDF ---
    elif menu == "🔍 Search & Print PDF":
        st.subheader("🔍 Master Search & Reports")
        search_query = st.text_input("Search Location, Owner, or Beds...")
        
        t1, t2 = st.tabs(["🏠 Houses", "👥 Clients"])
        with t1:
            res_h = supabase.table('house_inventory').select("*").execute()
            df_h = pd.DataFrame(res_h.data)
            if search_query:
                df_h = df_h[df_h.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
            st.dataframe(df_h, use_container_width=True)
            if not df_h.empty:
                pdf_h = generate_pdf(df_h, "Deewary House Inventory Report")
                st.download_button("📥 Download House List (PDF)", pdf_h, "houses.pdf", "application/pdf")

        with t2:
            res_c = supabase.table('client_leads').select("*").execute()
            df_c = pd.DataFrame(res_c.data)
            if search_query:
                df_c = df_c[df_c.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
            st.dataframe(df_c, use_container_width=True)
            if not df_c.empty:
                pdf_c = generate_pdf(df_c, "Deewary Client Leads Report")
                st.download_button("📥 Download Client List (PDF)", pdf_c, "clients.pdf", "application/pdf")

else:
    st.warning("Please enter Access Code 'admin786' to continue.")

st.divider()
st.caption(f"© {datetime.now().year} Deewary.com | Property Management System")
