import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
import io

# --- 1. CONNECTION SETUP ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("Supabase connection details missing!")
    st.stop()

# --- 2. THEME ---
st.set_page_config(page_title="Deewary Hub Pro", layout="wide", page_icon="🏠")
st.markdown("""
    <style>
    .stApp { background-color: #05070A; color: #E0E0E0; }
    .metric-card { background: rgba(255, 255, 255, 0.03); border: 1px solid #FF4B4B; padding: 15px; border-radius: 15px; text-align: center; }
    .house-card { background: #161B22; border-radius: 15px; padding: 10px; margin-bottom: 10px; border-bottom: 3px solid #FF4B4B; }
    .stButton>button { background: linear-gradient(90deg, #FF4B4B, #FF8080); color: white; border-radius: 8px; font-weight: bold; width: 100%; }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIN (Simplified for this version) ---
if "auth" not in st.session_state: st.session_state.update({"auth": False, "user": None})
if not st.session_state.auth:
    st.title("🏠 DEEWARY LOGIN")
    u = st.selectbox("User", ["Sawer Khan", "Tariq Hussain", "Anas (Admin)"])
    p = st.text_input("Pin", type="password")
    if st.button("Login"):
        if p in ["admin786", "sawer123", "tariq123"]:
            st.session_state.update({"auth": True, "user": u})
            st.rerun()
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

tab_dash, tab_entry, tab_history = st.tabs(["📊 Dashboard", "📝 Add Entry", "📂 Records"])

# --- TAB 1: DASHBOARD ---
with tab_dash:
    st.write(f"### Welcome, {st.session_state.user}!")
    
    # Simple Metrics
    avail_df = df_h[df_h['status'] == 'Available'] if not df_h.empty else pd.DataFrame()
    c1, c2 = st.columns(2)
    c1.markdown(f"<div class='metric-card'><h3>Available</h3><h2>{len(avail_df)}</h2></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-card'><h3>Today's Visits</h3><h2>{len(df_v)}</h2></div>", unsafe_allow_html=True)

    st.divider()
    st.subheader("📍 Live Inventory")
    if not avail_df.empty:
        for _, row in avail_df.head(10).iterrows():
            with st.container():
                col_img, col_txt = st.columns([1, 2])
                with col_img:
                    # Photo dikhane ka logic
                    img_url = row.get('pic_url')
                    if img_url: st.image(img_url, use_container_width=True)
                    else: st.info("No Photo")
                with col_txt:
                    st.markdown(f"**{row['location']}** - Rs. {row['rent']}")
                    st.caption(f"{row['marla']} | {row['beds']} Beds | 💧 {row['water']}")
            st.markdown("---")

# --- TAB 2: ENTRY (With Photo Upload) ---
with tab_entry:
    mode = st.radio("Add:", ["Property", "Visit"], horizontal=True)
    
    if mode == "Property":
        with st.form("p_form", clear_on_submit=True):
            o_name = st.text_input("Owner Name")
            o_loc = st.text_input("Location")
            o_rent = st.number_input("Rent", min_value=0)
            o_marla = st.text_input("Size (Marla)")
            o_beds = st.number_input("Beds", 1, 10)
            o_water = st.selectbox("Water", ["Tanker", "Boring", "Line", "Yes"])
            
            # --- PHOTO UPLOAD OPTION ---
            uploaded_file = st.file_uploader("Take/Choose House Photo", type=['jpg', 'png', 'jpeg'])
            
            if st.form_submit_button("SAVE PROPERTY"):
                pic_url = ""
                if uploaded_file:
                    # Uploading to Supabase Storage
                    file_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    file_content = uploaded_file.getvalue()
                    supabase.storage.from_('house_pics').upload(file_name, file_content)
                    # Getting Public URL
                    pic_url = supabase.storage.from_('house_pics').get_public_url(file_name)
                
                # Database mein save karna
                supabase.table('house_inventory').insert({
                    "owner_name": o_name, "location": o_loc, "rent": o_rent,
                    "marla": o_marla, "beds": o_beds, "water": o_water,
                    "pic_url": pic_url, "status": "Available", "added_by": st.session_state.user
                }).execute()
                st.success("Ghar aur Photo dono add ho gaye!")
                st.rerun()

# --- TAB 3: RECORDS ---
with tab_history:
    st.dataframe(df_h, use_container_width=True)
    st.divider()
    # Excel Download
    if not df_h.empty:
        buffer = io.BytesIO()
        df_h.to_excel(buffer, index=False)
        st.download_button("📥 Download All Data to Excel", buffer, file_name="inventory.xlsx")
