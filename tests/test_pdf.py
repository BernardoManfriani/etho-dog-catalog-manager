from pathlib import Path
from tests.conftest import make_fake_jpeg
from app.pdf.pdf_generator import PdfGenerator
from app.services.dog_service import DogService
from app.services.photo_service import PhotoService


def test_pdf_generates_file(dog_service: DogService, tmp_path):
    dog = dog_service.create_dog("Daisy", "F", "Farm", "")
    out = str(tmp_path / "test.pdf")
    gen = PdfGenerator(out)
    gen.generate_catalog(
        dogs=[dog],
        photos={dog.id: None},
        media_dir=str(tmp_path / "media"),
    )
    assert Path(out).exists()
    assert Path(out).stat().st_size > 0


def test_pdf_with_real_photo(
    dog_service: DogService,
    photo_service: PhotoService,
    tmp_path,
):
    dog = dog_service.create_dog("Jake", "M", "Shelter", "")
    photo = photo_service.upload_photo(
        dog.id, make_fake_jpeg(), "jake.jpg", set_as_primary=True
    )
    out = str(tmp_path / "with_photo.pdf")
    gen = PdfGenerator(out)
    gen.generate_catalog(
        dogs=[dog],
        photos={dog.id: photo},
        media_dir=str(tmp_path / "media"),
        project_root=str(tmp_path),
    )
    assert Path(out).exists()
    assert Path(out).stat().st_size > 0


def test_pdf_empty_catalog(tmp_path):
    out = str(tmp_path / "empty.pdf")
    gen = PdfGenerator(out)
    gen.generate_catalog(
        dogs=[],
        photos={},
        media_dir=str(tmp_path / "media"),
    )
    assert Path(out).exists()


def test_pdf_multiple_dogs(dog_service: DogService, tmp_path):
    dogs = [dog_service.create_dog(f"Cane {i}", "M", "Luogo", "") for i in range(10)]
    out = str(tmp_path / "multi.pdf")
    gen = PdfGenerator(out)
    gen.generate_catalog(
        dogs=dogs,
        photos={d.id: None for d in dogs},
        media_dir=str(tmp_path / "media"),
    )
    assert Path(out).exists()
    assert Path(out).stat().st_size > 0
