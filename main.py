"""
Entry point dell'applicazione Etho Dog Catalog Manager.

Uso:
    python main.py          — avvia l'app Streamlit
    streamlit run app/ui/Home.py  — alternativa diretta
"""
import os
import sys
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).parent.resolve()

    # Imposta la variabile d'ambiente usata da tutti i moduli
    os.environ["CATALOG_ROOT"] = str(project_root)

    # Crea le cartelle dati se non esistono
    (project_root / "data" / "media").mkdir(parents=True, exist_ok=True)
    (project_root / "data" / "exports").mkdir(parents=True, exist_ok=True)

    entry_page = str(project_root / "app" / "ui" / "Home.py")

    try:
        # Streamlit >= 1.12 supporta bootstrap.run
        from streamlit.web import bootstrap
        bootstrap.run(entry_page, "", [], {})
    except ImportError:
        # Fallback: lancia come sottoprocesso
        import subprocess
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", entry_page],
            check=True,
        )


if __name__ == "__main__":
    main()
