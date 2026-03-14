from typing import Optional
from app.models.dog import Dog
from app.models.photo import DogPhoto
from app.repositories.dog_repository import DogRepository
from app.repositories.photo_repository import PhotoRepository


VALID_SEX_VALUES = {"M", "F", "Unknown"}


class DogService:
    def __init__(self, dog_repo: DogRepository, photo_repo: PhotoRepository):
        self.dog_repo = dog_repo
        self.photo_repo = photo_repo

    def create_dog(
        self,
        name: str,
        sex: str = "Unknown",
        location: str = "",
        notes: str = "",
        needs_photo_update: bool = False,
        tag_number: Optional[int] = None,
        color: Optional[str] = None,
        year: Optional[str] = None,
        dead: bool = False,
        coat_color: Optional[str] = None,
    ) -> Dog:
        name = name.strip()
        if not name:
            raise ValueError("Dog name is required.")
        if sex not in VALID_SEX_VALUES:
            raise ValueError(f"Invalid sex: '{sex}'. Valid values: M, F, Unknown.")
        if tag_number is not None and not (1 <= tag_number <= 999):
            raise ValueError("Tag number must be between 1 and 999.")

        dog = Dog(
            name=name,
            sex=sex,
            location=location.strip(),
            notes=notes.strip(),
            needs_photo_update=needs_photo_update,
            tag_number=tag_number,
            color=color or None,
            year=year or None,
            dead=dead,
            coat_color=coat_color or None,
        )
        return self.dog_repo.create(dog)

    def update_dog(self, dog_id: int, **fields) -> Dog:
        dog = self.dog_repo.get_by_id(dog_id)
        if dog is None:
            raise ValueError(f"Dog with ID {dog_id} not found.")

        if "name" in fields:
            name = fields["name"].strip()
            if not name:
                raise ValueError("Dog name is required.")
            dog.name = name

        if "sex" in fields:
            sex = fields["sex"]
            if sex not in VALID_SEX_VALUES:
                raise ValueError(f"Invalid sex: '{sex}'.")
            dog.sex = sex

        if "location" in fields:
            dog.location = fields["location"].strip()
        if "notes" in fields:
            dog.notes = fields["notes"].strip()
        if "needs_photo_update" in fields:
            dog.needs_photo_update = bool(fields["needs_photo_update"])
        if "manual_order" in fields:
            dog.manual_order = fields["manual_order"]
        if "tag_number" in fields:
            tn = fields["tag_number"]
            if tn is not None and not (1 <= int(tn) <= 999):
                raise ValueError("Tag number must be between 1 and 999.")
            dog.tag_number = int(tn) if tn is not None else None
        if "color" in fields:
            dog.color = fields["color"] or None
        if "year" in fields:
            dog.year = fields["year"] or None
        if "dead" in fields:
            dog.dead = bool(fields["dead"])
        if "coat_color" in fields:
            dog.coat_color = fields["coat_color"] or None

        return self.dog_repo.update(dog)

    def archive_dog(self, dog_id: int) -> None:
        self.dog_repo.archive(dog_id)

    def restore_dog(self, dog_id: int) -> None:
        self.dog_repo.restore(dog_id)

    def get_dog_with_photos(self, dog_id: int) -> tuple[Optional[Dog], list[DogPhoto]]:
        dog = self.dog_repo.get_by_id(dog_id)
        if dog is None:
            return None, []
        photos = self.photo_repo.get_by_dog(dog_id)
        return dog, photos

    def search_dogs(
        self,
        query: str = "",
        sex: Optional[str] = None,
        location: Optional[str] = None,
        needs_photo_update: Optional[bool] = None,
        status: str = "active",
        order_by: str = "name",
        tag_number: Optional[int] = None,
        coat_color: Optional[str] = None,
    ) -> list[Dog]:
        return self.dog_repo.search(
            query=query,
            sex=sex,
            location=location,
            needs_photo_update=needs_photo_update,
            status=status,
            order_by=order_by,
            tag_number=tag_number,
            coat_color=coat_color,
        )

    def get_catalog_page(
        self,
        query: str = "",
        sex: Optional[str] = None,
        location: Optional[str] = None,
        needs_photo_update: Optional[bool] = None,
        order_by: str = "name",
        tag_number: Optional[int] = None,
        coat_color: Optional[str] = None,
    ) -> list[Dog]:
        return self.dog_repo.search(
            query=query,
            sex=sex,
            location=location,
            needs_photo_update=needs_photo_update,
            status="active",
            order_by=order_by,
            tag_number=tag_number,
            coat_color=coat_color,
        )

    def get_dashboard_stats(self) -> dict:
        return self.dog_repo.get_stats()

    def mark_needs_photo_update(self, dog_id: int, flag: bool) -> None:
        self.update_dog(dog_id, needs_photo_update=flag)

    def delete_dog(self, dog_id: int) -> None:
        """Hard delete: removes dog record, photo records, and image files from disk."""
        import os
        from pathlib import Path
        paths = self.photo_repo.delete_all_for_dog(dog_id)
        root = os.environ.get("CATALOG_ROOT", "")
        for rel_path in paths:
            try:
                full = Path(root) / rel_path if root else Path(rel_path)
                if full.exists():
                    full.unlink()
            except OSError:
                pass
        self.dog_repo.delete(dog_id)

    def get_distinct_locations(self) -> list[str]:
        return self.dog_repo.get_distinct_locations()
