from app.services.dog_service import DogService


def test_search_by_name(dog_service: DogService):
    dog_service.create_dog("Fluffy", "F", "Home", "")
    dog_service.create_dog("Shadow", "M", "Shelter", "")
    results = dog_service.search_dogs(query="fluf")
    assert len(results) == 1
    assert results[0].name == "Fluffy"


def test_search_case_insensitive(dog_service: DogService):
    dog_service.create_dog("UPPERCASE", "M", "", "")
    results = dog_service.search_dogs(query="uppercase")
    assert len(results) == 1


def test_search_by_sex(dog_service: DogService):
    dog_service.create_dog("Alpha", "M", "", "")
    dog_service.create_dog("Beta", "F", "", "")
    results = dog_service.search_dogs(sex="F")
    assert all(d.sex == "F" for d in results)
    assert len(results) == 1


def test_search_by_location(dog_service: DogService):
    dog_service.create_dog("North1", "M", "North", "")
    dog_service.create_dog("South1", "M", "South", "")
    results = dog_service.search_dogs(location="North")
    assert len(results) == 1
    assert results[0].location == "North"


def test_search_combined_filters(dog_service: DogService):
    dog_service.create_dog("Alpha", "M", "North", "")
    dog_service.create_dog("Beta", "F", "North", "")
    dog_service.create_dog("Gamma", "M", "South", "")
    results = dog_service.search_dogs(sex="M", location="North")
    assert len(results) == 1
    assert results[0].name == "Alpha"


def test_search_needs_photo_update(dog_service: DogService):
    dog_service.create_dog("WithFlag", "M", "", "", needs_photo_update=True)
    dog_service.create_dog("NoFlag", "M", "", "", needs_photo_update=False)
    results = dog_service.search_dogs(needs_photo_update=True)
    assert len(results) == 1
    assert results[0].name == "WithFlag"


def test_search_no_results(dog_service: DogService):
    dog_service.create_dog("Rex", "M", "", "")
    results = dog_service.search_dogs(query="zzznomatch")
    assert len(results) == 0


def test_search_archived_excluded_by_default(dog_service: DogService):
    dog = dog_service.create_dog("Archived", "M", "", "")
    dog_service.archive_dog(dog.id)
    results = dog_service.search_dogs(query="Archived")
    assert len(results) == 0


def test_search_in_notes(dog_service: DogService):
    dog_service.create_dog("Rex", "M", "", "pastore tedesco vaccinato")
    results = dog_service.search_dogs(query="vaccinato")
    assert len(results) == 1
