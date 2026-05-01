import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
import plotly.express as px
from fpdf import FPDF
import io

# --- 1. SUPABASE SETUP ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Deewary CRM", layout="wide", page_icon="🏢")

# Hide Streamlit UI
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# --- 3. DATA HELPERS ---
def get_data(table):
    try:
        res = supabase.table(table).select("*").execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except: return pd.DataFrame()

# --- 4. HEADER ---
st.markdown("""
    <div style="text-align: center; background-color: #1E1E1E; padding: 20px; border-radius: 15px; border: 2px solid #FF4B4B;">
        <h1 style="color: #FF4B4B; margin: 0; font-family: 'Arial Black';">DEEWARY PROPERTY MANAGER</h1>
        <p style="color: white; letter-spacing: 2px;">STAFF PANEL: ENTRIES & HISTORY</p>
    </div>
""", unsafe_allow_html=True)

# --- 5. STAFF LOGIN ---
st.sidebar.title("🔐 Staff Access")
user_name = st.sidebar.selectbox("Apna Naam Select Karen", ["Anas", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "admin786":
    # Sidebar ko do hisson mein taqseem kiya hai
    st.sidebar.markdown("### 📝 DATA ENTRY")
    entry_menu = st.sidebar.radio("Nayi Entry Karen:", [
        "🏠 Ghar ki Entry", 
        "👤 Client ki Entry", 
        "🤝 Deal Close Karen"
    ])

    st.sidebar.divider()
    
    st.sidebar.markdown("### 📜 RECORDS & PROGRESS")
    history_menu = st.sidebar.radio("History Dekhen:", [
        "📊 Daily Dashboard",
        "📋 Full Inventory History",
        "⏳ Pending Deals List",
        "✅ Done Deals History"
    ])

    # --- 6. DATA ENTRY LOGIC ---
    if entry_menu == "🏠 Ghar ki Entry":
        st.subheader("🏡 Naye Ghar ya Shop ki Detail")
        with st.form("h_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                o_name = st.text_input("Owner Name")
                loc = st.text_input("Location")
            with col2:
                rent = st.number_input("Demand Rent", min_value=0)
                status = st.selectbox("Status", ["Available", "Rent Out"])
            if st.form_submit_button("Save Property"):
                supabase.table('house_inventory').insert({"owner_name": o_name, "location": loc, "rent": rent, "status": status, "added_by": user_name}).execute()
                st.success("Ghar ka record save ho gaya!")

    elif entry_menu == "👤 Client ki Entry":
        st.subheader("👤 Client Requirement Darj Karen")
        with st.form("c_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                c_name = st.text_input("Client Name")
                req = st.text_input("Required Location")
            with col2:
                budget = st.number_input("Budget", min_value=0)
            if st.form_submit_button("Save Client"):
                supabase.table('client_leads').insert({"client_name": c_name, "req_location": req, "budget": budget, "added_by": user_name}).execute()
                st.success("Client ki requirement save ho gayi!")

    elif entry_menu == "🤝 Deal Close Karen":
        st.subheader("🤝 Nayi Deal (Pending ya Done) darj karen")
        with st.form("d_form", clear_on_submit=True):
            d1, d2 = st.columns(2)
            with d1:
                cl_name = st.text_input("Client for Deal")
                h_id = st.text_input("House ID / Ref")
            with d2:
                d_status = st.selectbox("Deal Status", ["Pending", "Done"])
                d_amt = st.number_input("Amount", min_value=0)
            if st.form_submit_button("Submit Deal"):
                supabase.table('deals').insert({"client_name": cl_name, "house_id": h_id, "deal_status": d_status, "amount": d_amt, "staff_name": user_name, "date": str(datetime.now().date())}).execute()
                st.success(f"Deal record ({d_status}) save ho gaya!")

    # --- 7. HISTORY & DASHBOARD LOGIC (Ye Niche Nazar Aayenge) ---
    st.markdown("---") # Visual separator

    if history_menu == "📊 Daily Dashboard":
        st.subheader("🚀 Staff Daily Progress Dashboard")
        df_h = get_data('house_inventory')
        df_d = get_data('deals')
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Properties", len(df_h))
        m2.metric("Pending Deals", len(df_d[df_d['deal_status']=='Pending']) if not df_d.empty else 0)
        m3.metric("Done Deals", len(df_d[df_d['deal_status']=='Done']) if not df_d.empty else 0)
        
        if not df_h.empty:
            fig = px.bar(df_h.groupby('added_by').size().reset_index(name='Count'), x='added_by', y='Count', title="Kaunsa Staff Kitni Entry Kar Raha Hai?", color_discrete_sequence=['#FF4B4B'])
            st.plotly_chart(fig, use_container_width=True)

    elif history_menu == "📋 Full Inventory History":
        st.subheader("📋 Tamam Gharon ka Record")
        st.dataframe(get_data('house_inventory'), use_container_width=True)

    elif history_menu == "⏳ Pending Deals List":
        st.subheader("⏳ Pending Deals (Jinpar kaam chal raha hai)")
        df_d = get_data('deals')
        if not df_d.empty:
            st.dataframe(df_d[df_d['deal_status'] == 'Pending'], use_container_width=True)
        else: st.info("Koi Pending deal nahi hai.")

    elif history_menu == "✅ Done Deals History":
        st.subheader("✅ Done Deals (Closed Deals History)")
        df_d = get_data('deals')
        if not df_d.empty:
            st.dataframe(df_d[df_d['deal_status'] == 'Done'], use_container_width=True)
        else: st.info("Abhi tak koi deal close nahi hui.")

else:
    if pwd != "": st.error("Access Code Ghalat Hai!")

st.divider()
st.caption(f"© {datetime.now().year} Deewary.com | Active Session: {user_name}")
