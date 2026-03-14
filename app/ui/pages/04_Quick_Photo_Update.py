import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import streamlit as st

from app.ui.service_locator import get_dog_service, get_photo_service
from app.ui.components import photo_grid

st.set_page_config(page_title="Update Photo", page_icon="📷", layout="centered")
st.title("📷 Quick Photo Update")

dog_service = get_dog_service()
photo_service = get_photo_service()

# --- Phase 1: Search dog ---
st.subheader("1. Search for dog")
search_query = st.text_input("Search by name...", key="ss_quick_photo_query")

if search_query:
    results = dog_service.search_dogs(query=search_query)
    if not results:
        st.info("No dog found.")
    else:
        for dog in results:
            primary = photo_service.get_primary_photo(dog.id)
            col1, col2 = st.columns([3, 1])
            with col1:
                label = f"**{dog.name}**"
                if dog.location:
                    label += f" — {dog.location}"
                if dog.needs_photo_update:
                    label += " ⚠️"
                st.markdown(label)
            with col2:
                if st.button("Select", key=f"select_quick_{dog.id}"):
                    st.session_state["ss_quick_photo_dog_id"] = dog.id
                    st.rerun()

# --- Phase 2: Upload photo ---
dog_id = st.session_state.get("ss_quick_photo_dog_id")

if dog_id:
    dog, photos = dog_service.get_dog_with_photos(dog_id)
    if dog is None:
        st.error("Dog not found.")
        st.stop()

    st.divider()
    st.subheader(f"2. Update photo for: **{dog.name}**")

    if st.button("✗ Deselect dog"):
        st.session_state.pop("ss_quick_photo_dog_id", None)
        st.rerun()

    # Current photos
    if photos:
        st.markdown("**Current photos:**")

        def on_set_primary(photo_id: int):
            photo_service.set_primary_photo(dog_id, photo_id)
            st.success("Primary photo updated!")
            st.rerun()

        photo_grid(photos, on_set_primary=on_set_primary)

    # Upload new photo
    st.markdown("**Upload new photo:**")
    with st.form("quick_upload_form"):
        uploaded = st.file_uploader(
            "Image", type=["jpg", "jpeg", "png", "webp"]
        )
        note = st.text_input("Note (optional)")
        set_primary = st.checkbox("Set as primary photo", value=True)
        remove_flag = st.checkbox(
            "Remove 'needs photo update' flag",
            value=dog.needs_photo_update,
            disabled=not dog.needs_photo_update,
        )
        upload_btn = st.form_submit_button("📤 Upload", type="primary")

    if upload_btn:
        if uploaded is None:
            st.error("Please select an image file.")
        else:
            try:
                photo_service.upload_photo(
                    dog_id=dog_id,
                    file_bytes=uploaded.read(),
                    filename=uploaded.name,
                    note=note,
                    set_as_primary=set_primary,
                )
                if remove_flag and dog.needs_photo_update:
                    dog_service.mark_needs_photo_update(dog_id, False)
                st.success(f"✅ Photo uploaded for {dog.name}!")
                st.rerun()
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Error: {e}")
