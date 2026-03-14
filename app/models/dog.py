from dataclasses import dataclass
from datetime import datetime
from typing import Optional


LOCATION_OPTIONS = ["TH", "IF", "DR", "JS", "BB", "WC", "E", "k17", "k18"]
COLOR_OPTIONS = ["Y", "B", "O", "P"]


@dataclass
class Dog:
    name: str
    id: Optional[int] = None
    sex: str = "Unknown"          # 'M', 'F', 'Unknown'
    location: str = ""
    notes: str = ""
    needs_photo_update: bool = False
    status: str = "active"        # 'active', 'archived'
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    manual_order: Optional[int] = None
    # Campi estesi
    tag_number: Optional[int] = None
    color: Optional[str] = None
    year: Optional[str] = None
    dead: bool = False

    def is_active(self) -> bool:
        return self.status == "active"

    def display_sex(self) -> str:
        mapping = {"M": "Maschio", "F": "Femmina", "Unknown": "Non specificato"}
        return mapping.get(self.sex, self.sex)

    def format_display_name(self) -> str:
        """
        Formato: Nome_location_sex[_tagnumber&color]_year[_(dead)]
        tag&color vengono inclusi solo se entrambi presenti.
        year viene incluso se presente.
        _(dead) viene aggiunto se dead=True.
        """
        parts = [self.name]
        if self.location:
            parts.append(self.location)
        if self.sex and self.sex not in ("Unknown", ""):
            parts.append(self.sex)
        if self.tag_number is not None and self.color:
            parts.append(f"{self.tag_number}&{self.color}")
        if self.year:
            parts.append(str(self.year))

        result = "_".join(parts)
        if self.dead:
            result += "_(dead)"
        return result
