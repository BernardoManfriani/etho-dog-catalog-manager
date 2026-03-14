from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class DogPhoto:
    dog_id: int
    file_path: str              # percorso relativo dal project root
    id: Optional[int] = None
    is_primary: bool = False
    note: str = ""
    uploaded_at: Optional[datetime] = None
    is_active: bool = True
