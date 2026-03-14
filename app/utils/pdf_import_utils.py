"""
PDF import pipeline.

Parses cheat-sheet PDFs with the format:
  Title line: e.g. "BLACK AND TAN DOGS"
  Dog entries (in the page header text block): "Name ♂ Location"  or  "Name ♀ Location"

Returns a list of dicts:
  {"name": str, "sex": str, "location": str, "coat_hint": str}
"""
import re
from typing import Optional

# Full location names → LOCATION_OPTIONS codes
LOCATION_MAP: dict[str, str] = {
    "banana beach": "BB",
    "imourane field": "IF",
    "water cleaning": "WC",
    "tamraght hill": "TH",
    "devil's rock": "DR",
    "devils rock": "DR",
    "devil rock": "DR",
    "k17": "k17",
    "k18": "k18",
    "everywhere": "E",
    "jet ski": "JS",
    "jetski": "JS",
    "river bed": "JS",   # closest available; user can correct
    "riverbed": "JS",
    "aourir": "BB",      # closest geographic match
    "tamawanza": "TH",
    "ranch pet": "",
    "tamraght sarl": "TH",
    "tamraght": "TH",
}

# Title keywords → coat color hint
COAT_TITLE_MAP: dict[str, str] = {
    "black and tan": "Black",
    "black": "Black",
    "white": "White",
    "light tan": "Light tan",
    "tan": "Light tan",
    "dark brown": "Dark brown",
    "brown": "Dark brown",
    "brindle": "Brindle",
}


def _map_location(raw: str) -> str:
    """Map a full location name to a location code, or return the original."""
    key = raw.strip().lower()
    return LOCATION_MAP.get(key, raw.strip())


def _detect_coat_from_title(title: str) -> str:
    """Try to guess a coat_color from the PDF page title."""
    t = title.lower()
    for kw, coat in COAT_TITLE_MAP.items():
        if kw in t:
            return coat
    return ""


def parse_pdf(file_bytes: bytes) -> list[dict]:
    """
    Parse a cheat-sheet PDF and return a list of dog dicts.
    Each dict: {name, sex, location, coat_hint}
    """
    try:
        import pdfplumber
        import io
    except ImportError:
        raise ImportError("pdfplumber is required for PDF import. Run: pip install pdfplumber")

    results: list[dict] = []
    seen: set[str] = set()  # avoid duplicates across pages

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            if not lines:
                continue

            # First non-empty non-numeric line is the title
            title = ""
            for ln in lines:
                if not ln.isdigit():
                    title = ln
                    break
            coat_hint = _detect_coat_from_title(title)

            # Parse all "Name ♂/♀/? Location" entries from the full text
            # Strategy: split on sex symbols, rebuild triplets
            # Pattern: one or more capitalized words, sex symbol, location words
            entries = _extract_entries(text)
            for name, sex, loc_raw in entries:
                key = (name.lower(), sex)
                if key in seen:
                    continue
                seen.add(key)
                results.append({
                    "name": name,
                    "sex": sex,
                    "location": _map_location(loc_raw),
                    "location_raw": loc_raw,
                    "coat_hint": coat_hint,
                })

    return results


def _extract_entries(text: str) -> list[tuple[str, str, str]]:
    """
    Extract (name, sex, location) triplets from a block of text.
    Handles ♂ ♀ ? as sex markers.
    """
    # Normalise whitespace
    text = re.sub(r"\s+", " ", text)

    # Find all positions of sex markers
    # Pattern: (Name words)(sex_marker)(Location words until next Name or end)
    # Name: 1-3 capitalised words (allow accented chars)
    NAME_PAT = r"[A-ZÁÉÍÓÚÀÈÌÒÙÄÖÜÑ][a-záéíóúàèìòùäöüñ]+(?:\s+[A-ZÁÉÍÓÚÀÈÌÒÙÄÖÜÑ][a-záéíóúàèìòùäöüñ]+)*"
    SEX_PAT = r"[♂♀?]"
    LOC_PAT = r"[A-Za-z][A-Za-z0-9'\s\-]*"

    # Full pattern: Name SEX Location
    pattern = re.compile(
        rf"({NAME_PAT})\s*({SEX_PAT})\s+({LOC_PAT}?)(?=\s+{NAME_PAT}\s*[♂♀?]|$)",
        re.UNICODE,
    )

    results = []
    for m in pattern.finditer(text):
        name = m.group(1).strip()
        sex_sym = m.group(2)
        loc = m.group(3).strip()

        # Clean up location: strip trailing page numbers / stray words
        loc = re.sub(r"\s*\d+\s*$", "", loc).strip()

        # Map sex symbol to M/F/Unknown
        if sex_sym == "♂":
            sex = "M"
        elif sex_sym == "♀":
            sex = "F"
        else:
            sex = "Unknown"

        # Skip obviously bad parses (loc too short / empty)
        if not name or len(name) < 2:
            continue

        results.append((name, sex, loc))

    return results
