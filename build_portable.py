"""
build_portable.py — Builds a zero-install Windows portable bundle.

Run this script once from the project root:
    python build_portable.py

Output: dist/EthoDogCatalog_portable.zip (~70-100 MB)

The zip contains a self-contained Python 3.11 + all dependencies + the app.
End users just extract the zip and double-click "Avvia App.bat".
"""

import os
import shutil
import stat
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

PYTHON_VERSION = "3.11.9"
PYTHON_EMBED_URL = (
    f"https://www.python.org/ftp/python/{PYTHON_VERSION}/"
    f"python-{PYTHON_VERSION}-embed-amd64.zip"
)
GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"

PROJECT_ROOT = Path(__file__).parent.resolve()
DIST_DIR = PROJECT_ROOT / "dist"
BUNDLE_NAME = "EthoDogCatalog"
BUNDLE_DIR = DIST_DIR / BUNDLE_NAME
PYTHON_DIR = BUNDLE_DIR / "python"
SITE_PACKAGES = PYTHON_DIR / "Lib" / "site-packages"

# Packages to install (no pytest — not needed by end users)
PACKAGES = ["streamlit", "pillow", "reportlab", "pdfplumber"]

# Files/folders to copy from project root into the bundle
INCLUDE_ITEMS = ["app", ".streamlit", "scripts", "main.py", "requirements.txt"]

# ── Helpers ───────────────────────────────────────────────────────────────────

def _log(msg: str) -> None:
    print(f"  {msg}")


def _download(url: str, dest: Path) -> None:
    _log(f"Downloading {url.split('/')[-1]}…")
    urllib.request.urlretrieve(url, dest)


def _rmtree(path: Path) -> None:
    """Delete a directory tree, handling read-only files on Windows."""
    if not path.exists():
        return
    def _on_error(func, fpath, _):
        os.chmod(fpath, stat.S_IWRITE)
        func(fpath)
    shutil.rmtree(path, onerror=_on_error)


# ── Steps ─────────────────────────────────────────────────────────────────────

def step_clean():
    print("\n[1/8] Cleaning previous build…")
    _rmtree(BUNDLE_DIR)
    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)
    _log("Done.")


def step_download_python():
    print("\n[2/8] Downloading Python embeddable…")
    tmp_zip = DIST_DIR / f"python-{PYTHON_VERSION}-embed.zip"
    if not tmp_zip.exists():
        _download(PYTHON_EMBED_URL, tmp_zip)
    else:
        _log("Already downloaded, skipping.")

    _log("Extracting…")
    PYTHON_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(tmp_zip, "r") as zf:
        zf.extractall(PYTHON_DIR)
    _log(f"Extracted to {PYTHON_DIR}")


def step_patch_pth():
    """
    Enable site-packages in the embeddable Python.
    The file is named pythonXYZ._pth (e.g. python311._pth).
    We need to:
      1. Uncomment '#import site'  →  'import site'
      2. Add 'Lib\\site-packages' so our installed packages are found.
    """
    print("\n[3/8] Patching python._pth to enable site-packages…")
    pth_files = list(PYTHON_DIR.glob("python*._pth"))
    if not pth_files:
        print("  ERROR: could not find python*._pth file.")
        sys.exit(1)
    pth_file = pth_files[0]
    _log(f"Patching {pth_file.name}")

    content = pth_file.read_text(encoding="utf-8")
    # Uncomment import site
    content = content.replace("#import site", "import site")
    # Add Lib\site-packages if not already there
    if "Lib\\site-packages" not in content:
        content += "\nLib\\site-packages\n"
    pth_file.write_text(content, encoding="utf-8")
    _log("Patched.")


def step_install_pip():
    print("\n[4/8] Bootstrapping pip in embedded Python…")
    get_pip = DIST_DIR / "get-pip.py"
    if not get_pip.exists():
        _download(GET_PIP_URL, get_pip)
    else:
        _log("get-pip.py already downloaded.")

    SITE_PACKAGES.mkdir(parents=True, exist_ok=True)
    python_exe = PYTHON_DIR / "python.exe"
    _log("Running get-pip.py…")
    subprocess.run(
        [str(python_exe), str(get_pip), "--no-warn-script-location", "-q"],
        check=True,
    )
    _log("pip installed.")


def step_install_packages():
    print("\n[5/8] Installing packages into embedded Python…")
    python_exe = PYTHON_DIR / "python.exe"
    for pkg in PACKAGES:
        _log(f"Installing {pkg}…")
        subprocess.run(
            [
                str(python_exe), "-m", "pip", "install", pkg,
                "--target", str(SITE_PACKAGES),
                "--no-warn-script-location",
                "-q",
            ],
            check=True,
        )
    _log("All packages installed.")


def step_copy_app():
    print("\n[6/8] Copying application files…")
    for item in INCLUDE_ITEMS:
        src = PROJECT_ROOT / item
        dst = BUNDLE_DIR / item
        if not src.exists():
            _log(f"  Skipping {item} (not found)")
            continue
        if src.is_dir():
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
                "__pycache__", "*.pyc", ".pytest_cache", "*.egg-info"
            ))
        else:
            shutil.copy2(src, dst)
        _log(f"Copied {item}")

    # Create empty data dirs
    (BUNDLE_DIR / "data" / "media").mkdir(parents=True, exist_ok=True)
    (BUNDLE_DIR / "data" / "exports").mkdir(parents=True, exist_ok=True)
    _log("Created data/ directories.")


