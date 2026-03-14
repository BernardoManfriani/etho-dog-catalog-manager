import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import streamlit as st

from app.ui.service_locator import get_export_service
from app.utils.backup_utils import BackupUtils

st.set_page_config(page_title="Export", page_icon="📄", layout="centered")
st.title("📄 Export & Backup")

export_service = get_export_service()

# --- PDF Export ---
st.subheader("Export PDF Catalog")

pdf_title = st.text_input("PDF Title", value="Dog Catalog")
if st.button("🖨️ Generate PDF", type="primary"):
    with st.spinner("Generating PDF..."):
        try:
            pdf_path = export_service.export_pdf(title=pdf_title)
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            st.download_button(
                label="⬇️ Download PDF",
                data=pdf_bytes,
                file_name=Path(pdf_path).name,
                mime="application/pdf",
            )
            st.success(f"PDF generated: {Path(pdf_path).name}")
        except Exception as e:
            st.error(f"PDF generation error: {e}")

st.divider()

# --- CSV Export ---
st.subheader("Export CSV")
if st.button("📊 Export CSV"):
    try:
        csv_str = export_service.export_csv()
        st.download_button(
            label="⬇️ Download CSV",
            data=csv_str,
            file_name="dogs_export.csv",
            mime="text/csv",
        )
    except Exception as e:
        st.error(f"CSV export error: {e}")

st.divider()

# --- CSV Import ---
st.subheader("Import from CSV")
st.caption(
    "The CSV must have at least the `name` column. "
    "Optional columns: `sex`, `location`, `notes`."
)
csv_file = st.file_uploader("Upload CSV file", type=["csv"])

if csv_file:
    if st.button("📥 Import dogs from CSV", type="primary"):
        with st.spinner("Importing..."):
            try:
                content = csv_file.read().decode("utf-8")
                result = export_service.import_csv(content)
                st.success(f"✅ Imported {result['created']} dogs.")
                if result["skipped"]:
                    st.warning(f"{result['skipped']} rows skipped.")
                if result["errors"]:
                    with st.expander("Error details"):
                        for err in result["errors"]:
                            st.text(err)
            except Exception as e:
                st.error(f"Import error: {e}")

st.divider()

# --- Backup ---
st.subheader("Database Backup")
st.caption(
    "Creates a zip file with the SQLite database and all photos. "
    "Keep it in a safe place."
)
if st.button("💾 Create backup"):
    with st.spinner("Creating backup..."):
        try:
            zip_path = export_service.create_backup()
            size_mb = BackupUtils.get_backup_size_mb(zip_path)
            with open(zip_path, "rb") as f:
                zip_bytes = f.read()
            st.download_button(
                label="⬇️ Download Backup",
                data=zip_bytes,
                file_name=Path(zip_path).name,
                mime="application/zip",
            )
            st.success(f"Backup created: {Path(zip_path).name} ({size_mb:.1f} MB)")
        except Exception as e:
            st.error(f"Backup error: {e}")
