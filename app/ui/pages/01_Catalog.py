import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import streamlit as st

from app.ui.service_locator import get_dog_service, get_photo_service
from app.ui.components import dog_card, filter_sidebar

st.set_page_config(page_title="Dog Catalog", page_icon="📋", layout="wide")
st.title("📋 Dog Catalog")

dog_service = get_dog_service()
photo_service = get_photo_service()

locations = dog_service.get_distinct_locations()
filters = filter_sidebar(locations)

dogs = dog_service.get_catalog_page(**filters)

if not dogs:
    st.info("No dogs found with the selected filters.")
else:
    st.caption(f"{len(dogs)} dogs found")
    cols_per_row = 4
    columns = st.columns(cols_per_row)

    for i, dog in enumerate(dogs):
        primary_photo = photo_service.get_primary_photo(dog.id)
        with columns[i % cols_per_row]:
            clicked = dog_card(dog, primary_photo, key_prefix=f"catalog_{i}_")
            if clicked:
                st.session_state["ss_selected_dog_id"] = dog.id
                st.switch_page("pages/02_Dog_Detail.py")
