"""
Modulo di wiring: crea e restituisce le istanze dei servizi.
Usato da tutte le pagine Streamlit per evitare duplicazione.
"""
import os
from pathlib import Path

from app.repositories.db_factory import get_db, get_media_dir, get_exports_dir
from app.repositories.dog_repository import DogRepository
from app.repositories.photo_repository import PhotoRepository
from app.services.dog_service import DogService
from app.services.photo_service import PhotoService
from app.services.export_service import ExportService


def _get_project_root() -> str:
    root = os.environ.get("CATALOG_ROOT")
    if root:
        return root
    return str(Path(__file__).parent.parent.parent)


def get_dog_service() -> DogService:
    db = get_db()
    return DogService(DogRepository(db), PhotoRepository(db))


def get_photo_service() -> PhotoService:
    db = get_db()
    return PhotoService(PhotoRepository(db), DogRepository(db), get_media_dir())


def get_export_service() -> ExportService:
    db = get_db()
    dog_repo = DogRepository(db)
    photo_repo = PhotoRepository(db)
    dog_svc = DogService(dog_repo, photo_repo)
    photo_svc = PhotoService(photo_repo, dog_repo, get_media_dir())
    root = _get_project_root()
    db_path = str(Path(root) / "data" / "catalog.db")
    return ExportService(dog_svc, photo_svc, get_media_dir(), get_exports_dir(), db_path)


def resolve_photo_path(relative_path: str) -> str:
    """Converte un percorso relativo in assoluto."""
    return str(Path(_get_project_root()) / relative_path)
