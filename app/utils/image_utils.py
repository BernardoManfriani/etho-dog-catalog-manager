import re
import uuid
from io import BytesIO
from pathlib import Path
from typing import Optional

from PIL import Image


class ImageUtils:
    MAX_DIMENSION = 1200
    JPEG_QUALITY = 85
    THUMBNAIL_SIZE = (300, 300)

    @staticmethod
    def process_upload(file_bytes: bytes, original_filename: str) -> tuple[bytes, str]:
        """
        Ridimensiona a max 1200px sul lato lungo, converte in JPEG.
        Ritorna (jpeg_bytes, new_filename).
        """
        img = Image.open(BytesIO(file_bytes))

        # Converti in RGB (necessario per JPEG, es. immagini RGBA/P)
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        # Ridimensiona se necessario
        w, h = img.size
        if w > ImageUtils.MAX_DIMENSION or h > ImageUtils.MAX_DIMENSION:
            img.thumbnail(
                (ImageUtils.MAX_DIMENSION, ImageUtils.MAX_DIMENSION),
                Image.LANCZOS,
            )

        buf = BytesIO()
        img.save(buf, format="JPEG", quality=ImageUtils.JPEG_QUALITY, optimize=True)
        jpeg_bytes = buf.getvalue()

        # Genera nome file univoco
        uid = uuid.uuid4().hex[:8]
        sanitized = ImageUtils._sanitize_filename(Path(original_filename).stem)
        new_filename = f"{uid}_{sanitized}.jpg"

        return jpeg_bytes, new_filename

    @staticmethod
    def make_thumbnail(file_path: str, size: tuple = (300, 300)) -> Optional[bytes]:
        """Ritorna bytes JPEG del thumbnail, None se il file manca."""
        try:
            img = Image.open(file_path)
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
            img.thumbnail(size, Image.LANCZOS)
            buf = BytesIO()
            img.save(buf, format="JPEG", quality=75)
            return buf.getvalue()
        except Exception:
            return None

    @staticmethod
    def load_image_for_display(file_path: str) -> Optional[bytes]:
        """
        Legge il file dal disco. Ritorna None se mancante o corrotto,
        senza mai sollevare eccezione verso l'UI.
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            return path.read_bytes()
        except Exception:
            return None

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """Rimuove caratteri non alfanumerici, lowercase, trunca a 40 char."""
        sanitized = re.sub(r"[^a-zA-Z0-9_-]", "_", name).lower()
        return sanitized[:40]
