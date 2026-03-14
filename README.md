# Etho Dog Catalog Manager

A local app for managing a dog catalog — photos, locations, coat colors, PDF export and more.

> **Developer?** Jump to [Developer Setup](#developer-setup) at the bottom.

---

## For All Users

### Download and run (no installation required)

1. Go to the [**Releases page**](https://github.com/BernardoManfriani/etho-dog-catalog-manager/releases/latest)
2. Download **EthoDogCatalog_portable.zip**
3. Extract the zip anywhere (e.g. your Desktop)
4. Double-click **`Avvia App.bat`**
5. The browser opens automatically at **http://localhost:8501**

No Python, no pip, no Git required. Works on Windows 10/11 (64-bit).

---

### Your data

All your data (dogs, photos, database) is saved in the `data/` folder inside the extracted directory.

**Do not move or delete the `data/` folder.**

To back up your data: copy the entire `EthoDogCatalog` folder to an external drive or cloud storage.

To restore: paste the folder back and launch `Avvia App.bat` as usual.

---

### How to use the app

#### Add a dog
1. Click **➕ Add dog** from the dashboard
2. Fill in name (required), location, sex, year, and coat color
3. Optionally add tag number, tag color, notes, and a photo
4. Click **💾 Add dog**

#### Browse the catalog
- Open **📋 Catalog** from the sidebar
- Switch between the 5 color tabs: **White / Light tan / Dark brown / Brindle / Black**
- Use the sidebar filters to search by name, sex, location, or tag number

#### Update a photo
1. Click **📷 Update photo** from the dashboard
2. Search the dog by name → click **Select**
3. Upload the new photo

#### Generate a PDF catalog
1. Open **📄 Export**
2. Set a title (optional) and click **🖨️ Generate PDF**
3. Download the file

#### Import dogs from an existing PDF
1. Click **📥 Import** from the dashboard
2. Upload a cheat-sheet PDF (format: `Name ♂/♀ Location` per dog)
3. Review the list, assign a coat color, click **Import**

#### Bulk delete
- **Catalog**: enable **"Select mode"** in the sidebar → pick dogs → **Delete selected**
- **Archived**: use checkboxes per row or **Delete ALL archived**

#### Close the app
Close the black terminal window. Your data is automatically saved.

---

### Troubleshooting

| Problem | Solution |
|---------|----------|
| Browser doesn't open | Open http://localhost:8501 manually |
| "Port already in use" | Close other black terminal windows and retry |
| Antivirus blocks the .bat | Add an exception for the `EthoDogCatalog` folder |

---
---

## Developer Setup

### Requirements

- Python 3.11+
- pip
- Git

### Installation

```bash
git clone https://github.com/BernardoManfriani/etho-dog-catalog-manager.git
cd etho-dog-catalog-manager

python -m venv .venv

# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### Run

```bash
python main.py
# or:
streamlit run app/ui/Home.py
```

Open **http://localhost:8501**

### Load demo data

```bash
python scripts/seed.py
```

### Run tests

```bash
pytest tests/
pytest tests/ -v   # verbose
```

### Project structure

```
etho-dog-catalog-manager/
├── app/
│   ├── models/           # Dog, DogPhoto dataclasses
│   ├── repositories/     # SQLite access (DogRepository, PhotoRepository)
│   ├── services/         # Business logic (DogService, PhotoService, ExportService)
│   ├── utils/            # ImageUtils, BackupUtils, CsvUtils, PdfImportUtils
│   ├── pdf/              # PdfGenerator (ReportLab)
│   └── ui/
│       ├── Home.py       # Dashboard
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
├── data/                 # Auto-created at runtime (gitignored)
├── scripts/seed.py       # Demo data
├── tests/
├── build_portable.py     # Builds the distributable zip
├── main.py
└── requirements.txt
```

### Architecture

```
UI (Streamlit pages)
    ↓
Services (DogService, PhotoService, ExportService)
    ↓
Repositories (DogRepository, PhotoRepository)
    ↓
SQLite — data/catalog.db
```

### Dog fields

| Field | Required | Values |
|-------|----------|--------|
| Name | Yes | free text |
| Sex | Yes | M / F |
| Location | Yes | TH, IF, DR, JS, BB, WC, E, k17, k18 |
| Year | Yes | free text |
| Coat color | No | White / Light tan / Dark brown / Brindle / Black |
| Tag number | No | 1–999 |
| Tag color | No | Y / B / O / P |
| Notes | No | free text |
| Dead | No | bool — red border + diagonal line in UI and PDF |

Display name format: `Name_Location_Sex_TagNumber&TagColor_Year_(dead)`

### Build the portable zip

```bash
python build_portable.py
# Output: dist/EthoDogCatalog_portable.zip (~137 MB)
```

### Publish a new release

```bash
git tag v1.x.x
git push origin v1.x.x
gh release create v1.x.x dist/EthoDogCatalog_portable.zip \
  --title "v1.x.x" --notes "..."
```

### Known limitations

- No authentication — single-user local use only
- SQLite is not designed for concurrent multi-user access
- No remote sync or cloud storage
- PDF import works best with cheat-sheet PDFs using the `Name ♂/♀ Location` format
