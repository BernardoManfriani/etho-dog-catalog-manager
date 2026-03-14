import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.pdf.pdf_generator import PdfGenerator
from app.services.dog_service import DogService
from app.services.photo_service import PhotoService
from app.utils.backup_utils import BackupUtils
from app.utils.csv_utils import CsvUtils


class ExportService:
    def __init__(
        self,
        dog_service: DogService,
        photo_service: PhotoService,
        media_dir: str,
        export_dir: str,
        db_path: str,
    ):
        self.dog_service = dog_service
        self.photo_service = photo_service
        self.media_dir = media_dir
        self.export_dir = export_dir
        self.db_path = db_path
        Path(export_dir).mkdir(parents=True, exist_ok=True)

    def export_pdf(
        self,
        query: str = "",
        sex: Optional[str] = None,
        location: Optional[str] = None,
        needs_photo_update: Optional[bool] = None,
        title: str = "Catalogo Cani",
    ) -> str:
        """Genera il PDF e ritorna il percorso del file."""
        dogs = self.dog_service.get_catalog_page(
            query=query,
            sex=sex,
            location=location,
            needs_photo_update=needs_photo_update,
            order_by="name",
        )

        dog_ids = [d.id for d in dogs]
        photos = self.photo_service.get_primary_photos_map(dog_ids)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_path = str(Path(self.export_dir) / f"catalog_{timestamp}.pdf")

        project_root = os.environ.get("CATALOG_ROOT") or str(
            Path(__file__).parent.parent.parent
        )

        gen = PdfGenerator(pdf_path)
        gen.generate_catalog(dogs, photos, self.media_dir, project_root, title)
        return pdf_path

    def export_csv(
        self,
        query: str = "",
        sex: Optional[str] = None,
        location: Optional[str] = None,
    ) -> str:
        """Ritorna una stringa CSV con i cani filtrati."""
        dogs = self.dog_service.get_catalog_page(
            query=query, sex=sex, location=location
        )
        return CsvUtils.export_dogs_to_csv(dogs)

    def import_csv(self, csv_content: str) -> dict:
        """
        Importa cani da CSV.
        Ritorna {"created": int, "skipped": int, "errors": list[str]}.
        """
        result = CsvUtils.import_dogs_from_csv(csv_content)
        created = 0
        import_errors = list(result["errors"])

        for i, row_data in enumerate(result["rows"]):
            try:
                self.dog_service.create_dog(**row_data)
                created += 1
            except ValueError as e:
                import_errors.append(f"Riga {i + 2}: {e}")

        return {
            "created": created,
            "skipped": len(result["errors"]),
            "errors": import_errors,
        }

    def create_backup(self) -> str:
        """Crea un backup zip del DB + media. Ritorna il percorso del file."""
        return BackupUtils.create_backup(self.db_path, self.media_dir, self.export_dir)
