import pytest
from app.services.dog_service import DogService


def test_create_dog(dog_service: DogService):
    dog = dog_service.create_dog("Buddy", "M", "Shelter A", "Good boy")
    assert dog.id is not None
    assert dog.name == "Buddy"
    assert dog.sex == "M"
    assert dog.location == "Shelter A"
    assert dog.status == "active"


def test_create_dog_empty_name_raises(dog_service: DogService):
    with pytest.raises(ValueError, match="[Nn]ame"):
        dog_service.create_dog("", "M", "", "")


def test_create_dog_whitespace_name_raises(dog_service: DogService):
    with pytest.raises(ValueError):
        dog_service.create_dog("   ", "M", "", "")


def test_create_dog_invalid_sex_raises(dog_service: DogService):
    with pytest.raises(ValueError, match="[Ss]ex"):
        dog_service.create_dog("Rex", "X", "", "")


def test_create_two_dogs_same_name(dog_service: DogService):
    """Due cani con lo stesso nome sono ammessi (ognuno ha un ID univoco)."""
    d1 = dog_service.create_dog("Luna", "F", "Rifugio A", "")
    d2 = dog_service.create_dog("Luna", "F", "Rifugio B", "")
    assert d1.id != d2.id


def test_update_dog(dog_service: DogService):
    dog = dog_service.create_dog("Rex", "M", "Shelter A", "")
    updated = dog_service.update_dog(dog.id, name="Rex Updated", location="Shelter B")
    assert updated.name == "Rex Updated"
    assert updated.location == "Shelter B"


def test_update_dog_not_found_raises(dog_service: DogService):
    with pytest.raises(ValueError, match="not found"):
        dog_service.update_dog(9999, name="Ghost")


def test_archive_dog(dog_service: DogService):
    dog = dog_service.create_dog("Max", "M", "", "")
    dog_service.archive_dog(dog.id)
    active = dog_service.search_dogs(status="active")
    assert not any(d.id == dog.id for d in active)
    archived = dog_service.search_dogs(status="archived")
    assert any(d.id == dog.id for d in archived)


def test_restore_dog(dog_service: DogService):
    dog = dog_service.create_dog("Max", "M", "", "")
    dog_service.archive_dog(dog.id)
    dog_service.restore_dog(dog.id)
    active = dog_service.search_dogs(status="active")
    assert any(d.id == dog.id for d in active)


def test_get_dashboard_stats(dog_service: DogService):
    dog_service.create_dog("A", "M", "", "")
    dog_service.create_dog("B", "F", "", "", needs_photo_update=True)
    stats = dog_service.get_dashboard_stats()
    assert stats["total_active"] == 2
    assert stats["needs_photo_update"] == 1
    assert stats["added_last_7_days"] >= 2
