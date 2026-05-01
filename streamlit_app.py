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

# Hide Streamlit UI
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# --- 3. FUNCTIONS (PDF) ---
def generate_pdf(df, title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.ln(10)
    for i in range(len(df)):
        row = df.iloc[i]
        # Yahan beds bhi shamil kar diya hai report mein
        text = f"{i+1}. " + " | ".join([f"{col}: {row[col]}" for col in df.columns[:6]])
        pdf.multi_cell(0, 10, txt=text)
        pdf.ln(2)
    return pdf.output(dest='S').encode('latin-1')

# --- 4. HEADER ---
st.markdown("""
    <div style="text-align: center; background-color: #1E1E1E; padding: 20px; border-radius: 15px; border: 2px solid #FF4B4B;">
        <h1 style="color: #FF4B4B; margin: 0;">DEEWARY PROPERTY MANAGER</h1>
        <p style="color: white;">OWNER INVENTORY & CLIENT DATABASE</p>
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
            c1, c2 = st.columns(2)
            with c1:
                o_name = st.text_input("Owner Name")
                o_contact = st.text_input("Contact")
                loc = st.text_input("Location")
                portion = st.selectbox("Portion", ["Full House", "Ground Floor", "First Floor", "Shop"])
            with c2:
                # BEDS ka column yahan add kiya hai
                beds = st.selectbox("Bedrooms (Beds)", ["1", "2", "3", "4", "5+", "N/A"])
                rent = st.number_input("Rent", min_value=0)
                size = st.text_input("Size (Marla)")
                status = st.selectbox("Status", ["Available", "Rent Out"])
            if st.form_submit_button("Save Record"):
                payload = {
                    "owner_name": o_name, "contact": o_contact, "location": loc, 
                    "portion": portion, "beds": beds, "rent": rent, 
                    "size": size, "status": status, "added_by": user_name
                }
                supabase.table('house_inventory').insert(payload).execute()
                st.success("Data Saved!")

    # --- 7. HOUSE HISTORY (EDIT/DELETE) ---
    elif menu == "📋 House History (Edit/Delete)":
        res = supabase.table('house_inventory').select("*").execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            for index, row in df.iterrows():
                # Expander mein beds show honge
                with st.expander(f"📍 {row['location']} ({row.get('beds', 'N/A')} Beds) - {row['owner_name']}"):
                    col_e1, col_e2, col_e3 = st.columns([2, 1, 1])
                    new_status = col_e1.selectbox("Update Status", ["Available", "Rent Out"], key=f"status_{row['id']}", index=0 if row['status']=='Available' else 1)
                    if col_e2.button("Update", key=f"upd_{row['id']}"):
                        supabase.table('house_inventory').update({"status": new_status}).eq("id", row['id']).execute()
                        st.rerun()
                    if col_e3.button("🗑️ Delete", key=f"del_{row['id']}"):
                        supabase.table('house_inventory').delete().eq("id", row['id']).execute()
                        st.rerun()
            st.dataframe(df, use_container_width=True)

    # --- 8. CLIENT HISTORY ---
    elif menu == "👥 Client History (Edit/Delete)":
        res = supabase.table('client_leads').select("*").execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            for index, row in df.iterrows():
                with st.expander(f"👤 {row['client_name']} - {row['req_location']}"):
                    if st.button(f"🗑️ Delete Client {row['id']}", key=f"cdel_{row['id']}"):
                        supabase.table('client_leads').delete().eq("id", row['id']).execute()
                        st.rerun()
            st.dataframe(df, use_container_width=True)

    # --- 9. SEARCH & PRINT ---
    elif menu == "🔍 Search & Print PDF":
        search = st.text_input("Search by Location or Contact")
        t1, t2 = st.tabs(["Houses", "Clients"])
        
        with t1:
            data = supabase.table('house_inventory').select("*").execute()
            df_h = pd.DataFrame(data.data)
            if search: df_h = df_h[df_h.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
            st.dataframe(df_h)
            if st.button("Download House List PDF"):
                pdf_bytes = generate_pdf(df_h, "Deewary House Inventory")
                st.download_button("Download Now", pdf_bytes, "houses.pdf", "application/pdf")

        with t2:
            data_c = supabase.table('client_leads').select("*").execute()
            df_c = pd.DataFrame(data_c.data)
            if search: df_c = df_c[df_c.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
            st.dataframe(df_c)
            if st.button("Download Client List PDF"):
                pdf_bytes = generate_pdf(df_c, "Deewary Client Leads")
                st.download_button("Download Now", pdf_bytes, "clients.pdf", "application/pdf")

else:
    st.warning("Access Code 'admin786' istemal karen.")
