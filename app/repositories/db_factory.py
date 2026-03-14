import os
from pathlib import Path
from app.repositories.database import Database


_db_instance: Database | None = None


def get_db() -> Database:
    global _db_instance
    if _db_instance is None:
        db_path = _resolve_db_path()
        _db_instance = Database(db_path)
        _db_instance.initialize_schema()
    return _db_instance


def reset_db() -> None:
    """Usato nei test per resettare il singleton."""
    global _db_instance
    _db_instance = None


def _resolve_db_path() -> str:
    catalog_root = os.environ.get("CATALOG_ROOT")
    if catalog_root:
        root = Path(catalog_root)
    else:
        # Risale dalla posizione di questo file al project root
        root = Path(__file__).parent.parent.parent

    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "media").mkdir(exist_ok=True)
    (data_dir / "exports").mkdir(exist_ok=True)

    return str(data_dir / "catalog.db")


def get_media_dir() -> str:
    catalog_root = os.environ.get("CATALOG_ROOT")
    if catalog_root:
        root = Path(catalog_root)
    else:
        root = Path(__file__).parent.parent.parent
    return str(root / "data" / "media")


def get_exports_dir() -> str:
    catalog_root = os.environ.get("CATALOG_ROOT")
    if catalog_root:
        root = Path(catalog_root)
    else:
        root = Path(__file__).parent.parent.parent
    return str(root / "data" / "exports")
