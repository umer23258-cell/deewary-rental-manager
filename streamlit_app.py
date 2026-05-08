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
    st.error("Supabase secrets missing!")
    st.stop()

# --- 2. THEME & UI ---
st.set_page_config(page_title="Deewary Hub Pro", layout="wide", page_icon="🏠")

st.markdown("""
    <style>
    .stApp { background-color: #05070A; color: #E0E0E0; }
    [data-testid="stMetric"] { background-color: #1E2130; border-left: 5px solid #FF4B4B; padding: 15px; border-radius: 10px; }
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 75, 75, 0.3);
        padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 10px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #FF4B4B 0%, #FF8080 100%);
        color: white; border: none; border-radius: 8px; font-weight: bold; width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.update({"authenticated": False, "user_role": None, "user_name": None})

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🏠 DEEWARY PRO</h1>", unsafe_allow_html=True)
        user = st.selectbox("Select User", ["Sawer Khan", "Tariq Hussain", "Anas (Admin)"])
        pwd = st.text_input("Access Key", type="password")
        if st.button("Unlock System"):
            if user == "Anas (Admin)" and pwd == "admin786":
                st.session_state.update({"authenticated": True, "user_role": "admin", "user_name": "Anas"})
                st.rerun()
            elif (user == "Sawer Khan" and pwd == "sawer123") or (user == "Tariq Hussain" and pwd == "tariq123"):
                st.session_state.update({"authenticated": True, "user_role": "staff", "user_name": user})
                st.rerun()
            else: st.error("❌ Invalid Access Key!")
    st.stop()

# --- 4. DATA LOGIC ---
def fetch_data(table):
    try:
        res = supabase.table(table).select("*").order('created_at', desc=True).execute()
        return pd.DataFrame(res.data)
    except: return pd.DataFrame()

df_h = fetch_data('house_inventory')
df_c = fetch_data('client_leads')
df_v = fetch_data('visit_logs')

# --- 5. TABS ---
tab_dash, tab_entry, tab_history = st.tabs(["📊 Dashboard", "📝 Add New Entry", "📂 Full History"])

# --- TAB 1: DASHBOARD ---
with tab_dash:
    avail_df = df_h[df_h['status'] == 'Available'] if not df_h.empty else pd.DataFrame()
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='metric-card'><h3>🏠 Available</h3><h2>{len(avail_df)}</h2></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='metric-card'><h3>👥 Leads</h3><h2>{len(df_c)}</h2></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='metric-card'><h3>🚗 Visits</h3><h2>{len(df_v)}</h2></div>", unsafe_allow_html=True)

    st.divider()
    st.subheader("📍 Quick View")
    if not avail_df.empty:
        for _, row in avail_df.head(10).iterrows():
            with st.container():
                col_img, col_txt = st.columns([1, 4])
                with col_img:
                    imgs = row.get('image_urls', [])
                    if imgs and len(imgs) > 0: st.image(imgs[0], use_container_width=True)
                    else: st.info("No Pic")
                with col_txt:
                    st.write(f"**{row['location']}** | Rs. {row['rent']} | {row['marla']}")
            st.markdown("---")

# --- TAB 2: ENTRY CENTER ---
with tab_entry:
    choice = st.radio("Choose:", ["Ghar (Property)", "Gahak (Client)", "Visit Log"], horizontal=True)
    
    if choice == "Ghar (Property)":
        with st.form("h_form", clear_on_submit=True):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                on = st.text_input("Owner Name"); oc = st.text_input("Contact"); ol = st.text_input("Location")
            with col_b:
                ornt = st.number_input("Rent", min_value=0); om = st.text_input("Marla")
                of = st.selectbox("Floor", ["Ground", "First", "Upper", "Full House"]); ob = st.number_input("Beds", 1, 15)
            with col_c:
                ow = st.selectbox("Water", ["Yes", "Boring", "Line Water"]); og = st.selectbox("Gas", ["Yes", "No"]); oe = st.selectbox("Electricity", ["Separate", "Sub Meter"])
            
            uploaded_files = st.file_uploader("📸 Select House Photos (Max 6)", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)
            
            if st.form_submit_button("Save to Inventory"):
                img_urls = []
                if uploaded_files:
                    for file in uploaded_files[:6]:
                        f_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.name}"
                        supabase.storage.from_('house_pics').upload(f_name, file.getvalue())
                        img_urls.append(supabase.storage.from_('house_pics').get_public_url(f_name))

                supabase.table('house_inventory').insert({
                    "owner_name":on, "contact":oc, "location":ol, "rent":ornt, "marla":om, 
                    "floor":of, "beds":ob, "water":ow, "gas":og, "electricity":oe, 
                    "added_by":st.session_state.user_name, "image_urls": img_urls, "status": "Available"
                }).execute()
                st.success("Property Saved!"); st.rerun()

    elif choice == "Gahak (Client)":
        with st.form("c_form"):
            cn = st.text_input("Name"); cc = st.text_input("Contact"); cb = st.number_input("Budget")
            if st.form_submit_button("Save Lead"):
                supabase.table('client_leads').insert({"name":cn,"contact":cc,"budget":cb,"added_by":st.session_state.user_name}).execute()
                st.success("Lead Saved!"); st.rerun()

# --- TAB 3: HISTORY (EDIT, DELETE, RENT OUT ADDED) ---
with tab_history:
    db_target = st.selectbox("Select Table:", ["house_inventory", "client_leads", "visit_logs"])
    raw_df = fetch_data(db_target)
    
    if not raw_df.empty:
        # EXCEL DOWNLOAD
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            raw_df.to_excel(writer, index=False)
        st.download_button("📥 Download Excel", output.getvalue(), f"{db_target}.xlsx")
        
        st.write("---")
        
        # Edit/Delete Management Section
        for i, row in raw_df.iterrows():
            # Har record ke liye aik expander box
            with st.expander(f"🆔 {row['id']} | {row.get('location', row.get('name', 'Details'))} | {row.get('status', '')}"):
                c1, c2, c3 = st.columns(3)
                
                # 1. RENT OUT BUTTON (Sirf house inventory ke liye)
                with c1:
                    if db_target == "house_inventory":
                        current_status = row.get('status', 'Available')
                        label = "🔓 Make Available" if current_status == "Rented" else "🔒 Rent Out"
                        target_status = "Available" if current_status == "Rented" else "Rented"
                        if st.button(label, key=f"status_{row['id']}"):
                            supabase.table(db_target).update({"status": target_status}).eq('id', row['id']).execute()
                            st.rerun()
                
                # 2. DELETE BUTTON (Sirf Admin Anas ke liye)
                with c2:
                    if st.session_state.user_role == "admin":
                        if st.button("🗑️ Delete Record", key=f"del_{row['id']}"):
                            supabase.table(db_target).delete().eq('id', row['id']).execute()
                            st.rerun()
                    else:
                        st.info("Delete only for Admin")

                # 3. EDIT OPTION (Manual entry trigger)
                with c3:
                    if st.button("📝 Edit Info", key=f"edit_{row['id']}"):
                        st.warning("Manual editing abhi enabled nahi hai, admin se contact karein.")

        st.divider()
        st.dataframe(raw_df, use_container_width=True)
