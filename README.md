# Etho Dog Catalog Manager

Applicazione locale per la gestione di un catalogo cani. Sostituisce il workflow manuale su PDF con un database locale + interfaccia web su browser.

## Prerequisiti

- Python 3.11 o superiore
- pip

## Installazione

```bash
# Clona o scarica il progetto
cd etho-dog-catalog-manager

# Installa le dipendenze
pip install -r requirements.txt
```

## Avvio

```bash
python main.py
```

Oppure direttamente con Streamlit:

```bash
streamlit run app/ui/Home.py
```

L'app sarà disponibile su: **http://localhost:8501**

## Primo avvio con dati demo

Per popolare il database con 20 cani di esempio:

```bash
python scripts/seed.py
```

## Struttura cartelle

```
etho-dog-catalog-manager/
├── app/
│   ├── models/          # Dataclass Dog, DogPhoto
│   ├── repositories/    # Accesso SQLite (DogRepository, PhotoRepository)
│   ├── services/        # Business logic (DogService, PhotoService, ExportService)
│   ├── utils/           # ImageUtils, BackupUtils, CsvUtils
│   ├── pdf/             # PdfGenerator (ReportLab)
│   └── ui/              # Pagine Streamlit
│       ├── Home.py      # Dashboard
│       └── pages/
│           ├── 01_Catalog.py
│           ├── 02_Dog_Detail.py
│           ├── 03_Add_Dog.py
│           ├── 04_Quick_Photo_Update.py
│           ├── 05_Export.py
│           └── 06_Archived.py
├── data/
│   ├── catalog.db       # Database SQLite
│   ├── media/           # Foto dei cani
│   └── exports/         # PDF e backup generati
├── scripts/
│   └── seed.py          # Dati demo
├── tests/               # Test pytest
├── main.py              # Entry point
└── requirements.txt
```

## Dove sono salvati i dati

| Dato | Percorso |
|------|----------|
| Database | `data/catalog.db` |
| Foto | `data/media/` |
| PDF esportati | `data/exports/` |
| Backup zip | `data/exports/` |

Le foto sono salvate come JPEG (max 1200px, qualità 85) con nomi univoci generati automaticamente.

## Come usare l'app

### Aggiungere un cane
1. Click su **➕ Aggiungi cane** dalla dashboard o dal menu laterale
2. Inserisci nome (obbligatorio), sesso, luogo, note
3. Carica una foto opzionale
4. Click **Salva**

### Cercare un cane
1. Apri **📋 Catalogo** dal menu
2. Usa la barra di ricerca in alto o i filtri nella sidebar (sesso, luogo, foto da aggiornare)

### Aggiornare la foto di un cane
1. Click su **📷 Aggiorna foto** dalla dashboard
2. Cerca il cane per nome
3. Clicca **Seleziona**
4. Carica la nuova foto
5. Click **Carica**

### Generare il PDF del catalogo
1. Apri **📄 Esporta** dal menu
2. Inserisci il titolo del PDF (opzionale)
3. Click **🖨️ Genera PDF**
4. Scarica il file con il pulsante che compare

## Come fare un backup

1. Apri **📄 Esporta**
2. Nella sezione **Backup Database**, click **💾 Crea backup**
3. Scarica il file `.zip` — contiene il database + tutte le foto

Per ripristinare: estrai il file zip e copia `catalog.db` in `data/` e le immagini in `data/media/`.

## Esportare/importare CSV

**Esporta:** Apri Esporta → click **Esporta CSV** → scarica.

**Importa:** Il CSV deve avere almeno la colonna `name`. Colonne opzionali: `sex`, `location`, `notes`.

Esempio CSV:
```csv
name,sex,location,notes
Rex,M,Rifugio A,Pastore tedesco
Luna,F,Rifugio B,
```

## Eseguire i test

```bash
pytest tests/
```

Per vedere l'output dettagliato:

```bash
pytest tests/ -v
```

## Impacchettare in .exe (Windows)

Installa PyInstaller:

```bash
pip install pyinstaller
```

Genera l'eseguibile:

```bash
pyinstaller --onefile --windowed \
  --add-data "app;app" \
  --add-data ".streamlit;.streamlit" \
  --add-data "data;data" \
  --name "EthoDogCatalog" \
  main.py
```

L'eseguibile verrà creato in `dist/EthoDogCatalog.exe`.

> **Nota:** Streamlit richiede che i suoi file statici siano inclusi. Potrebbe essere necessario aggiungere `--add-data` per la cartella Streamlit. Consulta la documentazione di PyInstaller per casi complessi.

Per packaging avanzato, considera `--collect-all streamlit`.

## Architettura

```
UI (Streamlit)
    ↓ chiama
Services (DogService, PhotoService, ExportService)
    ↓ chiama
Repositories (DogRepository, PhotoRepository)
    ↓ legge/scrive
SQLite (data/catalog.db)

Services → Utils (ImageUtils, BackupUtils, CsvUtils)
Services → PDF (PdfGenerator)
```

Ogni livello dipende solo da quello sotto. La UI non accede mai direttamente al DB.

## Limiti del MVP

- Nessuna autenticazione (uso locale monoUtente)
- Nessun sync remoto / cloud
- Import da vecchi PDF non supportato (usa import CSV)
- Nessun riconoscimento automatico del cane dalla foto
- Un solo utente alla volta (SQLite non è progettato per accessi concorrenti)

## Fase 2 (future)

- Deploy su VPS/server (Flask/FastAPI + PostgreSQL)
- Multiutenza con autenticazione
- Sync foto su S3 o storage remoto
- Import OCR da PDF
- Notifiche automatiche per cani con foto vecchie
