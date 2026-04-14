from __future__ import annotations

from pathlib import Path

from app.db.database import DB_PATH, database_exists, initialize_database
from app.services.ingest import load_jobs_from_csv


SAMPLE_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "sample_jobs.csv"


def ensure_seed_data(db_path: Path | None = None, csv_path: Path | None = None) -> Path:
    target_db = db_path or DB_PATH
    source_csv = csv_path or SAMPLE_DATA_PATH

    if database_exists(target_db):
        return target_db

    initialize_database(target_db)
    load_jobs_from_csv(source_csv, target_db)
    return target_db
