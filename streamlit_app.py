# --- MOBILE NAVIGATION FIX (Add this before menu logic) ---
# Yeh buttons sirf screen par nazar ayenge taake mobile user ko sidebar na dhundni pare
st.write("### 📱 Mobile Quick Menu")
row1 = st.columns(3)
row2 = st.columns(3)

with row1[0]:
    if st.button("🏠 Home", key="m_dash"): set_menu("🏠 Dashboard")
with row1[1]:
    if st.button("🏡 Ghar", key="m_ghar"): set_menu("🏠 Ghar ki Entry (Owners)")
with row1[2]:
    if st.button("👤 Client", key="m_client"): set_menu("👤 Client ki Entry (New)")

with row2[0]:
    if st.button("💬 Chat", key="m_disc"): set_menu("💬 Client in Discussion")
with row2[1]:
    if st.button("✅ Done", key="m_done"): set_menu("✅ Deal Done Entry")
with row2[2]:
    if st.button("📋 Hist", key="m_hist"): set_menu("📋 Gharon ki History")

st.divider()
# --- END OF MOBILE FIX ---