def step_write_launcher():
    print("\n[7/8] Writing launcher files…")

    bat_path = BUNDLE_DIR / "Avvia App.bat"
    bat_content = (
        "@echo off\r\n"
        "cd /d \"%~dp0\"\r\n"
        "echo.\r\n"
        "echo  ==========================================\r\n"
        "echo   Etho Dog Catalog Manager\r\n"
        "echo  ==========================================\r\n"
        "echo.\r\n"
        "echo  Avvio in corso...\r\n"
        "echo  Il browser si aprira' automaticamente.\r\n"
        "echo  Per chiudere l'app, chiudi questa finestra.\r\n"
        "echo.\r\n"
        "set CATALOG_ROOT=%~dp0\r\n"
        "timeout /t 2 /nobreak >nul\r\n"
        "start \"\" \"http://localhost:8501\"\r\n"
        "python\\python.exe -m streamlit run app\\ui\\Home.py "
        "--server.headless true --server.port 8501\r\n"
        "echo.\r\n"
        "echo  L'app si e' chiusa.\r\n"
        "pause\r\n"
    )
    bat_path.write_text(bat_content, encoding="utf-8")
    _log("Created 'Avvia App.bat'")

    leggimi_path = BUNDLE_DIR / "LEGGIMI.txt"
    leggimi_content = (
        "ETHO DOG CATALOG MANAGER\r\n"
        "========================\r\n"
        "\r\n"
        "COME AVVIARE L'APP\r\n"
        "------------------\r\n"
        "1. Estrai questo zip in una cartella (es. il Desktop)\r\n"
        "2. Apri la cartella EthoDogCatalog\r\n"
        "3. Fai doppio click su  \"Avvia App.bat\"\r\n"
        "4. Si apre una finestra nera — aspetta qualche secondo\r\n"
        "5. Il browser si apre automaticamente su http://localhost:8501\r\n"
        "\r\n"
        "DOVE SONO I TUOI DATI\r\n"
        "---------------------\r\n"
        "Tutti i dati (cani, foto, database) sono salvati nella cartella:\r\n"
        "   EthoDogCatalog\\data\\\r\n"
        "\r\n"
        "IMPORTANTE: non spostare o cancellare la cartella 'data'.\r\n"
        "Se vuoi fare un backup, copia l'intera cartella EthoDogCatalog\r\n"
        "su un disco esterno o nel cloud.\r\n"
        "\r\n"
        "COME CHIUDERE L'APP\r\n"
        "-------------------\r\n"
        "Chiudi la finestra nera del terminale.\r\n"
        "Puoi anche chiudere il browser — l'app continua a girare in background\r\n"
        "finche' la finestra nera e' aperta.\r\n"
        "\r\n"
        "PROBLEMI?\r\n"
        "---------\r\n"
        "- Il browser non si apre: apri manualmente http://localhost:8501\r\n"
        "- Messaggio 'Port already in use': chiudi le altre finestre nere\r\n"
        "  e riprova.\r\n"
        "- Antivirus blocca il .bat: e' normale per file .bat sconosciuti,\r\n"
        "  aggiungi un'eccezione per la cartella EthoDogCatalog.\r\n"
    )
    leggimi_path.write_text(leggimi_content, encoding="utf-8")
    _log("Created 'LEGGIMI.txt'")


def step_zip():
    print("\n[8/8] Creating zip archive…")
    zip_path = DIST_DIR / f"{BUNDLE_NAME}_portable.zip"
    if zip_path.exists():
        zip_path.unlink()

    file_count = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for file in BUNDLE_DIR.rglob("*"):
            if file.is_file():
                arcname = Path(BUNDLE_NAME) / file.relative_to(BUNDLE_DIR)
                zf.write(file, arcname)
                file_count += 1

    size_mb = zip_path.stat().st_size / (1024 * 1024)
    _log(f"Created {zip_path.name} ({size_mb:.1f} MB, {file_count} files)")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 50)
    print("  Etho Dog Catalog — Portable Bundle Builder")
    print("=" * 50)
    print(f"  Output: dist/{BUNDLE_NAME}_portable.zip")
    print(f"  Python: {PYTHON_VERSION} (embeddable, 64-bit)")
    print(f"  Packages: {', '.join(PACKAGES)}")

    DIST_DIR.mkdir(exist_ok=True)

    step_clean()
    step_download_python()
    step_patch_pth()
    step_install_pip()
    step_install_packages()
    step_copy_app()
    step_write_launcher()
    step_zip()

    print("\n" + "=" * 50)
    print("  BUILD COMPLETE")
    print(f"  >> dist/{BUNDLE_NAME}_portable.zip")
    print("=" * 50)
    print("\nTest instructions:")
    print("  1. Copy the zip to a PC without Python")
    print("  2. Extract → double-click 'Avvia App.bat'")
    print("  3. Browser opens at http://localhost:8501")


if __name__ == "__main__":
    main()
