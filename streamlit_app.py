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

st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# --- 3. PDF FUNCTION ---
def generate_pdf(df, title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.ln(10)
    for i in range(len(df)):
        row = df.iloc[i]
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
        "📋 Full History (View Only)",
        "🛠️ Manage Records (Edit/Delete)", # Naya Dashboard
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
                beds = st.selectbox("Bedrooms (Beds)", ["1", "2", "3", "4", "5+", "N/A"])
                rent = st.number_input("Rent", min_value=0)
                size = st.text_input("Size (Marla)")
                status = st.selectbox("Status", ["Available", "Rent Out"])
            if st.form_submit_button("Save Record"):
                payload = {"owner_name": o_name, "contact": o_contact, "location": loc, "portion": portion, "beds": beds, "rent": rent, "size": size, "status": status, "added_by": user_name}
                supabase.table('house_inventory').insert(payload).execute()
                st.success("Record Saved!")

    # --- 7. FULL HISTORY (VIEW ONLY) ---
    elif menu == "📋 Full History (View Only)":
        st.subheader("📋 Tamam Records")
        t1, t2 = st.tabs(["Ghar/Shops", "Clients"])
        with t1:
            df_h = pd.DataFrame(supabase.table('house_inventory').select("*").execute().data)
            st.dataframe(df_h, use_container_width=True)
        with t2:
            df_c = pd.DataFrame(supabase.table('client_leads').select("*").execute().data)
            st.dataframe(df_c, use_container_width=True)

    # --- 8. MANAGE RECORDS (EDIT/DELETE BY ID) ---
    elif menu == "🛠️ Manage Records (Edit/Delete)":
        st.subheader("🛠️ Search by ID to Edit or Delete")
        target_table = st.radio("Select Table", ["house_inventory", "client_leads"], horizontal=True)
        search_id = st.number_input("Enter ID Number", min_value=1, step=1)
        
        if st.button("Find Record"):
            res = supabase.table(target_table).select("*").eq("id", search_id).execute()
            if res.data:
                record = res.data[0]
                st.write("---")
                st.write(f"**Current Data:** {record}")
                
                # Edit Section
                st.markdown("### Update Status")
                if target_table == "house_inventory":
                    new_val = st.selectbox("New Status", ["Available", "Rent Out"], index=0 if record['status'] == 'Available' else 1)
                    if st.button("Confirm Update"):
                        supabase.table(target_table).update({"status": new_val}).eq("id", search_id).execute()
                        st.success("Status Updated!")
                
                # Delete Section
                st.markdown("### Danger Zone")
                if st.button("🗑️ Permanently Delete Record"):
                    supabase.table(target_table).delete().eq("id", search_id).execute()
                    st.warning(f"Record ID {search_id} Deleted!")
            else:
                st.error("Is ID ka koi record nahi mila.")

    # --- 9. SEARCH & PRINT ---
    elif menu == "🔍 Search & Print PDF":
        search = st.text_input("Search (Location/Name/Contact)")
        res = supabase.table('house_inventory').select("*").execute()
        df = pd.DataFrame(res.data)
        if search and not df.empty:
            df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
        st.dataframe(df)
        if st.button("Download PDF"):
            pdf_bytes = generate_pdf(df, "Property Report")
            st.download_button("Download Now", pdf_bytes, "report.pdf")

else:
    st.warning("Access Code 'admin786' istemal karen.")

st.divider()
st.caption(f"© {datetime.now().year} Deewary.com | Manager: {user_name}")
                
