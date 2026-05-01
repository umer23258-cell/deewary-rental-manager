import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# --- 1. SUPABASE SETUP ---
# Ye secrets aapne Streamlit ki settings mein dalne hain
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. PAGE CONFIG & UI ---
st.set_page_config(page_title="Deewary Property Manager", layout="wide", page_icon="🏢")

# GitHub aur extra menus hide karne ke liye CSS
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 3. HEADER ---
st.markdown("""
    <div style="text-align: center; background-color: #1E1E1E; padding: 20px; border-radius: 15px; border: 2px solid #FF4B4B;">
        <h1 style="color: #FF4B4B; margin: 0; font-family: 'Arial Black';">DEEWARY PROPERTY MANAGER</h1>
        <p style="color: white; letter-spacing: 2px;">OWNER INVENTORY & CLIENT DATABASE</p>
    </div>
""", unsafe_allow_html=True)

# --- 4. STAFF LOGIN ---
st.sidebar.title("🔐 Staff Access")
user_name = st.sidebar.selectbox("Apna Naam Select Karen", ["Office Staff - 01", "Office Staff - 02", "Anas"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "deewary786":
    menu = st.sidebar.radio("KAAM SELECT KAREN", [
        "🏠 Ghar ki Entry (Owners)", 
        "👤 Client ki Entry (Tenants)", 
        "📊 Search & View Data"
    ])

    # --- 5. GHAR KI ENTRY (OWNERS) ---
    if menu == "🏠 Ghar ki Entry (Owners)":
        st.subheader("🏡 Naye Ghar ya Shop ki Detail Darj Karen")
        with st.form("house_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                o_name = st.text_input("Owner ka Naam")
                o_contact = st.text_input("Owner ka Contact Number")
                loc = st.text_input("Location / Address")
                size = st.text_input("Size (Marla/Kanal)")
                portion = st.selectbox("Portion", ["Full House", "Ground Floor", "First Floor", "Basement", "Shop", "Office"])
            
            with col2:
                rent = st.number_input("Demand Rent (PKR)", min_value=0)
                v_time = st.text_input("Visit Time (e.g. 10am to 6pm)")
                st.write("**Sahuliyat (Check Karen):**")
                c1, c2, c3 = st.columns(3)
                w = c1.checkbox("Pani")
                g = c2.checkbox("Gas")
                e = c3.checkbox("Bijli")
                status = st.selectbox("Status", ["Available", "Rent Out (Booked)"])

            other = st.text_area("Other Details (Extra info)")
            
            if st.form_submit_button("Save House Record"):
                payload = {
                    "owner_name": o_name, "contact": o_contact, "location": loc, "size": size,
                    "portion": portion, "rent": rent, "visit_time": v_time, "water": w,
                    "gas": g, "electricity": e, "status": status, "details": other, "added_by": user_name
                }
                supabase.table('house_inventory').insert(payload).execute()
                st.success("Ghar ka record Supabase mein save ho gaya!")
                st.balloons()

    # --- 6. CLIENT KI ENTRY (TENANTS) ---
    elif menu == "👤 Client ki Entry (Tenants)":
        st.subheader("👨‍👩‍👧‍👦 Client ki Requirement Register Karen")
        with st.form("client_form", clear_on_submit=True):
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                c_name = st.text_input("Client ka Naam")
                c_contact = st.text_input("Client ka Contact Number")
                c_loc = st.text_input("Kis Area mein ghar chahiye?")
                c_budget = st.number_input("Monthly Budget (PKR)", min_value=0)
            
            with c_col2:
                c_portion = st.selectbox("Requirement", ["Full House", "Portion", "Flat", "Shop", "Office"])
                c_family = st.text_input("Family Members (e.g. 5 People)")
                c_job = st.text_input("Job / Business Details")
            
            c_req = st.text_area("Other Requirements (e.g. Gas lazmi ho, Gari ki parking ho)")
            
            if st.form_submit_button("Save Client Lead"):
                payload = {
                    "client_name": c_name, "contact": c_contact, "req_location": c_loc,
                    "budget": c_budget, "req_portion": c_portion, "family": c_family,
                    "job": c_job, "requirements": c_req, "added_by": user_name
                }
                supabase.table('client_leads').insert(payload).execute()
                st.success("Client ki requirement save ho gayi hai!")

    # --- 7. VIEW DATA ---
    elif menu == "📊 Search & View Data":
        st.info("Niche dono tables ka data mojud hai.")
        
        st.write("### 🏠 House Inventory")
        res_h = supabase.table('house_inventory').select("*").execute()
        st.dataframe(pd.DataFrame(res_h.data), use_container_width=True)

        st.write("### 👥 Client Leads")
        res_c = supabase.table('client_leads').select("*").execute()
        st.dataframe(pd.DataFrame(res_c.data), use_container_width=True)

else:
    st.warning("Side menu mein Access Code daalein taake aap software use kar saken.")

st.divider()
st.caption(f"© {datetime.now().year} Deewary.com | Property Management System")