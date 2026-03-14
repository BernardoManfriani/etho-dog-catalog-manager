import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import streamlit as st

from app.models.dog import COAT_OPTIONS
from app.ui.service_locator import get_dog_service, get_photo_service
from app.ui.components import dog_card, filter_sidebar, confirm_action

st.set_page_config(page_title="Dog Catalog", page_icon="📋", layout="wide")
st.title("📋 Dog Catalog")

dog_service = get_dog_service()
photo_service = get_photo_service()

locations = dog_service.get_distinct_locations()
filters = filter_sidebar(locations)

# ── Bulk delete section (sidebar) ────────────────────────────────────────────
with st.sidebar:
    st.divider()
    st.subheader("Bulk Delete")
    bulk_mode = st.toggle("Enable select mode", key="ss_bulk_mode")

# ── Sub-catalog tabs ─────────────────────────────────────────────────────────
tab_labels = ["🐾 All"] + COAT_OPTIONS
tabs = st.tabs(tab_labels)


def _render_dogs(dogs, tab_key_prefix, bulk_mode_on):
    if not dogs:
        st.info("No dogs found.")
        return

    st.caption(f"{len(dogs)} dogs found")

    if bulk_mode_on:
        # ── Selection UI ─────────────────────────────────────────────────────
        sel_key = f"catalog_sel_{tab_key_prefix}"
        if sel_key not in st.session_state:
            st.session_state[sel_key] = []

        dog_options = {f"{dog.format_display_name()} (#{dog.id})": dog.id for dog in dogs}

        ba1, ba2 = st.columns(2)
        with ba1:
            if st.button("☑️ Select all", key=f"selall_{tab_key_prefix}"):
                st.session_state[sel_key] = list(dog_options.values())
                st.rerun()
        with ba2:
            if st.button("⬜ Deselect all", key=f"deselall_{tab_key_prefix}"):
                st.session_state[sel_key] = []
                st.rerun()

        selected_ids = st.multiselect(
            "Select dogs to delete",
            options=list(dog_options.keys()),
            default=[k for k, v in dog_options.items() if v in st.session_state[sel_key]],
            key=f"ms_{tab_key_prefix}",
        )
        # Sync back to session state
        st.session_state[sel_key] = [dog_options[k] for k in selected_ids if k in dog_options]
        chosen_ids = st.session_state[sel_key]

        if chosen_ids:
            if confirm_action(
                f"🗑️ Delete selected ({len(chosen_ids)})",
                "Permanently delete selected dogs and all their photos. Cannot be undone.",
                f"bulk_del_{tab_key_prefix}",
            ):
                for dog_id in chosen_ids:
                    dog_service.delete_dog(dog_id)
                st.session_state[sel_key] = []
                st.success(f"Deleted {len(chosen_ids)} dog(s).")
                st.rerun()

        if confirm_action(
            f"🗑️ Delete ALL shown ({len(dogs)})",
            f"Permanently delete all {len(dogs)} dogs currently displayed.",
            f"bulk_del_all_{tab_key_prefix}",
        ):
            for dog in dogs:
                dog_service.delete_dog(dog.id)
            st.session_state[sel_key] = []
            st.success(f"Deleted {len(dogs)} dog(s).")
            st.rerun()

        st.divider()

    # ── Card grid ─────────────────────────────────────────────────────────────
    cols_per_row = 4
    columns = st.columns(cols_per_row)
    for i, dog in enumerate(dogs):
        primary_photo = photo_service.get_primary_photo(dog.id)
        with columns[i % cols_per_row]:
            clicked = dog_card(dog, primary_photo, key_prefix=f"{tab_key_prefix}_{i}_")
            if clicked:
                st.session_state["ss_selected_dog_id"] = dog.id
                st.switch_page("pages/02_Dog_Detail.py")


# "All" tab
with tabs[0]:
    dogs = dog_service.get_catalog_page(**filters)
    _render_dogs(dogs, "all", st.session_state.get("ss_bulk_mode", False))

# One tab per coat color
for idx, coat in enumerate(COAT_OPTIONS):
    with tabs[idx + 1]:
        if st.button(f"➕ Add {coat} dog", key=f"add_coat_{coat}"):
            st.session_state["ss_preset_coat_color"] = coat
            st.switch_page("pages/03_Add_Dog.py")
        dogs = dog_service.get_catalog_page(**filters, coat_color=coat)
        tab_key = coat.replace(" ", "_").lower()
        _render_dogs(dogs, tab_key, st.session_state.get("ss_bulk_mode", False))
