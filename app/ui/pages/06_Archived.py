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

    # ── Bulk actions bar ─────────────────────────────────────────────────────
    sel_key = "archived_selected_ids"
    if sel_key not in st.session_state:
        st.session_state[sel_key] = set()

    bar_col1, bar_col2, bar_col3 = st.columns([1, 1, 4])
    with bar_col1:
        if st.button("☑️ Select all", width='stretch'):
            st.session_state[sel_key] = {d.id for d in archived_dogs}
            st.rerun()
    with bar_col2:
        if st.button("⬜ Deselect all", width='stretch'):
            st.session_state[sel_key] = set()
            st.rerun()

    selected = st.session_state[sel_key]

    if selected:
        st.warning(f"**{len(selected)} dog(s) selected.**")
        del_col1, del_col2 = st.columns(2)
        with del_col1:
            if confirm_action(
                f"🗑️ Delete selected ({len(selected)})",
                "Permanently delete selected dogs and all their photos.",
                "bulk_del_selected",
            ):
                for dog_id in list(selected):
                    dog_service.delete_dog(dog_id)
                st.session_state[sel_key] = set()
                st.success("Deleted.")
                st.rerun()
        with del_col2:
            if confirm_action(
                "🗑️ Delete ALL archived",
                f"Permanently delete all {len(archived_dogs)} archived dogs.",
                "bulk_del_all_archived",
            ):
                for dog in archived_dogs:
                    dog_service.delete_dog(dog.id)
                st.session_state[sel_key] = set()
                st.success("All archived dogs deleted.")
                st.rerun()
    else:
        if confirm_action(
            "🗑️ Delete ALL archived",
            f"Permanently delete all {len(archived_dogs)} archived dogs.",
            "bulk_del_all_archived",
        ):
            for dog in archived_dogs:
                dog_service.delete_dog(dog.id)
            st.session_state[sel_key] = set()
            st.success("All archived dogs deleted.")
            st.rerun()

    st.divider()

    # ── Dog rows ─────────────────────────────────────────────────────────────
    for dog in archived_dogs:
        with st.container(border=True):
            chk_col, name_col, date_col, restore_col, del_col = st.columns([0.4, 3, 2, 1, 1])
            with chk_col:
                checked = st.checkbox(
                    "", value=(dog.id in selected), key=f"chk_{dog.id}", label_visibility="collapsed"
                )
                if checked:
                    st.session_state[sel_key].add(dog.id)
                else:
                    st.session_state[sel_key].discard(dog.id)
            with name_col:
                st.markdown(f"**{dog.name}**")
                meta_parts = []
                if dog.sex and dog.sex != "Unknown":
                    meta_parts.append(dog.display_sex())
                if dog.location:
                    meta_parts.append(dog.location)
                if dog.coat_color:
                    meta_parts.append(dog.coat_color)
                if meta_parts:
                    st.caption(" · ".join(meta_parts))
            with date_col:
                if dog.updated_at:
                    st.caption(f"Archived: {dog.updated_at.strftime('%d/%m/%Y')}")
            with restore_col:
                if st.button("♻️ Restore", key=f"restore_{dog.id}"):
                    dog_service.restore_dog(dog.id)
                    st.session_state[sel_key].discard(dog.id)
                    st.success(f"'{dog.name}' restored!")
                    st.rerun()
            with del_col:
                if confirm_action("🗑️ Delete", "Permanent deletion.", f"del_{dog.id}"):
                    dog_service.delete_dog(dog.id)
                    st.session_state[sel_key].discard(dog.id)
                    st.rerun()
