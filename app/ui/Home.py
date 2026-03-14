import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st

from app.ui.service_locator import get_dog_service
from app.ui.components import stats_metric_row

st.set_page_config(
    page_title="Etho Dog Catalog",
    page_icon="🐕",
    layout="wide",
)

st.title("🐕 Etho Dog Catalog Manager")
st.markdown("Dog catalog management — local archive.")

dog_service = get_dog_service()
stats = dog_service.get_dashboard_stats()

st.subheader("Overview")
stats_metric_row(stats)

st.divider()

st.subheader("Quick Actions")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📋 Open catalog", width='stretch', type="primary"):
        st.switch_page("pages/01_Catalog.py")

with col2:
    if st.button("➕ Add dog", width='stretch', type="primary"):
        st.switch_page("pages/03_Add_Dog.py")

with col3:
    if st.button("📷 Update photo", width='stretch', type="primary"):
        st.switch_page("pages/04_Quick_Photo_Update.py")

col4, col5 = st.columns(2)
with col4:
    if st.button("📄 Export PDF", width='stretch'):
        st.switch_page("pages/05_Export.py")

with col5:
    if st.button("🗃️ Archived", width='stretch'):
        st.switch_page("pages/06_Archived.py")

if stats.get("needs_photo_update", 0) > 0:
    st.warning(
        f"⚠️ {stats['needs_photo_update']} dogs have their photo marked as needing update."
    )
