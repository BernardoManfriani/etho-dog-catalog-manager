from dataclasses import dataclass
from datetime import datetime
from typing import Optional


LOCATION_OPTIONS = ["TH", "IF", "DR", "JS", "BB", "WC", "E", "k17", "k18"]
COLOR_OPTIONS = ["Y", "B", "O", "P"]  # tag/collar color codes

# Coat-color sub-catalogs (fur/pelage classification)
COAT_OPTIONS = ["White", "Light tan", "Dark brown", "Brindle", "Black"]


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
    # Extended fields
    tag_number: Optional[int] = None
    color: Optional[str] = None       # tag/collar color: Y, B, O, P
    year: Optional[str] = None
    dead: bool = False
    coat_color: Optional[str] = None  # coat/fur catalog: White, Light tan, Dark brown, Brindle, Black

    def is_active(self) -> bool:
        return self.status == "active"

    def display_sex(self) -> str:
        mapping = {"M": "Male", "F": "Female", "Unknown": "Unknown"}
        return mapping.get(self.sex, self.sex)

    def format_display_name(self) -> str:
        """
        Format: Name_location_sex[_tagnumber&color]_year[_(dead)]
        tag&color included only when both are present.
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
