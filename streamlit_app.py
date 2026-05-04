import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
import plotly.express as px  # Professional charts ke liye

# --- 1. SUPABASE SETUP ---
# Database connection directly secrets se uthayi jayegi
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. PAGE CONFIG ---
st.set_page_config(
    page_title="Deewary Pro Manager", 
    layout="wide", 
    page_icon="🏢",
    initial_sidebar_state="expanded"
)

# --- 3. EXTRA LEVEL CUSTOM CSS ---
st.markdown("""
    <style>
    /* Professional Dark Theme & Mobile Optimization */
    .main { background-color: #0E1117; }
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;}
    
    /* Metric Card Styling */
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 700;
        color: #FF4B4B;
    }
    div[data-testid="metric-container"] {
        background-color: #1E1E1E;
        border: 1px solid #333;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    /* Sidebar Customization */
    [data-testid="stSidebar"] {
        background-color: #111111;
        border-right: 1px solid #333;
    }
    
    /* WhatsApp Button Style */
    .wa-btn {
        background-color: #25D366;
        color: white;
        padding: 8px 15px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. UTILITY FUNCTIONS ---
def send_whatsapp(number, client_name, msg_type="general"):
    # Number clean-up for Pakistan
    clean_num = str(number).replace("+", "").replace("-", "").replace(" ", "")
    if clean_num.startswith("0"): clean_num = "92" + clean_num[1:]
    
    msgs = {
        "general": f"Assalam o Alaikum {client_name}, Deewary.com se rabta karne ka shukria. Kya main aapki mazeed madad kar sakta hoon?",
        "done": f"Mubarak ho {client_name}! Aapki deal Deewary.com ke sath finalize ho gayi hai."
    }
    return f"https://wa.me/{clean_num}?text={msgs[msg_type].replace(' ', '%20')}"

# --- 5. LOG-IN SYSTEM ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<div style='text-align:center; padding-top:100px;'>", unsafe_allow_html=True)
    st.title("🏢 DEEWARY MANAGER LOGIN")
    pwd = st.text_input("Enter Access Code", type="password")
    if st.button("Access Portal"):
        if pwd == "admin786":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Ghalat Code!")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 6. SIDEBAR NAVIGATION ---
st.sidebar.markdown(f"### WELCOME, {st.session_state.get('user', 'UMER')}")
menu = st.sidebar.radio("MAIN MENU", [
    "📊 Dashboard", 
    "🏠 Property Inventory", 
    "👥 Client CRM", 
    "⏳ Pending & Done Deals"
])

# --- 7. MODULE 1: DYNAMIC DASHBOARD ---
if menu == "📊 Dashboard":
    st.markdown("<div class='header-box'><h1>REAL-TIME ANALYTICS</h1></div>", unsafe_allow_html=True)
    
    # Fetch Data
    h_data = supabase.table('house_inventory').select("*").execute().data
    c_data = supabase.table('client_leads').select("*").execute().data
    d_data = supabase.table('deals_done').select("*").execute().data
    
    # Dashboard Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Houses", len(h_data))
    m2.metric("Leads", len(c_data))
    m3.metric("Done Deals", len(d_data))
    m4.metric("Conversion", f"{round(len(d_data)/len(c_data)*100, 1) if c_data else 0}%")

    st.divider()
    
    # Pro Charts (Plotly)
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Property Inventory Status")
        if h_data:
            df_h = pd.DataFrame(h_data)
            fig = px.pie(df_h, names='status', hole=.4, color_discrete_sequence=['#FF4B4B', '#25D366'])
            st.plotly_chart(fig, use_container_width=True)
    
    with col_b:
        st.subheader("Client Growth")
        if c_data:
            df_c = pd.DataFrame(c_data)
            df_c['created_at'] = pd.to_datetime(df_c['created_at'])
            fig_line = px.line(df_c.groupby(df_c['created_at'].dt.date).count(), y='id', labels={'id':'New Leads'})
            st.plotly_chart(fig_line, use_container_width=True)

# --- 8. MODULE 2: INVENTORY ---
elif menu == "🏠 Property Inventory":
    st.title("House Inventory Management")
    
    tab1, tab2 = st.tabs(["📋 View All", "➕ Add New House"])
    
    with tab2:
        with st.form("new_house"):
            o_name = st.text_input("Owner Name")
            loc = st.text_input("Location")
            rent = st.number_input("Demand Rent", min_value=0)
            portion = st.selectbox("Portion", ["Full", "Ground", "First", "Basement"])
            if st.form_submit_button("Save Property"):
                supabase.table('house_inventory').insert({
                    "owner_name": o_name, "location": loc, "rent": rent, "portion": portion, "status": "Available"
                }).execute()
                st.success("Property Added!")

    with tab1:
        res = supabase.table('house_inventory').select("*").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            # Custom styled dataframe
            st.dataframe(df.style.highlight_max(axis=0, color='#331111'), use_container_width=True)

# --- 9. MODULE 3: CLIENT CRM ---
elif menu == "👥 Client CRM":
    st.title("Client Relationship Manager")
    
    res = supabase.table('client_leads').select("*").order('id', desc=True).execute()
    if res.data:
        for client in res.data:
            with st.container():
                st.markdown(f"""
                <div style="background-color:#1E1E1E; padding:15px; border-radius:10px; border-left: 5px solid #FF4B4B; margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between;">
                        <b>👤 {client['client_name']}</b>
                        <span style="color:#888;">{client['contact']}</span>
                    </div>
                    <p style="font-size:0.9rem; margin-top:5px;">Requirement: {client.get('req_location', 'N/A')} | Budget: {client.get('budget', 0)}</p>
                    <a href="{send_whatsapp(client['contact'], client['client_name'])}" target="_blank" class="wa-btn">Send WhatsApp Msg</a>
                </div>
                """, unsafe_allow_html=True)

# --- FOOTER ---
st.sidebar.divider()
st.sidebar.caption(f"© {datetime.now().year} Deewary.com | V2.0 Pro Edition")
