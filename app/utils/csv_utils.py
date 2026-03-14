import csv
import io
from typing import Any
from app.models.dog import Dog


VALID_SEX_VALUES = {"M", "F", "Unknown", ""}
EXPORT_COLUMNS = [
    "id", "name", "sex", "location", "notes",
    "needs_photo_update", "status", "created_at", "updated_at",
]


class CsvUtils:
    @staticmethod
    def export_dogs_to_csv(dogs: list[Dog]) -> str:
        """Ritorna una stringa CSV con tutti i cani."""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=EXPORT_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for dog in dogs:
            writer.writerow({
                "id": dog.id,
                "name": dog.name,
                "sex": dog.sex,
                "location": dog.location,
                "notes": dog.notes,
                "needs_photo_update": 1 if dog.needs_photo_update else 0,
                "status": dog.status,
                "created_at": dog.created_at.isoformat() if dog.created_at else "",
                "updated_at": dog.updated_at.isoformat() if dog.updated_at else "",
            })
        return output.getvalue()

    @staticmethod
    def import_dogs_from_csv(csv_content: str) -> dict[str, Any]:
        """
        Parsa il CSV e ritorna:
        {
            "rows": list[dict],  # dati pronti per DogService.create_dog()
            "errors": list[str],  # messaggi di errore con numero di riga
        }
        """
        reader = csv.DictReader(io.StringIO(csv_content))

        if "name" not in (reader.fieldnames or []):
            return {
                "rows": [],
                "errors": ["Required column 'name' not found in CSV."],
            }

        rows = []
        errors = []

        for i, row in enumerate(reader, start=2):  # start=2 because row 1 is header
            name = row.get("name", "").strip()
            if not name:
                errors.append(f"Row {i}: empty 'name' field, row skipped.")
                continue

            sex = row.get("sex", "Unknown").strip()
            if sex not in VALID_SEX_VALUES:
                errors.append(
                    f"Row {i}: invalid sex '{sex}', set to 'Unknown'."
                )
                sex = "Unknown"
            if not sex:
                sex = "Unknown"

            rows.append({
                "name": name,
                "sex": sex,
                "location": row.get("location", "").strip(),
                "notes": row.get("notes", "").strip(),
            })

        return {"rows": rows, "errors": errors}
