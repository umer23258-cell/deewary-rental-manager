import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# --- 1. SUPABASE SETUP ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Deewary Property Manager", layout="wide", page_icon="🏢")

# Hide Streamlit UI
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}</style>", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS (Delete & Edit) ---
def delete_record(table_name, record_id):
    supabase.table(table_name).delete().eq("id", record_id).execute()
    st.success(f"Record ID {record_id} deleted!")
    st.rerun()

# --- 4. HEADER ---
st.markdown("""
    <div style="text-align: center; background-color: #1E1E1E; padding: 20px; border-radius: 15px; border: 2px solid #FF4B4B;">
        <h1 style="color: #FF4B4B; margin: 0; font-family: 'Arial Black';">DEEWARY PROPERTY MANAGER</h1>
        <p style="color: white; letter-spacing: 2px;">MANAGEMENT PORTAL</p>
    </div>
""", unsafe_allow_html=True)

# --- 5. SIDEBAR ---
st.sidebar.title("🔐 Staff Access")
user_name = st.sidebar.selectbox("Apna Naam Select Karen", ["Anas", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Access Code", type="password")

if pwd == "admin786":
    menu = st.sidebar.radio("KAAM SELECT KAREN", [
        "🏠 Dashboard",
        "--- NAYI ENTRY ---",
        "🏠 Ghar ki Entry (Owners)", 
        "👤 Client ki Entry (New)",
        "💬 Client in Discussion",
        "⏳ Deal Pending Entry",
        "✅ Deal Done Entry",
        "--- RECORDS & HISTORY ---",
        "📋 Gharon ki History",
        "👥 New Clients History",
        "🗣️ Discussion History",
        "📂 Pending Deals History",
        "💰 Done Deals History"
    ])

    # --- 6. GHAR KI HISTORY (Edit/Delete Example) ---
    if menu == "📋 Gharon ki History":
        st.subheader("📋 Registered Houses")
        res = supabase.table('house_inventory').select("*").order('id').execute()
        if res.data:
            df = pd.DataFrame(res.data)
            for _, row in df.iterrows():
                with st.expander(f"ID: {row['id']} - {row['owner_name']} ({row['location']})"):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"**Rent:** {row['rent']} | **Beds:** {row['beds']} | **Gas:** {row['gas']}")
                    with col2:
                        if st.button("📝 Edit", key=f"edit_h_{row['id']}"):
                            st.info("Niche form mein changes kar ke update dabayein.")
                            st.session_state.edit_id = row['id']
                    with col3:
                        if st.button("🗑️ Delete", key=f"del_h_{row['id']}"):
                            delete_record('house_inventory', row['id'])
        else:
            st.warning("Koi record nahi mila.")

    # --- 7. NEW CLIENTS HISTORY ---
    elif menu == "👥 New Clients History":
        st.subheader("👥 Client Requirements")
        res = supabase.table('client_leads').select("*").order('id').execute()
        if res.data:
            df = pd.DataFrame(res.data)
            for _, row in df.iterrows():
                with st.expander(f"ID: {row['id']} - {row['client_name']}"):
                    c1, c2 = st.columns([4, 1])
                    with c1: st.write(f"**Contact:** {row['contact']} | **Budget:** {row['budget']}")
                    with c2:
                        if st.button("🗑️ Delete", key=f"del_c_{row['id']}"):
                            delete_record('client_leads', row['id'])

    # --- 8. DISCUSSION HISTORY ---
    elif menu == "🗣️ Discussion History":
        st.subheader("🗣️ Conversations")
        res = supabase.table('client_discussions').select("*").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            for _, row in df.iterrows():
                with st.expander(f"ID: {row['id']} - {row['client_name']}"):
                    st.write(f"**Note:** {row['notes']}")
                    if st.button("🗑️ Delete", key=f"del_d_{row['id']}"):
                        delete_record('client_discussions', row['id'])

    # --- 9. PENDING DEALS HISTORY ---
    elif menu == "📂 Pending Deals History":
        st.subheader("📂 Token/Pending Records")
        res = supabase.table('deals_pending').select("*").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            for _, row in df.iterrows():
                with st.expander(f"ID: {row['id']} - {row['client_name']}"):
                    st.write(f"**Token:** {row['token_amount']} | **Date:** {row['expected_date']}")
                    if st.button("🗑️ Delete", key=f"del_p_{row['id']}"):
                        delete_record('deals_pending', row['id'])

    # --- 10. DONE DEALS HISTORY ---
    elif menu == "💰 Done Deals History":
        st.subheader("💰 Closed Deals")
        res = supabase.table('deals_done').select("*").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            for _, row in df.iterrows():
                with st.expander(f"ID: {row['id']} - {row['client_name']} to {row['owner_name']}"):
                    st.write(f"**Rent:** {row['final_rent']} | **Commission:** {row['commission']}")
                    if st.button("🗑️ Delete", key=f"del_done_{row['id']}"):
                        delete_record('deals_done', row['id'])

    # Yahan baqi Nayi Entry ke forms pehle walay hi rahenge...
    elif menu == "🏠 Ghar ki Entry (Owners)":
        # (Purana Ghar Entry Form)
        pass

else:
    if pwd != "": st.error("Access Code Ghalat Hai!")

st.divider()
st.caption(f"© {datetime.now().year} Deewary.com | System Active")
