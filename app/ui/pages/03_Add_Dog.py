import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from datetime import datetime
import streamlit as st

from app.models.dog import LOCATION_OPTIONS, COLOR_OPTIONS
from app.ui.service_locator import get_dog_service, get_photo_service

st.set_page_config(page_title="Add Dog", page_icon="➕", layout="centered")
st.title("➕ Add new dog")

dog_service = get_dog_service()
photo_service = get_photo_service()

with st.form("add_dog_form", clear_on_submit=True):

    st.subheader("Main Info")
    name = st.text_input("Name *")
    location = st.selectbox("Location *", LOCATION_OPTIONS)
    sex = st.radio("Sex *", ["M", "F"], horizontal=True)
    year = st.text_input("Year *", value=str(datetime.now().year))

    st.divider()
    st.subheader("Optional Fields")

    col1, col2 = st.columns(2)
    with col1:
        tag_input = st.text_input("Tag number (1-999)", placeholder="es. 42")
    with col2:
        color_choice = st.selectbox("Color", ["(nessuno)"] + COLOR_OPTIONS)

    dead = st.checkbox("Dead")
    notes = st.text_area("Notes", placeholder="Free notes...")

    st.divider()
    photo_file = st.file_uploader("Main photo", type=["jpg", "jpeg", "png", "webp"])

    submitted = st.form_submit_button("💾 Add dog", type="primary")

if submitted:
    # Validazione tag_number
    tag_number = None
    if tag_input.strip():
        try:
            tag_number = int(tag_input.strip())
            if not (1 <= tag_number <= 999):
                st.error("Tag number must be between 1 and 999.")
                st.stop()
        except ValueError:
            st.error("Tag number must be an integer.")
            st.stop()

    color = color_choice if color_choice != "(nessuno)" else None

    if not year.strip():
        st.error("Year is required.")
        st.stop()

    try:
        dog = dog_service.create_dog(
            name=name,
            sex=sex,
            location=location,
            notes=notes,
            tag_number=tag_number,
            color=color,
            year=year.strip(),
            dead=dead,
        )

        if photo_file:
            try:
                photo_service.upload_photo(
                    dog_id=dog.id,
                    file_bytes=photo_file.read(),
                    filename=photo_file.name,
                    set_as_primary=True,
                )
            except ValueError as photo_err:
                st.warning(f"Dog added, but photo error: {photo_err}")

        st.success(f"✅ '{dog.format_display_name()}' added successfully!")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("View in catalog", key="go_detail"):
                st.session_state["ss_selected_dog_id"] = dog.id
                st.switch_page("pages/02_Dog_Detail.py")
        with col2:
            if st.button("Add another", key="add_another"):
                st.rerun()

    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"Unexpected error: {e}")
