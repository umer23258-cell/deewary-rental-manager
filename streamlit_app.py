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
    st.error("Supabase connection details missing in Secrets!")
    st.stop()

# --- 2. THEME & UI (Same as yours) ---
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
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIN SYSTEM (Same as yours) ---
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

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown(f"### Welcome, **{st.session_state.user_name}**")
    st.caption(f"Access Level: {st.session_state.user_role.upper()}")
    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.rerun()

# --- 6. TABS ---
tab_dash, tab_entry, tab_history = st.tabs(["📊 Dashboard (Stock)", "📝 Add New Entry", "📂 Full History & Edit"])

# --- TAB 1: DASHBOARD ---
with tab_dash:
    st.markdown("## Live Operational Overview")
    
    avail_df = df_h[df_h['status'] == 'Available'] if not df_h.empty else pd.DataFrame()
    rented_df = df_h[df_h['status'] == 'Rented'] if not df_h.empty else pd.DataFrame()
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div class='metric-card'><h3>🏠 Available</h3><h2>{len(avail_df)}</h2></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='metric-card'><h3>👥 Active Leads</h3><h2>{len(df_c)}</h2></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='metric-card'><h3>🚗 Total Visits</h3><h2>{len(df_v)}</h2></div>", unsafe_allow_html=True)
    with c4:
        total_rented_val = rented_df['rent'].sum() if not rented_df.empty else 0
        st.markdown(f"<div class='metric-card'><h3>💰 Monthly Vol</h3><h2>{total_rented_val:,.0f}</h2></div>", unsafe_allow_html=True)

    # --- DAILY RECORD SECTION ---
    st.divider()
    st.subheader("📅 Today's Record Summary")
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    t_h = len(df_h[df_h['created_at'].str.contains(today_str, na=False)]) if not df_h.empty else 0
    t_c = len(df_c[df_c['created_at'].str.contains(today_str, na=False)]) if not df_c.empty else 0
    t_v = len(df_v[df_v['date'].astype(str) == today_str]) if not df_v.empty else 0

    tc1, tc2, tc3 = st.columns(3)
    tc1.metric("New Houses", t_h); tc2.metric("New Leads", t_c); tc3.metric("Visits", t_v)

    st.divider()
    st.subheader("📍 Quick Available Stock List")
    if not avail_df.empty:
        # Display with Image Support
        for _, row in avail_df.head(10).iterrows():
            with st.container():
                col_img, col_txt = st.columns([1, 3])
                with col_img:
                    if row.get('pic_url'): st.image(row['pic_url'], use_container_width=True)
                    else: st.info("No Photo")
                with col_txt:
                    st.markdown(f"### {row['location']} - Rs. {row['rent']}")
                    st.write(f"Owner: {row['owner_name']} | {row['marla']} | {row['beds']} Beds | 💧 {row['water']}")
            st.markdown("---")
    else: st.info("No houses currently available.")

# --- TAB 2: ENTRY CENTER (With Photo Upload) ---
with tab_entry:
    choice = st.radio("Choose Category:", ["Ghar (Property)", "Gahak (Client)", "Visit Log"], horizontal=True)
    
    if choice == "Ghar (Property)":
        with st.form("h_form", clear_on_submit=True):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                on = st.text_input("Owner Name"); oc = st.text_input("Owner Contact"); ol = st.text_input("Exact Location")
            with col_b:
                ornt = st.number_input("Monthly Rent", min_value=0); om = st.text_input("Marla (Size)")
                of = st.selectbox("Floor", ["Ground", "First", "Upper", "Full House"]); ob = st.number_input("Bedrooms", 1, 15)
            with col_c:
                ow = st.selectbox("Water", ["Yes", "Boring", "Line Water", "Tanker", "No"])
                og = st.selectbox("Gas", ["Separate", "Common", "No"])
                oe = st.selectbox("Electricity", ["Separate", "Sub Meter"])
            
            # Photo Upload Field
            up_file = st.file_uploader("Upload House Photo (Optional)", type=['jpg', 'jpeg', 'png'])
            
            if st.form_submit_button("Save to Inventory"):
                p_url = ""
                if up_file:
                    f_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{up_file.name}"
                    supabase.storage.from_('house_pics').upload(f_name, up_file.getvalue())
                    p_url = supabase.storage.from_('house_pics').get_public_url(f_name)

                supabase.table('house_inventory').insert({
                    "owner_name":on, "contact":oc, "location":ol, "rent":ornt, "marla":om, 
                    "floor":of, "beds":ob, "water":ow, "gas":og, "electricity":oe, 
                    "pic_url":p_url, "added_by":st.session_state.user_name
                }).execute()
                st.success("Property Registered!"); st.rerun()

    elif choice == "Gahak (Client)":
        with st.form("c_form", clear_on_submit=True):
            ca, cb = st.columns(2)
            with ca:
                cn = st.text_input("Client Name"); cc = st.text_input("Contact"); cb_val = st.number_input("Budget", min_value=0)
                cb_beds = st.number_input("Required Beds", 1, 15)
            with cb:
                cm = st.text_input("Required Marla"); car = st.text_input("Preferred Area")
                cp = st.selectbox("Portion Type", ["Any", "Ground", "First", "Full House"])
            if st.form_submit_button("Save Client Lead"):
                supabase.table('client_leads').insert({"name":cn,"contact":cc,"budget":cb_val,"beds":cb_beds,"marla":cm,"area":car,"portion":cp,"added_by":st.session_state.user_name}).execute()
                st.success("Client Requirement Logged!"); st.rerun()

    elif choice == "Visit Log":
        with st.form("v_form", clear_on_submit=True):
            vc = st.text_input("Client Name"); vh = st.text_input("Property Visited")
            vf = st.text_area("Client Feedback/Remarks")
            if st.form_submit_button("Log Visit"):
                supabase.table('visit_logs').insert({"client":vc,"house":vh,"staff":st.session_state.user_name,"feedback":vf,"date":str(datetime.now().date())}).execute()
                st.success("Activity Recorded!"); st.rerun()

# --- TAB 3: HISTORY & EXCEL ---
with tab_history:
    db_target = st.selectbox("Database Table:", ["house_inventory", "client_leads", "visit_logs"])
    raw_df = fetch_data(db_target)
    
    if not raw_df.empty:
        # Excel Download Button
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            raw_df.to_excel(writer, index=False)
        st.download_button(label="📥 Download as Excel", data=output.getvalue(), file_name=f"{db_target}.xlsx")
        
        search_q = st.text_input(f"🔍 Search in {db_target}...")
        if search_q:
            raw_df = raw_df[raw_df.astype(str).apply(lambda x: x.str.contains(search_q, case=False)).any(axis=1)]
        st.dataframe(raw_df, use_container_width=True)
        
        st.divider()
        rec_id = st.text_input("Enter ID to modify:")
        if rec_id:
            col_edit, col_del = st.columns(2)
            with col_edit:
                new_status = st.selectbox("Status:", ["Available", "Rented", "Maintenance"])
                if st.button("Update Status"):
                    supabase.table(db_target).update({"status": new_status}).eq('id', rec_id).execute()
                    st.success("Updated!"); st.rerun()
            with col_del:
                if st.session_state.user_role == "admin" and st.button("🗑️ Delete Record"):
                    supabase.table(db_target).delete().eq('id', rec_id).execute()
                    st.rerun()
    else: st.info("No data found.")

st.divider()
st.markdown("<p style='text-align: center; opacity: 0.6;'>Deewary Rental OS v3.0 | Staff: Sawer & Tariq</p>", unsafe_allow_html=True)
