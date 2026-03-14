from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


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

    def is_active(self) -> bool:
        return self.status == "active"

    def display_sex(self) -> str:
        mapping = {"M": "Maschio", "F": "Femmina", "Unknown": "Non specificato"}
        return mapping.get(self.sex, self.sex)
