import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import streamlit as st

from app.ui.service_locator import get_dog_service
from app.ui.components import confirm_action

st.set_page_config(page_title="Archived Dogs", page_icon="🗃️", layout="wide")
st.title("🗃️ Archived Dogs")

dog_service = get_dog_service()

archived_dogs = dog_service.search_dogs(status="archived", order_by="name")

if not archived_dogs:
    st.info("No archived dogs.")
else:
    st.caption(f"{len(archived_dogs)} archived dogs")

    for dog in archived_dogs:
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            with col1:
                st.markdown(f"**{dog.name}**")
                meta_parts = []
                if dog.sex and dog.sex != "Unknown":
                    meta_parts.append(dog.display_sex())
                if dog.location:
                    meta_parts.append(dog.location)
                if meta_parts:
                    st.caption(" · ".join(meta_parts))
            with col2:
                if dog.updated_at:
                    st.caption(f"Archived: {dog.updated_at.strftime('%d/%m/%Y')}")
            with col3:
                if st.button("♻️ Restore", key=f"restore_{dog.id}"):
                    dog_service.restore_dog(dog.id)
                    st.success(f"Dog '{dog.name}' restored!")
                    st.rerun()
            with col4:
                if confirm_action("🗑️ Delete", "Permanent deletion.", f"del_{dog.id}"):
                    dog_service.delete_dog(dog.id)
                    st.rerun()
