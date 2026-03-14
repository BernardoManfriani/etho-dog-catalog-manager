import zipfile
from datetime import datetime
from pathlib import Path


class BackupUtils:
    @staticmethod
    def create_backup(db_path: str, media_dir: str, output_dir: str) -> str:
        """
        Crea uno zip in output_dir con DB + cartella media.
        Ritorna il percorso del file zip creato.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = f"catalog_backup_{timestamp}.zip"
        zip_path = Path(output_dir) / zip_name

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # Aggiungi il database
            db = Path(db_path)
            if db.exists():
                zf.write(db, arcname="catalog.db")

            # Aggiungi tutte le immagini
            media = Path(media_dir)
            if media.exists():
                for img_file in media.iterdir():
                    if img_file.is_file():
                        zf.write(img_file, arcname=f"media/{img_file.name}")

        return str(zip_path)

    @staticmethod
    def get_backup_size_mb(zip_path: str) -> float:
        path = Path(zip_path)
        if not path.exists():
            return 0.0
        return path.stat().st_size / (1024 * 1024)
