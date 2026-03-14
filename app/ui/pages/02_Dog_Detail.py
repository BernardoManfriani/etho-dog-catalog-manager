import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import streamlit as st

from app.models.dog import LOCATION_OPTIONS, COLOR_OPTIONS
from app.ui.service_locator import get_dog_service, get_photo_service, resolve_photo_path
from app.ui.components import photo_grid, confirm_action

st.set_page_config(page_title="Dettaglio Cane", page_icon="🐕", layout="wide")

dog_service = get_dog_service()
photo_service = get_photo_service()

dog_id = st.session_state.get("ss_selected_dog_id")

if not dog_id:
    st.warning("No dog selected. Go back to catalog.")
    if st.button("← Catalog"):
        st.switch_page("pages/01_Catalog.py")
    st.stop()

dog, photos = dog_service.get_dog_with_photos(dog_id)

if dog is None:
    st.error("Dog not found.")
    st.stop()

# Header with formatted display name
st.title(f"🐕 {dog.format_display_name()}")
if st.button("← Catalog"):
    st.switch_page("pages/01_Catalog.py")

st.divider()

left_col, right_col = st.columns([1, 2])

with left_col:
    primary = photo_service.get_primary_photo(dog_id)
    if primary:
        full_path = resolve_photo_path(primary.file_path)
        p = Path(full_path)
        if p.exists():
            st.image(p.read_bytes(), width='stretch')
        else:
            st.caption("⚠️ File foto mancante")
    else:
        st.markdown(
            """<div style="background:#f0f0f0;height:200px;display:flex;
            align-items:center;justify-content:center;border-radius:8px;color:#aaa;">
            📷 No photo</div>""",
            unsafe_allow_html=True,
        )

    if dog.dead:
        st.error("⚠️ Dog marked as DEAD")
    if dog.location == "E":
        st.success("📍 Location: E")

with right_col:
    edit_mode = st.session_state.get("ss_detail_edit_mode", False)

    if not edit_mode:
        # Vista lettura
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"**Sex:** {dog.sex}")
            st.markdown(f"**Location:** {dog.location or '—'}")
            st.markdown(f"**Year:** {dog.year or '—'}")
        with col_b:
            st.markdown(f"**Tag:** {dog.tag_number if dog.tag_number is not None else '—'}")
            st.markdown(f"**Color:** {dog.color or '—'}")
            st.markdown(f"**Dead:** {'Yes' if dog.dead else 'No'}")

        if dog.notes:
            st.markdown(f"**Notes:** {dog.notes}")
        st.markdown(f"**Needs photo update:** {'Yes' if dog.needs_photo_update else 'No'}")
        if dog.created_at:
            st.caption(f"Created on {dog.created_at.strftime('%d/%m/%Y %H:%M')}")
        if dog.updated_at:
            st.caption(f"Updated on {dog.updated_at.strftime('%d/%m/%Y %H:%M')}")

        st.divider()
        btn1, btn2, btn3, btn4 = st.columns(4)
        with btn1:
            if st.button("✏️ Edit", width='stretch'):
                st.session_state["ss_detail_edit_mode"] = True
                st.rerun()
        with btn2:
            flag_label = "✅ Photo OK" if dog.needs_photo_update else "⚠️ Needs photo update"
            if st.button(flag_label, width='stretch'):
                dog_service.mark_needs_photo_update(dog_id, not dog.needs_photo_update)
                st.rerun()
        with btn3:
            if confirm_action("🗃️ Archive", "The dog will be archived.", f"archive_{dog_id}"):
                dog_service.archive_dog(dog_id)
                st.session_state.pop("ss_selected_dog_id", None)
                st.success("Dog archived.")
                st.switch_page("pages/01_Catalog.py")
        with btn4:
            if confirm_action("🗑️ Delete Dog", "This will permanently delete the dog and all photos.", f"delete_{dog_id}"):
                dog_service.delete_dog(dog_id)
                st.session_state.pop("ss_selected_dog_id", None)
                st.success("Dog permanently deleted.")
                st.switch_page("pages/01_Catalog.py")

    else:
        # Modalità modifica
        with st.form("edit_dog_form"):
            new_name = st.text_input("Name", value=dog.name)

            loc_idx = LOCATION_OPTIONS.index(dog.location) if dog.location in LOCATION_OPTIONS else 0
            new_location = st.selectbox("Location", LOCATION_OPTIONS, index=loc_idx)

            sex_options = ["M", "F", "Unknown"]
            sex_idx = sex_options.index(dog.sex) if dog.sex in sex_options else 0
            new_sex = st.selectbox("Sex", sex_options, index=sex_idx)

            new_year = st.text_input("Year", value=dog.year or "")

            col1, col2 = st.columns(2)
            with col1:
                new_tag = st.text_input(
                    "Tag number (1-999)",
                    value=str(dog.tag_number) if dog.tag_number is not None else "",
                )
            with col2:
                color_opts = ["(nessuno)"] + COLOR_OPTIONS
                color_idx = color_opts.index(dog.color) if dog.color in COLOR_OPTIONS else 0
                new_color_choice = st.selectbox("Color", color_opts, index=color_idx)

            new_dead = st.checkbox("Dead", value=dog.dead)
            new_notes = st.text_area("Notes", value=dog.notes)
            new_needs_update = st.checkbox("Needs photo update", value=dog.needs_photo_update)

            save_btn = st.form_submit_button("💾 Save changes", type="primary")
            cancel_btn = st.form_submit_button("Cancel")

        if save_btn:
            try:
                tag_number = None
                if new_tag.strip():
                    tag_number = int(new_tag.strip())
                new_color = new_color_choice if new_color_choice != "(nessuno)" else None
                dog_service.update_dog(
                    dog_id,
                    name=new_name,
                    sex=new_sex,
                    location=new_location,
                    notes=new_notes,
                    needs_photo_update=new_needs_update,
                    tag_number=tag_number,
                    color=new_color,
                    year=new_year.strip() or None,
                    dead=new_dead,
                )
                st.session_state["ss_detail_edit_mode"] = False
                st.success("Changes saved!")
                st.rerun()
            except ValueError as e:
                st.error(str(e))

        if cancel_btn:
            st.session_state["ss_detail_edit_mode"] = False
            st.rerun()

st.divider()

# Photo gallery
st.subheader("Photo gallery")

def on_set_primary(photo_id: int):
    photo_service.set_primary_photo(dog_id, photo_id)
    st.success("Photo set as primary.")
    st.rerun()

def on_delete_photo(photo_id: int):
    photo_service.delete_photo(photo_id)
    st.success("Photo removed.")
    st.rerun()

photo_grid(photos, on_set_primary=on_set_primary, on_delete=on_delete_photo)

# Upload new photo
st.subheader("Upload new photo")
with st.form("upload_photo_form"):
    uploaded_file = st.file_uploader("Select image", type=["jpg", "jpeg", "png", "webp"])
    photo_note = st.text_input("Optional note")
    set_primary_flag = st.checkbox("Set as primary photo")
    upload_btn = st.form_submit_button("📤 Upload photo", type="primary")

if upload_btn:
    if uploaded_file is None:
        st.error("Please select an image file.")
    else:
        try:
            photo_service.upload_photo(
                dog_id=dog_id,
                file_bytes=uploaded_file.read(),
                filename=uploaded_file.name,
                note=photo_note,
                set_as_primary=set_primary_flag,
            )
            st.success("Photo uploaded successfully!")
            st.rerun()
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Upload error: {e}")
