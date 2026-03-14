import sqlite3
from pathlib import Path


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        return conn

    def initialize_schema(self) -> None:
        with self.get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS dogs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    sex TEXT DEFAULT 'Unknown',
                    location TEXT DEFAULT '',
                    notes TEXT DEFAULT '',
                    needs_photo_update BOOLEAN DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    manual_order INTEGER,
                    tag_number INTEGER,
                    color TEXT DEFAULT '',
                    year TEXT DEFAULT '',
                    dead BOOLEAN DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS dog_photos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dog_id INTEGER NOT NULL REFERENCES dogs(id),
                    file_path TEXT NOT NULL,
                    is_primary BOOLEAN DEFAULT 0,
                    note TEXT DEFAULT '',
                    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                );

                CREATE INDEX IF NOT EXISTS idx_dogs_status ON dogs(status);
                CREATE INDEX IF NOT EXISTS idx_dogs_name ON dogs(name);
                CREATE INDEX IF NOT EXISTS idx_dog_photos_dog_id ON dog_photos(dog_id);
                CREATE INDEX IF NOT EXISTS idx_dog_photos_primary ON dog_photos(dog_id, is_primary);
            """)
        # Migra DB esistenti che non hanno ancora le nuove colonne
        self._migrate_columns()

    def _migrate_columns(self) -> None:
        """Aggiunge le colonne mancanti ai DB esistenti (idempotente)."""
        new_cols = [
            ("tag_number", "INTEGER"),
            ("color", "TEXT DEFAULT ''"),
            ("year", "TEXT DEFAULT ''"),
            ("dead", "BOOLEAN DEFAULT 0"),
        ]
        conn = self.get_connection()
        try:
            existing = {row[1] for row in conn.execute("PRAGMA table_info(dogs)")}
            for col_name, col_def in new_cols:
                if col_name not in existing:
                    conn.execute(f"ALTER TABLE dogs ADD COLUMN {col_name} {col_def}")
            conn.commit()
        finally:
            conn.close()
