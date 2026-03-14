import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import streamlit as st

from app.models.dog import LOCATION_OPTIONS, COAT_OPTIONS
from app.ui.service_locator import get_dog_service
from app.utils.pdf_import_utils import parse_pdf

st.set_page_config(page_title="Import", page_icon="📥", layout="wide")
st.title("📥 Import Dogs")
st.caption("Import dogs from a cheat-sheet PDF or a CSV file.")

dog_service = get_dog_service()

tab_pdf, tab_csv = st.tabs(["📄 PDF import", "📊 CSV import"])

# ── PDF import ────────────────────────────────────────────────────────────────
with tab_pdf:
    st.subheader("Upload cheat-sheet PDF")
    st.info(
        "Expected format: one PDF page per color group. "
        "Each page lists dogs as 'Name ♂/♀ Location' in the header text block."
    )

    uploaded_pdf = st.file_uploader("Choose PDF file", type=["pdf"], key="pdf_upload")

    if uploaded_pdf:
        with st.spinner("Parsing PDF…"):
            try:
                entries = parse_pdf(uploaded_pdf.read())
            except Exception as e:
                st.error(f"Could not parse PDF: {e}")
                st.stop()

        if not entries:
            st.warning("No dog entries found in the PDF.")
            st.stop()

        st.success(f"Found **{len(entries)}** entries in the PDF.")

        # Global coat color override
        coat_detected = entries[0].get("coat_hint", "") if entries else ""
        coat_options_list = ["(auto-detect from PDF)"] + COAT_OPTIONS
        default_coat_idx = (coat_options_list.index(coat_detected)
                            if coat_detected in coat_options_list else 0)
        global_coat = st.selectbox(
            "Assign coat color to all imported dogs",
            coat_options_list,
            index=default_coat_idx,
        )

        st.divider()
        st.subheader("Preview — edit before importing")

        # Build editable table state
        if "import_rows" not in st.session_state or st.session_state.get("import_source") != uploaded_pdf.name:
            st.session_state["import_rows"] = [
                {
                    "import": True,
                    "name": e["name"],
                    "sex": e["sex"],
                    "location": e["location"],
                    "location_raw": e.get("location_raw", ""),
                    "coat_hint": e.get("coat_hint", ""),
                }
                for e in entries
            ]
            st.session_state["import_source"] = uploaded_pdf.name

        rows = st.session_state["import_rows"]

        # Show editable rows
        for i, row in enumerate(rows):
            col_chk, col_name, col_sex, col_loc, col_loc_raw = st.columns([0.5, 2, 1, 1.5, 2])
            with col_chk:
                rows[i]["import"] = st.checkbox("", value=row["import"], key=f"imp_chk_{i}")
            with col_name:
                rows[i]["name"] = st.text_input("Name", value=row["name"], key=f"imp_name_{i}", label_visibility="collapsed")
            with col_sex:
                sex_idx = ["Unknown", "M", "F"].index(row["sex"]) if row["sex"] in ["Unknown", "M", "F"] else 0
                rows[i]["sex"] = st.selectbox("Sex", ["Unknown", "M", "F"], index=sex_idx, key=f"imp_sex_{i}", label_visibility="collapsed")
            with col_loc:
                loc_opts = [""] + LOCATION_OPTIONS
                loc_idx = loc_opts.index(row["location"]) if row["location"] in loc_opts else 0
                rows[i]["location"] = st.selectbox("Location", loc_opts, index=loc_idx, key=f"imp_loc_{i}", label_visibility="collapsed")
            with col_loc_raw:
                st.caption(f"PDF: {row['location_raw']}")

        st.divider()
        selected = [r for r in rows if r["import"] and r["name"].strip()]
        st.caption(f"{len(selected)} dogs selected for import.")

        if st.button(f"💾 Import {len(selected)} dogs", type="primary", disabled=len(selected) == 0):
            # Check for existing names to avoid duplicates
            existing = {d.name.lower() for d in dog_service.search_dogs(status="active")}
            existing |= {d.name.lower() for d in dog_service.search_dogs(status="archived")}

            added, skipped = 0, 0
            for r in selected:
                if r["name"].strip().lower() in existing:
                    skipped += 1
                    continue
                coat = global_coat if global_coat != "(auto-detect from PDF)" else r.get("coat_hint") or None
                try:
                    dog_service.create_dog(
                        name=r["name"].strip(),
                        sex=r["sex"],
                        location=r["location"],
                        coat_color=coat if coat in COAT_OPTIONS else None,
                    )
                    added += 1
                except Exception:
                    skipped += 1

            st.success(f"✅ Imported **{added}** dogs. Skipped **{skipped}** (duplicates or errors).")
            del st.session_state["import_rows"]
            del st.session_state["import_source"]

# ── CSV import ────────────────────────────────────────────────────────────────
with tab_csv:
    st.subheader("Upload CSV file")

    st.download_button(
        "⬇️ Download CSV template",
        data="name,sex,location,notes,tag_number,color,year,dead,coat_color\n"
             "Rex,M,BB,Example dog,,,2023,False,Black\n",
        file_name="import_template.csv",
        mime="text/csv",
    )

    uploaded_csv = st.file_uploader("Choose CSV file", type=["csv"], key="csv_upload")

    if uploaded_csv:
        import csv, io as _io
        content = uploaded_csv.read().decode("utf-8", errors="replace")
        reader = list(csv.DictReader(_io.StringIO(content)))

        if not reader:
            st.warning("CSV is empty.")
            st.stop()

        required_cols = {"name"}
        missing = required_cols - set(reader[0].keys())
        if missing:
            st.error(f"Missing required columns: {missing}")
            st.stop()

        st.success(f"Found **{len(reader)}** rows.")
        st.dataframe(reader[:10])  # preview first 10

        if st.button(f"💾 Import {len(reader)} rows from CSV", type="primary"):
            existing = {d.name.lower() for d in dog_service.search_dogs(status="active")}
            existing |= {d.name.lower() for d in dog_service.search_dogs(status="archived")}

            added, skipped = 0, 0
            for row in reader:
                name = row.get("name", "").strip()
                if not name or name.lower() in existing:
                    skipped += 1
                    continue
                try:
                    tn_raw = row.get("tag_number", "").strip()
                    tn = int(tn_raw) if tn_raw.isdigit() else None
                    dead_raw = row.get("dead", "").strip().lower()
                    dead = dead_raw in ("true", "1", "yes")
                    coat = row.get("coat_color", "").strip() or None
                    if coat and coat not in COAT_OPTIONS:
                        coat = None
                    dog_service.create_dog(
                        name=name,
                        sex=row.get("sex", "Unknown").strip() or "Unknown",
                        location=row.get("location", "").strip(),
                        notes=row.get("notes", "").strip(),
                        tag_number=tn,
                        color=row.get("color", "").strip() or None,
                        year=row.get("year", "").strip() or None,
                        dead=dead,
                        coat_color=coat,
                    )
                    added += 1
                except Exception:
                    skipped += 1

            st.success(f"✅ Imported **{added}** dogs. Skipped **{skipped}**.")
