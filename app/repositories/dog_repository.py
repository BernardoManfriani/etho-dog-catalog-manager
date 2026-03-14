import sqlite3
from datetime import datetime
from typing import Optional
from app.models.dog import Dog
from app.repositories.database import Database


class DogRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_by_id(self, dog_id: int) -> Optional[Dog]:
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT * FROM dogs WHERE id = ?", [dog_id]).fetchone()
            return self._row_to_dog(row) if row else None

    def get_all(self, status: str = "active") -> list[Dog]:
        with self.db.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM dogs WHERE status = ? ORDER BY name", [status]
            ).fetchall()
            return [self._row_to_dog(r) for r in rows]

    def search(
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
        clauses = ["status = ?"]
        params: list = [status]

        if query:
            clauses.append("(name LIKE ? OR location LIKE ? OR notes LIKE ?)")
            params += [f"%{query}%", f"%{query}%", f"%{query}%"]

        if sex and sex not in ("All", "Tutti"):
            clauses.append("sex = ?")
            params.append(sex)

        if location and location not in ("All", "Tutti"):
            clauses.append("location = ?")
            params.append(location)

        if needs_photo_update is not None:
            clauses.append("needs_photo_update = ?")
            params.append(1 if needs_photo_update else 0)

        if tag_number is not None:
            clauses.append("tag_number = ?")
            params.append(tag_number)

        if coat_color:
            clauses.append("coat_color = ?")
            params.append(coat_color)

        valid_orders = {"name", "created_at", "updated_at", "manual_order"}
        order_col = order_by if order_by in valid_orders else "name"

        sql = f"SELECT * FROM dogs WHERE {' AND '.join(clauses)} ORDER BY {order_col}"

        with self.db.get_connection() as conn:
            rows = conn.execute(sql, params).fetchall()
            return [self._row_to_dog(r) for r in rows]

    def create(self, dog: Dog) -> Dog:
        now = datetime.now().isoformat()
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO dogs (name, sex, location, notes, needs_photo_update,
                   status, created_at, updated_at, manual_order,
                   tag_number, color, year, dead, coat_color)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                [
                    dog.name, dog.sex, dog.location, dog.notes,
                    1 if dog.needs_photo_update else 0,
                    dog.status, now, now, dog.manual_order,
                    dog.tag_number,
                    dog.color or "",
                    dog.year or "",
                    1 if dog.dead else 0,
                    dog.coat_color or "",
                ],
            )
            dog.id = cursor.lastrowid
            dog.created_at = datetime.fromisoformat(now)
            dog.updated_at = datetime.fromisoformat(now)
            return dog

    def update(self, dog: Dog) -> Dog:
        now = datetime.now().isoformat()
        with self.db.get_connection() as conn:
            conn.execute(
                """UPDATE dogs SET name=?, sex=?, location=?, notes=?,
                   needs_photo_update=?, status=?, updated_at=?, manual_order=?,
                   tag_number=?, color=?, year=?, dead=?, coat_color=?
                   WHERE id=?""",
                [
                    dog.name, dog.sex, dog.location, dog.notes,
                    1 if dog.needs_photo_update else 0,
                    dog.status, now, dog.manual_order,
                    dog.tag_number,
                    dog.color or "",
                    dog.year or "",
                    1 if dog.dead else 0,
                    dog.coat_color or "",
                    dog.id,
                ],
            )
            dog.updated_at = datetime.fromisoformat(now)
            return dog

    def archive(self, dog_id: int) -> None:
        now = datetime.now().isoformat()
        with self.db.get_connection() as conn:
            conn.execute(
                "UPDATE dogs SET status='archived', updated_at=? WHERE id=?",
                [now, dog_id],
            )

    def restore(self, dog_id: int) -> None:
        now = datetime.now().isoformat()
        with self.db.get_connection() as conn:
            conn.execute(
                "UPDATE dogs SET status='active', updated_at=? WHERE id=?",
                [now, dog_id],
            )

    def delete(self, dog_id: int) -> None:
        with self.db.get_connection() as conn:
            conn.execute("DELETE FROM dogs WHERE id=?", [dog_id])

    def get_stats(self) -> dict:
        with self.db.get_connection() as conn:
            total_active = conn.execute(
                "SELECT COUNT(*) FROM dogs WHERE status='active'"
            ).fetchone()[0]

            with_photo = conn.execute(
                """SELECT COUNT(DISTINCT d.id) FROM dogs d
                   JOIN dog_photos p ON p.dog_id = d.id
                   WHERE d.status='active' AND p.is_primary=1 AND p.is_active=1"""
            ).fetchone()[0]

            needs_update = conn.execute(
                "SELECT COUNT(*) FROM dogs WHERE status='active' AND needs_photo_update=1"
            ).fetchone()[0]

            recent = conn.execute(
                """SELECT COUNT(*) FROM dogs
                   WHERE status='active'
                   AND created_at >= datetime('now', '-7 days')"""
            ).fetchone()[0]

            total_archived = conn.execute(
                "SELECT COUNT(*) FROM dogs WHERE status='archived'"
            ).fetchone()[0]

            return {
                "total_active": total_active,
                "with_primary_photo": with_photo,
                "needs_photo_update": needs_update,
                "added_last_7_days": recent,
                "total_archived": total_archived,
            }

    def get_distinct_locations(self) -> list[str]:
        with self.db.get_connection() as conn:
            rows = conn.execute(
                """SELECT DISTINCT location FROM dogs
                   WHERE status='active' AND location != ''
                   ORDER BY location"""
            ).fetchall()
            return [r[0] for r in rows]

    def update_order(self, dog_id: int, order: int) -> None:
        with self.db.get_connection() as conn:
            conn.execute(
                "UPDATE dogs SET manual_order=? WHERE id=?", [order, dog_id]
            )

    def _row_to_dog(self, row: sqlite3.Row) -> Dog:
        def _parse_dt(val):
            if val is None:
                return None
            try:
                return datetime.fromisoformat(str(val))
            except ValueError:
                return None

        keys = row.keys()

        def _get(key, default=None):
            return row[key] if key in keys else default

        return Dog(
            id=row["id"],
            name=row["name"],
            sex=row["sex"] or "Unknown",
            location=row["location"] or "",
            notes=row["notes"] or "",
            needs_photo_update=bool(row["needs_photo_update"]),
            status=row["status"] or "active",
            created_at=_parse_dt(row["created_at"]),
            updated_at=_parse_dt(row["updated_at"]),
            manual_order=row["manual_order"],
            tag_number=_get("tag_number"),
            color=_get("color") or None,
            year=_get("year") or None,
            dead=bool(_get("dead", 0)),
            coat_color=_get("coat_color") or None,
        )
