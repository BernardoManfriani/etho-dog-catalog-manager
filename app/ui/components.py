"""Componenti Streamlit riusabili condivisi tra le pagine."""
import base64
from pathlib import Path
from typing import Optional, Callable, Union

import streamlit as st

from app.models.dog import Dog
from app.models.photo import DogPhoto
from app.ui.service_locator import resolve_photo_path


def stats_metric_row(stats: dict) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Dogs", stats.get("total_active", 0))
    col2.metric("With Photo", stats.get("with_primary_photo", 0))
    col3.metric("Needs Photo Update", stats.get("needs_photo_update", 0))
    col4.metric("Added (7d)", stats.get("added_last_7_days", 0))


def dog_card(dog: Dog, photo: Optional[DogPhoto], key_prefix: str = "") -> bool:
    """
    Renderizza una card cane con:
    - etichetta formattata SOPRA la foto
    - bordo rosso + linea obliqua se dead=True
    - sfondo verde se location='E'
    Ritorna True se l'utente clicca su "Vedi dettaglio".
    """
    # Stili condizionali
    border_color = "#dc3545" if dog.dead else "#dee2e6"
    border_width = "3px" if dog.dead else "1px"
    bg_color = "#d4edda" if dog.location == "E" else "#ffffff"
    label_color = "#495057"

    # Overlay diagonale per cani dead
    overlay_html = ""
    if dog.dead:
        overlay_html = """
        <div style="
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: linear-gradient(
                to bottom right,
                transparent calc(50% - 2px),
                rgba(220,53,69,0.65) calc(50% - 2px),
                rgba(220,53,69,0.65) calc(50% + 2px),
                transparent calc(50% + 2px)
            );
            pointer-events: none;
            z-index: 10;
            border-radius: 7px;
        "></div>"""

    # Immagine
    img_html = _get_image_html(photo)

    # Etichetta formattata
    display_name = dog.format_display_name()
    # Escape HTML basico
    display_name_safe = display_name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    card_html = f"""
    <div style="
        background: {bg_color};
        border: {border_width} solid {border_color};
        border-radius: 8px;
        padding: 8px;
        margin-bottom: 4px;
        position: relative;
        overflow: hidden;
    ">
        {overlay_html}
        <div style="
            font-size: 11px;
            font-weight: 700;
            color: {label_color};
            margin-bottom: 6px;
            word-break: break-all;
            line-height: 1.4;
            font-family: monospace;
        ">{display_name_safe}</div>
        {img_html}
    </div>
    """
    st.html(card_html)
    return st.button("View details", key=f"{key_prefix}btn_{dog.id}", width='stretch')


def photo_grid(
    photos: list[DogPhoto],
    on_set_primary: Optional[Callable[[int], None]] = None,
    on_delete: Optional[Callable[[int], None]] = None,
    cols: int = 4,
) -> None:
    if not photos:
        st.info("No photos uploaded.")
        return

    columns = st.columns(cols)
    for i, photo in enumerate(photos):
        with columns[i % cols]:
            full_path = resolve_photo_path(photo.file_path)
            img_bytes = _safe_load_image(full_path)
            if img_bytes:
                st.image(img_bytes, width='stretch')
            else:
                st.caption("⚠️ Missing file")

            if photo.is_primary:
                st.success("✓ Primary", icon=None)
            elif on_set_primary:
                if st.button("Set as primary", key=f"primary_{photo.id}"):
                    on_set_primary(photo.id)

            if photo.note:
                st.caption(photo.note)

            if on_delete:
                if st.button("Delete", key=f"del_{photo.id}", type="secondary"):
                    on_delete(photo.id)


def filter_sidebar(locations: list[str]) -> dict:
    with st.sidebar:
        st.header("Filters")
        query = st.text_input("Search by name...", key="ss_filter_query")

        sex_options = ["All", "M", "F"]
        sex = st.selectbox("Sex", sex_options, key="ss_filter_sex")

        loc_options = ["All"] + locations
        location = st.selectbox("Location", loc_options, key="ss_filter_location")

        tag_raw = st.text_input("Tag number", placeholder="1–999", key="ss_filter_tag")
        tag_number: Optional[int] = None
        if tag_raw.strip().isdigit():
            tag_number = int(tag_raw.strip())

        needs_update = st.checkbox("Needs photo update only", key="ss_filter_needs_update")

        order_options = {
            "Name (A-Z)": "name",
            "Date added": "created_at",
            "Last updated": "updated_at",
        }
        order_label = st.selectbox("Sort by", list(order_options.keys()), key="ss_filter_order")
        order_by = order_options[order_label]

    return {
        "query": query,
        "sex": sex if sex != "All" else None,
        "location": location if location != "All" else None,
        "tag_number": tag_number,
        "needs_photo_update": True if needs_update else None,
        "order_by": order_by,
    }


def confirm_action(label: str, confirm_label: str, key: str) -> bool:
    confirm_key = f"confirm_state_{key}"
    if confirm_key not in st.session_state:
        st.session_state[confirm_key] = False

    if not st.session_state[confirm_key]:
        if st.button(label, key=f"btn_{key}", type="secondary"):
            st.session_state[confirm_key] = True
            st.rerun()
        return False
    else:
        st.warning(f"Are you sure? {confirm_label}")
        col1, col2 = st.columns(2)
        confirmed = col1.button("Yes, confirm", key=f"confirm_yes_{key}", type="primary")
        if col2.button("Cancel", key=f"confirm_no_{key}"):
            st.session_state[confirm_key] = False
            st.rerun()
        if confirmed:
            st.session_state[confirm_key] = False
            return True
        return False


def _get_image_html(photo: Optional[DogPhoto]) -> str:
    """Ritorna HTML per la foto come base64, o placeholder se mancante."""
    if photo and photo.file_path:
        full_path = resolve_photo_path(photo.file_path)
        img_bytes = _safe_load_image(full_path)
        if img_bytes:
            b64 = base64.b64encode(img_bytes).decode()
            return (
                f'<img src="data:image/jpeg;base64,{b64}" '
                f'style="width:100%;height:140px;object-fit:cover;'
                f'border-radius:4px;display:block;">'
            )
    return (
        '<div style="width:100%;height:140px;background:#f5f5f5;'
        'display:flex;align-items:center;justify-content:center;'
        'color:#bbb;font-size:13px;border-radius:4px;">📷 No photo</div>'
    )


def _safe_load_image(path: str) -> Optional[bytes]:
    try:
        p = Path(path)
        if p.exists():
            return p.read_bytes()
    except Exception:
        pass
    return None
