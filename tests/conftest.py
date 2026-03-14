import os
import pytest
from pathlib import Path

from app.repositories.database import Database
from app.repositories.dog_repository import DogRepository
from app.repositories.photo_repository import PhotoRepository
from app.services.dog_service import DogService
from app.services.photo_service import PhotoService


@pytest.fixture(autouse=True)
def set_catalog_root(tmp_path):
    """Imposta CATALOG_ROOT nella cartella temp per ogni test."""
    os.environ["CATALOG_ROOT"] = str(tmp_path)
    yield
    os.environ.pop("CATALOG_ROOT", None)


@pytest.fixture
def tmp_db(tmp_path):
    db = Database(str(tmp_path / "test.db"))
    db.initialize_schema()
    return db


@pytest.fixture
def tmp_media(tmp_path):
    media = tmp_path / "media"
    media.mkdir()
    return str(media)


@pytest.fixture
def dog_repo(tmp_db):
    return DogRepository(tmp_db)


@pytest.fixture
def photo_repo(tmp_db):
    return PhotoRepository(tmp_db)


@pytest.fixture
def dog_service(dog_repo, photo_repo):
    return DogService(dog_repo, photo_repo)


@pytest.fixture
def photo_service(photo_repo, dog_repo, tmp_media):
    return PhotoService(photo_repo, dog_repo, tmp_media)


def make_fake_jpeg() -> bytes:
    """Crea un'immagine JPEG minimale in memoria (senza file su disco)."""
    from PIL import Image
    from io import BytesIO
    img = Image.new("RGB", (200, 200), color=(180, 100, 60))
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()
