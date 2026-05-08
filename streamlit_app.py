import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
import io

# --- 1. CONNECTION ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("Secrets missing!")
    st.stop()

# --- 2. THEME & STYLING ---
st.set_page_config(page_title="Deewary Hub Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #05070A; color: #E0E0E0; }
    .metric-card { background: #1E2130; border-left: 5px solid #FF4B4B; padding: 15px; border-radius: 10px; text-align: center; }
    .stButton>button { background: linear-gradient(90deg, #FF4B4B, #FF8080); color: white; font-weight: bold; width: 100%; border-radius: 8px; }
    .img-box { border: 1px solid #333; border-radius: 10px; padding: 5px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIN ---
if "auth" not in st.session_state: st.session_state.update({"auth": False, "user": None, "role": None})
if not st.session_state.auth:
    st.title("🏠 DEEWARY HUB LOGIN")
    u = st.selectbox("User", ["Anas (Admin)", "Sawer Khan", "Tariq Hussain"])
    p = st.text_input("Pin", type="password")
    if st.button("Unlock"):
        if (u == "Anas (Admin)" and p == "admin786"):
            st.session_state.update({"auth": True, "user": "Anas", "role": "admin"})
            st.rerun()
        elif p in ["sawer123", "tariq123"]:
            st.session_state.update({"auth": True, "user": u, "role": "staff"})
            st.rerun()
        else: st.error("Wrong Pin!")
    st.stop()

# --- 4. DATA LOGIC ---
def fetch_data(table):
    try:
        res = supabase.table(table).select("*").order('created_at', desc=True).execute()
        return pd.DataFrame(res.data)
    except: return pd.DataFrame()

df_h = fetch_data('house_inventory')
df_c = fetch_data('client_leads')

tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📝 Add Entry", "📂 History & Edit"])

# --- TAB 1: DASHBOARD ---
with tab1:
    if not df_h.empty:
        avail = df_h[df_h['status'] == 'Available']
        rented = df_h[df_h['status'] == 'Rented']
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='metric-card'><h3>Available</h3><h2>{len(avail)}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-card'><h3>Rented Out</h3><h2>{len(rented)}</h2></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-card'><h3>Total Leads</h3><h2>{len(df_c)}</h2></div>", unsafe_allow_html=True)
    
    st.divider()
    st.subheader("📍 Quick Inventory View")
    if not df_h.empty:
        for _, row in df_h.head(5).iterrows():
            with st.container():
                col_i, col_t = st.columns([1, 4])
                with col_i:
                    imgs = row.get('image_urls', [])
                    if imgs: st.image(imgs[0], use_container_width=True)
                    else: st.info("No Pic")
                with col_t:
                    st.write(f"**ID: {row['id']}** | {row['location']} | {row['status']}")
                    st.caption(f"Rent: {row['rent']} | Added by: {row['added_by']}")
            st.markdown("---")

# --- TAB 2: ADD ENTRY (FIXED BUTTON) ---
with tab_entry:
    st.subheader("Add New Property")
    # Form ensures data only saves when button is clicked
    with st.form("house_form", clear_on_submit=True):
        c_a, c_b = st.columns(2)
        with c_a:
            on = st.text_input("Owner Name"); oc = st.text_input("Contact"); ol = st.text_input("Location")
            ornt = st.number_input("Rent", min_value=0)
        with c_b:
            om = st.text_input("Marla"); of = st.selectbox("Floor", ["Ground", "First", "Upper", "Full House"])
            ow = st.selectbox("Water", ["Yes", "Boring", "Line Water"]); og = st.selectbox("Gas", ["Yes", "No"])
        
        files = st.file_uploader("📸 Upload Photos (Max 6)", type=['jpg','png','jpeg'], accept_multiple_files=True)
        
        # Data saves ONLY when this button is pressed
        if st.form_submit_button("Save to Inventory"):
            urls = []
            if files:
                for f in files[:6]:
                    f_path = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{f.name}"
                    supabase.storage.from_('house_pics').upload(f_path, f.getvalue())
                    urls.append(supabase.storage.from_('house_pics').get_public_url(f_path))
            
            supabase.table('house_inventory').insert({
                "owner_name": on, "contact": oc, "location": ol, "rent": ornt,
                "marla": om, "floor": of, "water": ow, "gas": og,
                "image_urls": urls, "added_by": st.session_state.user, "status": "Available"
            }).execute()
            st.success("✅ Property Saved Successfully!"); st.rerun()

# --- TAB 3: HISTORY (EDIT & DELETE INCLUDED) ---
with tab3:
    db = st.selectbox("Select Table", ["house_inventory", "client_leads", "visit_logs"])
    data = fetch_data(db)
    
    if not data.empty:
        # Excel Export Fix
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
            data.to_excel(writer, index=False)
        st.download_button("📥 Download Excel", buf.getvalue(), f"{db}.xlsx")
        
        st.divider()
        st.subheader("🛠️ Management Actions")
        # Edit/Delete/RentOut functionality
        target_id = st.text_input("Enter ID to Modify:")
        if target_id:
            col_r, col_d = st.columns(2)
            with col_r:
                new_status = st.selectbox("Change Status:", ["Available", "Rented", "Pending"])
                if st.button("Update Status"):
                    supabase.table(db).update({"status": new_status}).eq('id', target_id).execute()
                    st.success("Status Updated!"); st.rerun()
            with col_d:
                if st.session_state.role == "admin":
                    if st.button("🗑️ Delete Record Permanently"):
                        supabase.table(db).delete().eq('id', target_id).execute()
                        st.warning("Record Deleted!"); st.rerun()
        
        st.dataframe(data, use_container_width=True)
