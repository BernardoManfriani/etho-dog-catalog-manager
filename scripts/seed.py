"""
Script di seed per popolare il database con dati demo.

Uso:
    python scripts/seed.py

Crea 20 cani demo con dati variati.
Può essere eseguito più volte senza duplicati (controlla per nome+location).
"""
import os
import sys
from pathlib import Path

# Imposta il project root prima di qualsiasi import dall'app
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
os.environ["CATALOG_ROOT"] = str(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))

from app.repositories.db_factory import get_db, get_media_dir
from app.repositories.dog_repository import DogRepository
from app.repositories.photo_repository import PhotoRepository
from app.services.dog_service import DogService
from app.services.photo_service import PhotoService


DEMO_DOGS = [
    {"name": "Rex", "sex": "M", "location": "Rifugio A", "notes": "Pastore tedesco, amichevole"},
    {"name": "Luna", "sex": "F", "location": "Famiglia Foster 1", "notes": "Timida all'inizio"},
    {"name": "Briciola", "sex": "F", "location": "Rifugio B", "notes": "Meticcia, piccola taglia"},
    {"name": "Thor", "sex": "M", "location": "Rifugio A", "notes": "Rottweiler, ottimo carattere"},
    {"name": "Stella", "sex": "F", "location": "Rifugio C", "notes": "Labrador gialla, 3 anni"},
    {"name": "Artu", "sex": "M", "location": "Famiglia Foster 2", "notes": "Cerca casa definitiva"},
    {"name": "Fiocco", "sex": "M", "location": "Rifugio B", "notes": "Barboncino, anziano"},
    {"name": "Nuvola", "sex": "F", "location": "Rifugio A", "notes": "Samoiedo, cucciola"},
    {"name": "Drago", "sex": "M", "location": "Rifugio D", "notes": "Boxer, giocherellone"},
    {"name": "Perla", "sex": "F", "location": "Famiglia Foster 3", "notes": "Setter, vaccinata"},
    {"name": "Birillo", "sex": "M", "location": "Rifugio C", "notes": "Beagle, adora i bambini"},
    {"name": "Ambra", "sex": "F", "location": "Rifugio A", "notes": "Golden, in attesa di adozione"},
    {"name": "Fulmine", "sex": "M", "location": "Rifugio B", "notes": "Dalmatico, 2 anni"},
    {"name": "Pippa", "sex": "F", "location": "Rifugio D", "notes": "Chihuahua mix"},
    {"name": "Argo", "sex": "M", "location": "Famiglia Foster 1", "notes": "Incrocio Husky"},
    {"name": "Mia", "sex": "F", "location": "Rifugio C", "notes": "Shih-Tzu, sterilizzata"},
    {"name": "Ugo", "sex": "M", "location": "Rifugio A", "notes": "Bulldog inglese"},
    {"name": "Rosa", "sex": "F", "location": "Famiglia Foster 2", "notes": "Cocker spaniel"},
    {"name": "Zeus", "sex": "M", "location": "Rifugio D", "notes": "Cane corso, adulto"},
    {"name": "Gaia", "sex": "F", "location": "Rifugio B", "notes": "Levriero, dolcissima"},
]

# Alcuni cani vengono segnati con foto da aggiornare
NEEDS_UPDATE_NAMES = {"Briciola", "Fiocco", "Pippa", "Rosa"}


def seed_dogs(dog_service: DogService) -> int:
    existing = {
        (d.name, d.location)
        for d in dog_service.search_dogs(status="active")
    }
    count = 0
    for data in DEMO_DOGS:
        key = (data["name"], data["location"])
        if key in existing:
            print(f"  Già presente: {data['name']}")
            continue
        dog_service.create_dog(
            name=data["name"],
            sex=data["sex"],
            location=data["location"],
            notes=data["notes"],
            needs_photo_update=data["name"] in NEEDS_UPDATE_NAMES,
        )
        print(f"  Aggiunto: {data['name']}")
        count += 1
    return count


def main() -> None:
    print(f"Project root: {PROJECT_ROOT}")
    print("Connessione al database...")

    db = get_db()
    dog_repo = DogRepository(db)
    photo_repo = PhotoRepository(db)
    dog_service = DogService(dog_repo, photo_repo)

    print("Seeding cani demo...")
    count = seed_dogs(dog_service)
    print(f"\nSeed completato: {count} cani aggiunti.")

    total = len(dog_service.search_dogs(status="active"))
    print(f"Totale cani nel DB: {total}")


if __name__ == "__main__":
    main()
