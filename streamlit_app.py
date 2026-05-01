import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime, date, timedelta
from fpdf import FPDF

# --- 1. SUPABASE SETUP ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- 2. PAGE CONFIG & PREMIUM DARK THEME ---
st.set_page_config(page_title="Deewary Pro Admin", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #0E1117; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #30363D; }
    
    .main-header { background-color: #161B22; padding: 15px; border-radius: 10px; border-bottom: 2px solid #FF8C00; margin-bottom: 20px; }
    .metric-card { background-color: #1C2128; padding: 15px; border-radius: 10px; border: 1px solid #30363D; border-top: 3px solid #FF8C00; text-align: center; }
    .staff-box { background-color: #161B22; padding: 10px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid #FF8C00; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER & LOGIN ---
st.markdown("""
    <div class="main-header">
        <h2 style="color: #FF8C00; margin: 0;">DEEWARY<span style="color: white;">.PRO</span></h2>
        <p style="color: #8B949E; margin: 0; font-size: 12px;">REAL ESTATE & CONSTRUCTION MANAGEMENT PORTAL</p>
    </div>
""", unsafe_allow_html=True)

user_name = st.sidebar.selectbox("User Account", ["Anas", "Sawer Khan", "Tariq Hussain"])
pwd = st.sidebar.text_input("Security Pin", type="password")

if pwd == "admin786":
    menu = st.sidebar.radio("NAVIGATE", [
        "📊 Live Dashboard", 
        "📈 Monthly Staff Report", 
        "🤝 Deal Pipeline",
        "📥 Data Entry", 
        "🛠️ Admin Control"
    ])

    # --- 4. LIVE DASHBOARD ---
    if menu == "📊 Live Dashboard":
        today = date.today().isoformat()
        h_data = supabase.table('house_inventory').select("*").execute().data
        df_all = pd.DataFrame(h_data)
        
        # Top Metrics: Rent & Progress
        total_rent_active = df_all[df_all['status'] == 'Available']['rent'].sum() if not df_all.empty else 0
        st.markdown(f"### 💰 Total Available Inventory Rent: <span style='color:#FF8C00;'>PKR {total_rent_active:,}</span>", unsafe_allow_html=True)
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            today_h = len(df_all[df_all['created_at'].str.contains(today)]) if not df_all.empty else 0
            st.markdown(f'<div class="metric-card"><h2>{today_h}</h2><p>Ghar Added (Today)</p></div>', unsafe_allow_html=True)
        with c2:
            deals_today = len(df_all[(df_all['status'] == 'Rent Out') & (df_all['created_at'].str.contains(today))]) if not df_all.empty else 0
            st.markdown(f'<div class="metric-card"><h2 style="color:#00FF00;">{deals_today}</h2><p>Deals Done (Today)</p></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card"><h2>5</h2><p>Visits Scheduled</p></div>', unsafe_allow_html=True) # Static for example
        with c4:
            pending = len(df_all[df_all['status'] == 'Available']) if not df_all.empty else 0
            st.markdown(f'<div class="metric-card"><h2>{pending}</h2><p>Pending Units</p></div>', unsafe_allow_html=True)

    # --- 5. MONTHLY STAFF REPORT ---
    elif menu == "📈 Monthly Staff Report":
        st.markdown("### 🗓️ Monthly Progress Report")
        month_start = (date.today().replace(day=1)).isoformat()
        
        h_res = supabase.table('house_inventory').select("*").gte('created_at', month_start).execute()
        df_month = pd.DataFrame(h_res.data)
        
        for staff in ["Anas", "Sawer Khan", "Tariq Hussain"]:
            s_data = df_month[df_month['added_by'] == staff] if not df_month.empty else pd.DataFrame()
            total_added = len(s_data)
            deals_done = len(s_data[s_data['status'] == 'Rent Out'])
            pending = total_added - deals_done
            
            st.markdown(f"""
            <div class="staff-box">
                <table style="width:100%; color:white;">
                    <tr>
                        <td width="25%"><b>{staff}</b></td>
                        <td>Ghar Lagaye: {total_added}</td>
                        <td>Ghar Done: {deals_done}</td>
                        <td>Pending: {pending}</td>
                        <td style="color:#FF8C00;">Success Rate: {round((deals_done/total_added)*100 if total_added > 0 else 0)}%</td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

    # --- 6. DEAL PIPELINE ---
    elif menu == "🤝 Deal Pipeline":
        st.markdown("### 🤝 Active Client Negotiations")
        clients = supabase.table('client_leads').select("*").execute()
        df_cl = pd.DataFrame(clients.data)
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown('<div class="metric-card"><h3>12</h3><p>Ongoing Deals</p></div>', unsafe_allow_html=True)
        with col_p2:
            st.markdown('<div class="metric-card"><h3>45</h3><p>Completed Deals</p></div>', unsafe_allow_html=True)
            
        st.write("#### Client Details & Status")
        st.dataframe(df_cl, use_container_width=True)

    # --- 7. DATA ENTRY ---
    elif menu == "📥 Data Entry":
        st.subheader("Add New Property or Lead")
        with st.form("entry_form"):
            type_e = st.radio("Entry Type", ["Property", "Client"], horizontal=True)
            o_n = st.text_input("Name")
            cont = st.text_input("Contact")
            loc = st.text_input("Location")
            rent_val = st.number_input("Value (Rent/Budget)", min_value=0)
            if st.form_submit_button("Save Record"):
                table = "house_inventory" if type_e == "Property" else "client_leads"
                payload = {"owner_name" if type_e == "Property" else "client_name": o_n, "contact": cont, "location" if type_e == "Property" else "req_location": loc, "rent" if type_e == "Property" else "budget": rent_val, "added_by": user_name, "status": "Available"}
                supabase.table(table).insert(payload).execute()
                st.success("Record Saved!")

    # --- 8. ADMIN CONTROL ---
    elif menu == "🛠️ Admin Control":
        st.write("#### Delete/Edit Records by ID")
        del_id = st.number_input("Enter ID", min_value=1)
        if st.button("Delete Permanent"):
            supabase.table("house_inventory").delete().eq("id", del_id).execute()
            st.warning(f"ID {del_id} Deleted")

else:
    st.info("Please enter your security pin to continue.")

st.markdown("<hr><p style='text-align:center; color:grey;'>Deewary.com Management System | 2026</p>", unsafe_allow_html=True)
