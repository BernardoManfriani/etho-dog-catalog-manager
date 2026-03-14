# Etho Dog Catalog Manager

A local-first web app for managing a dog catalog. Built with Python and Streamlit — runs entirely on your machine, no internet or cloud required.

Dogs are organized by coat color (White, Light tan, Dark brown, Brindle, Black), each with photos, location, sex, tag number, year, and status. You can generate PDF catalogs, import dogs from existing cheat-sheet PDFs, export/import CSV, and create full backups.

---

## Requirements

- Python 3.11 or higher
- pip

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/etho-dog-catalog-manager.git
cd etho-dog-catalog-manager

# 2. Create a virtual environment (recommended)
python -m venv .venv

# Activate it:
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Running the app

```bash
python main.py
```

Or directly with Streamlit:

```bash
streamlit run app/ui/Home.py
```

Then open your browser at: **http://localhost:8501**

---

## Load demo data (optional)

To pre-populate the database with 20 example dogs:

```bash
python scripts/seed.py
```

---

## Pages overview

| Page | What it does |
|------|-------------|
| **Home** | Dashboard with stats and quick action buttons |
| **Catalog** | Browse dogs in 5 color sub-catalogs (White, Light tan, Dark brown, Brindle, Black). Search, filter, bulk delete. |
| **Dog Detail** | View/edit a dog's info, manage photos, archive or permanently delete |
| **Add Dog** | Add a new dog with all fields and an optional photo |
| **Quick Photo Update** | Fast two-step screen: search a dog → upload a new photo |
| **Export** | Generate PDF catalog, export/import CSV, create a zip backup |
| **Archived** | View archived dogs, restore or permanently delete, bulk delete |
| **Import** | Import dogs from a cheat-sheet PDF or a CSV file |

---

## How to use

### Add a dog
1. Click **➕ Add dog** from the dashboard or the sidebar
2. Fill in the name (required), location, sex, year, coat color
3. Optionally add tag number, tag color, notes, and a photo
4. Click **💾 Add dog**

### Search and filter
1. Open **📋 Catalog** from the sidebar
2. Use the sidebar filters: search by name, sex, location, tag number, needs-photo-update
3. Switch between color sub-catalog tabs to browse by coat color

### Update a dog's photo
1. Click **📷 Update photo** from the dashboard
2. Search the dog by name and click **Select**
3. Upload the new photo

### Generate a PDF catalog
1. Open **📄 Export**
2. Set a title (optional) and click **🖨️ Generate PDF**
3. Download the file — cards show name, location, sex, tag, coat color, year, and notes

### Import dogs from a PDF
1. Click **📥 Import** from the dashboard (or open it from the sidebar)
2. Upload a cheat-sheet PDF with the format: `Name ♂/♀ Location` per dog
3. Review the extracted list, adjust if needed, assign a coat color, then click **Import**

### Import dogs from CSV
Go to **Import → CSV tab**. Download the template, fill it in, and upload. Required column: `name`. Optional: `sex`, `location`, `notes`, `tag_number`, `color`, `year`, `dead`, `coat_color`.

### Bulk delete
- In the **Catalog**: enable **"Select mode"** in the sidebar → pick dogs from the multiselect list → **Delete selected** or **Delete ALL shown**
- In **Archived**: use per-row checkboxes or **Delete ALL archived**

### Backup and restore
1. Open **Export → Backup section** → click **💾 Create backup**
2. Download the `.zip` file — it contains the database and all photos

To restore: extract the zip, copy `catalog.db` into `data/` and the images into `data/media/`.

---

## Where data is stored

| Data | Path |
|------|------|
| Database | `data/catalog.db` |
| Photos | `data/media/` |
| Exported PDFs | `data/exports/` |
| Backup zips | `data/exports/` |

> **Note:** `data/` is listed in `.gitignore` — your dogs, photos, and database will never be accidentally pushed to GitHub.

Photos are automatically resized to max 1200px and saved as JPEG (quality 85) with a unique filename.

---

## Dog fields

| Field | Required | Notes |
|-------|----------|-------|
| Name | Yes | |
| Sex | Yes | M / F |
| Location | Yes | TH, IF, DR, JS, BB, WC, E, k17, k18 |
| Year | Yes | |
| Coat color | No | White / Light tan / Dark brown / Brindle / Black — determines which sub-catalog the dog appears in |
| Tag number | No | 1–999 |
| Tag color | No | Y / B / O / P |
| Notes | No | Free text |
| Dead | No | Shows red border + diagonal line in catalog and PDF |

The display name shown in cards and PDFs is auto-formatted as:
```
Name_Location_Sex_TagNumber&TagColor_Year_(dead)
```

---

## Running tests

```bash
pytest tests/
```

For verbose output:

```bash
pytest tests/ -v
```

---

## Project structure

```
etho-dog-catalog-manager/
├── app/
│   ├── models/          # Dog, DogPhoto dataclasses
│   ├── repositories/    # SQLite access (DogRepository, PhotoRepository)
│   ├── services/        # Business logic (DogService, PhotoService, ExportService)
│   ├── utils/           # ImageUtils, BackupUtils, CsvUtils, PdfImportUtils
│   ├── pdf/             # PdfGenerator (ReportLab)
│   └── ui/
│       ├── Home.py      # Dashboard
│       ├── components.py
│       ├── service_locator.py
│       └── pages/
│           ├── 01_Catalog.py
│           ├── 02_Dog_Detail.py
│           ├── 03_Add_Dog.py
│           ├── 04_Quick_Photo_Update.py
│           ├── 05_Export.py
│           ├── 06_Archived.py
│           └── 07_Import.py
├── data/                # Auto-created at first launch (gitignored)
│   ├── catalog.db
│   ├── media/
│   └── exports/
├── scripts/
│   └── seed.py
├── tests/
├── main.py
└── requirements.txt
```

---

## Architecture

```
UI (Streamlit pages)
    ↓
Services (DogService, PhotoService, ExportService)
    ↓
Repositories (DogRepository, PhotoRepository)
    ↓
SQLite — data/catalog.db
```

Each layer only depends on the one below it. UI never touches the database directly.

---

## Known limitations

- No authentication — designed for single-user local use
- No remote sync or cloud storage
- SQLite is not designed for concurrent multi-user access
- PDF import works best with cheat-sheet PDFs using the `Name ♂/♀ Location` format; complex layouts may need manual correction after import

---

## Packaging as a standalone .exe (Windows)

```bash
pip install pyinstaller

pyinstaller --onefile --windowed \
  --add-data "app;app" \
  --add-data ".streamlit;.streamlit" \
  --name "EthoDogCatalog" \
  main.py
```

The executable will be created at `dist/EthoDogCatalog.exe`.
