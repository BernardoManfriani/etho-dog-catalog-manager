import pytest
from pathlib import Path
from tests.conftest import make_fake_jpeg
from app.services.dog_service import DogService
from app.services.photo_service import PhotoService


def test_upload_photo(dog_service: DogService, photo_service: PhotoService, tmp_media: str):
    dog = dog_service.create_dog("Rover", "M", "", "")
    photo = photo_service.upload_photo(
        dog.id, make_fake_jpeg(), "test.jpg", set_as_primary=True
    )
    assert photo.id is not None
    assert photo.is_primary
    # Il file deve esistere su disco
    full_path = Path(tmp_media) / Path(photo.file_path).name
    assert full_path.exists()


def test_first_photo_auto_primary(dog_service: DogService, photo_service: PhotoService):
    """Il primo upload diventa automaticamente foto principale."""
    dog = dog_service.create_dog("Coco", "F", "", "")
    photo = photo_service.upload_photo(dog.id, make_fake_jpeg(), "coco.jpg")
    assert photo.is_primary


def test_set_primary(dog_service: DogService, photo_service: PhotoService):
    dog = dog_service.create_dog("Biscuit", "F", "", "")
    p1 = photo_service.upload_photo(dog.id, make_fake_jpeg(), "a.jpg")
    p2 = photo_service.upload_photo(dog.id, make_fake_jpeg(), "b.jpg")
    photo_service.set_primary_photo(dog.id, p2.id)
    primary = photo_service.get_primary_photo(dog.id)
    assert primary.id == p2.id


def test_only_one_primary(dog_service: DogService, photo_service: PhotoService):
    """Dopo set_primary, una sola foto deve essere primaria."""
    dog = dog_service.create_dog("Daisy", "F", "", "")
    p1 = photo_service.upload_photo(dog.id, make_fake_jpeg(), "d1.jpg")
    p2 = photo_service.upload_photo(dog.id, make_fake_jpeg(), "d2.jpg")
    p3 = photo_service.upload_photo(dog.id, make_fake_jpeg(), "d3.jpg")
    photo_service.set_primary_photo(dog.id, p3.id)
    photos = photo_service.get_photos_for_dog(dog.id)
    primaries = [p for p in photos if p.is_primary]
    assert len(primaries) == 1
    assert primaries[0].id == p3.id


def test_delete_photo_soft(dog_service: DogService, photo_service: PhotoService):
    dog = dog_service.create_dog("Ghost", "M", "", "")
    photo = photo_service.upload_photo(dog.id, make_fake_jpeg(), "ghost.jpg")
    photo_service.delete_photo(photo.id)
    photos = photo_service.get_photos_for_dog(dog.id)
    assert not any(p.id == photo.id for p in photos)


def test_upload_invalid_extension(dog_service: DogService, photo_service: PhotoService):
    dog = dog_service.create_dog("Test", "M", "", "")
    with pytest.raises(ValueError, match="[Ff]ormat"):
        photo_service.upload_photo(dog.id, b"fake", "image.bmp")


def test_upload_auto_removes_needs_update_flag(
    dog_service: DogService, photo_service: PhotoService
):
    dog = dog_service.create_dog("Flag", "M", "", "", needs_photo_update=True)
    assert dog.needs_photo_update
    photo_service.upload_photo(dog.id, make_fake_jpeg(), "flag.jpg", set_as_primary=True)
    refreshed = dog_service.search_dogs(query="Flag")
    assert not refreshed[0].needs_photo_update
