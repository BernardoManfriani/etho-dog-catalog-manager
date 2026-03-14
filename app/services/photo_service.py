import os
from pathlib import Path
from typing import Optional
from app.models.photo import DogPhoto
from app.repositories.dog_repository import DogRepository
from app.repositories.photo_repository import PhotoRepository
from app.utils.image_utils import ImageUtils

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


class PhotoService:
    def __init__(self, photo_repo: PhotoRepository, dog_repo: DogRepository, media_dir: str):
        self.photo_repo = photo_repo
        self.dog_repo = dog_repo
        self.media_dir = media_dir

    def upload_photo(
        self,
        dog_id: int,
        file_bytes: bytes,
        filename: str,
        note: str = "",
        set_as_primary: bool = False,
    ) -> DogPhoto:
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file format: '{ext}'. "
                f"Use: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Ridimensiona e converti in JPEG
        processed_bytes, new_filename = ImageUtils.process_upload(file_bytes, filename)

        # Scrivi su disco
        dest_path = Path(self.media_dir) / new_filename
        dest_path.write_bytes(processed_bytes)

        # Percorso relativo per il DB
        relative_path = str(Path("data") / "media" / new_filename)

        # È il primo upload per questo cane?
        is_first = self.photo_repo.count_active_for_dog(dog_id) == 0

        photo = DogPhoto(
            dog_id=dog_id,
            file_path=relative_path,
            is_primary=False,
            note=note,
        )
        photo = self.photo_repo.add(photo)

        # Imposta come primaria se richiesto o se è la prima foto
        if set_as_primary or is_first:
            self.photo_repo.set_primary(dog_id, photo.id)
            photo.is_primary = True
            # Rimuovi il flag needs_photo_update se si imposta una nuova primaria
            dog = self.dog_repo.get_by_id(dog_id)
            if dog and dog.needs_photo_update:
                dog.needs_photo_update = False
                self.dog_repo.update(dog)

        return photo

    def set_primary_photo(self, dog_id: int, photo_id: int) -> None:
        self.photo_repo.set_primary(dog_id, photo_id)

    def delete_photo(self, photo_id: int) -> None:
        """Soft delete: disattiva la foto nel DB e rimuove il file dal disco."""
        photo = self.photo_repo.get_by_id(photo_id)
        if photo is None:
            return
        self.photo_repo.deactivate(photo_id)
        # Prova a rimuovere il file fisico
        full_path = self._resolve_full_path(photo.file_path)
        try:
            if full_path and Path(full_path).exists():
                Path(full_path).unlink()
        except OSError:
            pass  # Non interrompere se il file non è eliminabile

    def get_photos_for_dog(self, dog_id: int) -> list[DogPhoto]:
        return self.photo_repo.get_by_dog(dog_id)

    def get_primary_photo(self, dog_id: int) -> Optional[DogPhoto]:
        return self.photo_repo.get_primary(dog_id)

    def get_primary_photos_map(self, dog_ids: list[int]) -> dict[int, Optional[DogPhoto]]:
        """Ritorna un dizionario dog_id -> foto primaria (o None)."""
        return {dog_id: self.photo_repo.get_primary(dog_id) for dog_id in dog_ids}

    def _resolve_full_path(self, relative_path: str) -> Optional[str]:
        """Risolve un percorso relativo (da project root) a percorso assoluto."""
        import os
        catalog_root = os.environ.get("CATALOG_ROOT")
        if catalog_root:
            return str(Path(catalog_root) / relative_path)
        # Risale dalla posizione di questo file
        root = Path(__file__).parent.parent.parent
        return str(root / relative_path)
