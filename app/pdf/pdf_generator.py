from datetime import datetime
from pathlib import Path
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as rl_canvas

from app.models.dog import Dog
from app.models.photo import DogPhoto


class PdfGenerator:
    COLS = 3
    MARGIN = 15 * mm
    GAP = 5 * mm
    PHOTO_HEIGHT = 45 * mm
    TEXT_LINE_HEIGHT = 5 * mm
    CARD_TEXT_LINES = 3
    CARD_PADDING = 4 * mm
    BORDER_COLOR = colors.HexColor("#cccccc")
    PLACEHOLDER_COLOR = colors.HexColor("#eeeeee")
    TEXT_COLOR = colors.HexColor("#222222")
    META_COLOR = colors.HexColor("#666666")

    def __init__(self, output_path: str):
        self.output_path = output_path

    def generate_catalog(
        self,
        dogs: list[Dog],
        photos: dict[int, Optional[DogPhoto]],
        media_dir: str,
        project_root: Optional[str] = None,
        title: str = "Dog Catalog",
    ) -> str:
        """Genera il PDF e ritorna il percorso del file."""
        Path(self.output_path).parent.mkdir(parents=True, exist_ok=True)

        page_w, page_h = A4
        card_w, card_h = self._get_card_dimensions(page_w, page_h)

        c = rl_canvas.Canvas(self.output_path, pagesize=A4)
        self._draw_header(c, page_w, page_h, title)

        # Prima pagina inizia sotto l'header
        header_h = 20 * mm
        x_start = self.MARGIN
        y_start = page_h - self.MARGIN - header_h - card_h

        col = 0
        row = 0
        rows_per_page = int((page_h - 2 * self.MARGIN - header_h) / (card_h + self.GAP))

        for i, dog in enumerate(dogs):
            x = x_start + col * (card_w + self.GAP)
            y = y_start - row * (card_h + self.GAP)

            photo = photos.get(dog.id)
            self._draw_card(c, dog, photo, x, y, card_w, card_h, project_root)

            col += 1
            if col >= self.COLS:
                col = 0
                row += 1
                if row >= rows_per_page:
                    c.showPage()
                    self._draw_header(c, page_w, page_h, title)
                    row = 0
                    y_start = page_h - self.MARGIN - header_h - card_h

        c.save()
        return self.output_path

    def _draw_header(self, c: rl_canvas.Canvas, page_w: float, page_h: float, title: str) -> None:
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(self.TEXT_COLOR)
        c.drawString(self.MARGIN, page_h - self.MARGIN - 8 * mm, title)

        date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        c.setFont("Helvetica", 8)
        c.setFillColor(self.META_COLOR)
        c.drawRightString(page_w - self.MARGIN, page_h - self.MARGIN - 8 * mm, date_str)

        # Linea separatrice
        c.setStrokeColor(self.BORDER_COLOR)
        c.setLineWidth(0.5)
        c.line(self.MARGIN, page_h - self.MARGIN - 12 * mm,
               page_w - self.MARGIN, page_h - self.MARGIN - 12 * mm)

    def _draw_card(
        self,
        c: rl_canvas.Canvas,
        dog: Dog,
        photo: Optional[DogPhoto],
        x: float,
        y: float,
        card_w: float,
        card_h: float,
        project_root: Optional[str],
    ) -> None:
        # Bordo card
        c.setStrokeColor(self.BORDER_COLOR)
        c.setLineWidth(0.5)
        c.setFillColor(colors.white)
        c.roundRect(x, y, card_w, card_h, 3 * mm, fill=1, stroke=1)

        # Area foto
        photo_x = x + self.CARD_PADDING
        photo_y = y + card_h - self.CARD_PADDING - self.PHOTO_HEIGHT
        photo_w = card_w - 2 * self.CARD_PADDING

        if photo and photo.file_path:
            img_path = self._resolve_photo_path(photo.file_path, project_root)
            if img_path and Path(img_path).exists():
                try:
                    img_reader = ImageReader(img_path)
                    iw, ih = img_reader.getSize()
                    ratio = min(photo_w / iw, self.PHOTO_HEIGHT / ih)
                    draw_w = iw * ratio
                    draw_h = ih * ratio
                    # Centra orizzontalmente
                    offset_x = (photo_w - draw_w) / 2
                    c.drawImage(
                        img_reader,
                        photo_x + offset_x,
                        photo_y + (self.PHOTO_HEIGHT - draw_h),
                        draw_w,
                        draw_h,
                        preserveAspectRatio=True,
                        mask="auto",
                    )
                    img_path = None  # flag: disegno riuscito
                except Exception:
                    img_path = "placeholder"
            else:
                img_path = "placeholder"
        else:
            img_path = "placeholder"

        if img_path == "placeholder":
            # Placeholder grigio
            c.setFillColor(self.PLACEHOLDER_COLOR)
            c.rect(photo_x, photo_y, photo_w, self.PHOTO_HEIGHT, fill=1, stroke=0)
            c.setFillColor(self.META_COLOR)
            c.setFont("Helvetica", 7)
            c.drawCentredString(
                photo_x + photo_w / 2,
                photo_y + self.PHOTO_HEIGHT / 2 - 3 * mm,
                "No photo available",
            )

        # Testo sotto la foto
        text_y = photo_y - self.TEXT_LINE_HEIGHT * 0.5

        # Nome (bold)
        c.setFillColor(self.TEXT_COLOR)
        c.setFont("Helvetica-Bold", 9)
        name_display = dog.format_display_name()
        if len(name_display) > 40:
            name_display = name_display[:40] + "…"
        c.drawString(photo_x, text_y, name_display)
        text_y -= self.TEXT_LINE_HEIGHT

        # Sesso e luogo
        c.setFillColor(self.META_COLOR)
        c.setFont("Helvetica", 7)
        meta_parts = []
        if dog.sex and dog.sex != "Unknown":
            meta_parts.append(dog.display_sex())
        if dog.location:
            meta_parts.append(dog.location[:20])
        meta_str = " · ".join(meta_parts) if meta_parts else "—"
        c.drawString(photo_x, text_y, meta_str[:38])
        text_y -= self.TEXT_LINE_HEIGHT

        # Note brevi (opzionale)
        if dog.notes:
            c.setFont("Helvetica-Oblique", 6)
            c.setFillColor(self.META_COLOR)
            notes_display = dog.notes[:45] + "…" if len(dog.notes) > 45 else dog.notes
            c.drawString(photo_x, text_y, notes_display)

    def _get_card_dimensions(self, page_w: float, page_h: float) -> tuple[float, float]:
        usable_w = page_w - 2 * self.MARGIN - (self.COLS - 1) * self.GAP
        card_w = usable_w / self.COLS
        card_h = (
            self.PHOTO_HEIGHT
            + self.CARD_TEXT_LINES * self.TEXT_LINE_HEIGHT
            + 2 * self.CARD_PADDING
            + 2 * mm
        )
        return card_w, card_h

    def _resolve_photo_path(
        self, relative_path: str, project_root: Optional[str]
    ) -> Optional[str]:
        import os
        if project_root:
            return str(Path(project_root) / relative_path)
        root_env = os.environ.get("CATALOG_ROOT")
        if root_env:
            return str(Path(root_env) / relative_path)
        # Risale da questo file
        root = Path(__file__).parent.parent.parent
        return str(root / relative_path)
