import sqlite3
from datetime import datetime
from typing import Optional
from app.models.photo import DogPhoto
from app.repositories.database import Database


class PhotoRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_by_id(self, photo_id: int) -> Optional[DogPhoto]:
        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM dog_photos WHERE id = ?", [photo_id]
            ).fetchone()
            return self._row_to_photo(row) if row else None

    def get_by_dog(self, dog_id: int, active_only: bool = True) -> list[DogPhoto]:
        with self.db.get_connection() as conn:
            if active_only:
                rows = conn.execute(
                    """SELECT * FROM dog_photos WHERE dog_id=? AND is_active=1
                       ORDER BY is_primary DESC, uploaded_at DESC""",
                    [dog_id],
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM dog_photos WHERE dog_id=? ORDER BY uploaded_at DESC",
                    [dog_id],
                ).fetchall()
            return [self._row_to_photo(r) for r in rows]

    def get_primary(self, dog_id: int) -> Optional[DogPhoto]:
        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM dog_photos WHERE dog_id=? AND is_primary=1 AND is_active=1",
                [dog_id],
            ).fetchone()
            return self._row_to_photo(row) if row else None

    def add(self, photo: DogPhoto) -> DogPhoto:
        now = datetime.now().isoformat()
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO dog_photos (dog_id, file_path, is_primary, note, uploaded_at, is_active)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                [
                    photo.dog_id, photo.file_path,
                    1 if photo.is_primary else 0,
                    photo.note, now,
                    1 if photo.is_active else 0,
                ],
            )
            photo.id = cursor.lastrowid
            photo.uploaded_at = datetime.fromisoformat(now)
            return photo

    def set_primary(self, dog_id: int, photo_id: int) -> None:
        with self.db.get_connection() as conn:
            # Transazione atomica: azzera tutti, poi setta il target
            conn.execute(
                "UPDATE dog_photos SET is_primary=0 WHERE dog_id=?", [dog_id]
            )
            conn.execute(
                "UPDATE dog_photos SET is_primary=1 WHERE id=?", [photo_id]
            )

    def deactivate(self, photo_id: int) -> None:
        with self.db.get_connection() as conn:
            conn.execute(
                "UPDATE dog_photos SET is_active=0, is_primary=0 WHERE id=?",
                [photo_id],
            )

    def get_all_active_paths(self) -> list[str]:
        with self.db.get_connection() as conn:
            rows = conn.execute(
                "SELECT file_path FROM dog_photos WHERE is_active=1"
            ).fetchall()
            return [r[0] for r in rows]

    def count_active_for_dog(self, dog_id: int) -> int:
        with self.db.get_connection() as conn:
            return conn.execute(
                "SELECT COUNT(*) FROM dog_photos WHERE dog_id=? AND is_active=1",
                [dog_id],
            ).fetchone()[0]

    def delete_all_for_dog(self, dog_id: int) -> list[str]:
        """Delete all photo records for a dog; returns file_paths for disk cleanup."""
        with self.db.get_connection() as conn:
            rows = conn.execute(
                "SELECT file_path FROM dog_photos WHERE dog_id=?", [dog_id]
            ).fetchall()
            conn.execute("DELETE FROM dog_photos WHERE dog_id=?", [dog_id])
        return [r[0] for r in rows]

    def _row_to_photo(self, row: sqlite3.Row) -> DogPhoto:
        def _parse_dt(val):
            if val is None:
                return None
            try:
                return datetime.fromisoformat(str(val))
            except ValueError:
                return None

        return DogPhoto(
            id=row["id"],
            dog_id=row["dog_id"],
            file_path=row["file_path"],
            is_primary=bool(row["is_primary"]),
            note=row["note"] or "",
            uploaded_at=_parse_dt(row["uploaded_at"]),
            is_active=bool(row["is_active"]),
        )
