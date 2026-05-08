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
    st.error("Supabase connection details missing in Secrets!")
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

# --- 4. DATA FETCH ---
def fetch_data(table):
    try:
        res = supabase.table(table).select("*").order('created_at', desc=True).execute()
        return pd.DataFrame(res.data)
    except: return pd.DataFrame()

df_h = fetch_data('house_inventory')
df_c = fetch_data('client_leads')
df_v = fetch_data('visit_logs')

# --- 5. TABS ---
tab_dash, tab_entry, tab_history = st.tabs(["📊 Dashboard (Stock)", "📝 Add New Entry", "📂 Full History"])

# --- DASHBOARD ---
with tab_dash:
    st.markdown("## Live Operational Overview")
    
    avail_df = df_h[df_h['status'] == 'Available'] if not df_h.empty else pd.DataFrame()
    
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='metric-card'><h3>🏠 Available</h3><h2>{len(avail_df)}</h2></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='metric-card'><h3>👥 Active Leads</h3><h2>{len(df_c)}</h2></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='metric-card'><h3>🚗 Total Visits</h3><h2>{len(df_v)}</h2></div>", unsafe_allow_html=True)

    # DAILY RECORD SUMMARY
    st.divider()
    st.subheader("📅 Today's Record Summary")
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    t_h = len(df_h[df_h['created_at'].str.contains(today_str, na=False)]) if not df_h.empty else 0
    t_v = len(df_v[df_v['date'].astype(str) == today_str]) if not df_v.empty else 0

    tc1, tc2 = st.columns(2)
    tc1.metric("New Houses Today", t_h)
    tc2.metric("Visits Today", t_v)

    st.divider()
    st.subheader("📍 Quick Available Stock")
    if not avail_df.empty:
        for _, row in avail_df.head(10).iterrows():
            with st.container():
                col_img, col_txt = st.columns([1, 3])
                with col_img:
                    if row.get('pic_url'): st.image(row['pic_url'], use_container_width=True)
                    else: st.info("No Photo")
                with col_txt:
                    st.markdown(f"### {row['location']} - Rs. {row['rent']}")
                    st.write(f"{row['marla']} | {row['beds']} Beds | 💧 {row['water']}")
            st.markdown("---")

# --- ENTRY CENTER ---
with tab_entry:
    choice = st.radio("Choose Category:", ["Ghar (Property)", "Visit Log"], horizontal=True)
    
    if choice == "Ghar (Property)":
        with st.form("h_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                on = st.text_input("Owner Name"); ol = st.text_input("Location")
            with col_b:
                ornt = st.number_input("Monthly Rent", min_value=0); om = st.text_input("Marla")
            
            # PHOTO UPLOAD
            up_file = st.file_uploader("House Photo (Optional)", type=['jpg', 'jpeg', 'png'])
            
            if st.form_submit_button("Save to Inventory"):
                p_url = ""
                if up_file:
                    f_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    supabase.storage.from_('house_pics').upload(f_name, up_file.getvalue())
                    p_url = supabase.storage.from_('house_pics').get_public_url(f_name)

                supabase.table('house_inventory').insert({
                    "owner_name":on, "location":ol, "rent":ornt, "marla":om, 
                    "pic_url":p_url, "status":"Available", "added_by":st.session_state.user_name
                }).execute()
                st.success("Property Saved!"); st.rerun()

# --- HISTORY & EXCEL ---
with tab_history:
    db_target = st.selectbox("Select Table:", ["house_inventory", "client_leads", "visit_logs"])
    raw_df = fetch_data(db_target)
    
    if not raw_df.empty:
        # EXCEL DOWNLOAD
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            raw_df.to_excel(writer, index=False)
        st.download_button("📥 Download as Excel", output.getvalue(), f"{db_target}.xlsx")
        
        st.dataframe(raw_df, use_container_width=True)
