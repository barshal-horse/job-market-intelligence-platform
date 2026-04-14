from __future__ import annotations

from pathlib import Path
import sys


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.db.database import initialize_database
from app.services.ingest import load_jobs_from_csv


def main() -> None:
    csv_path = BASE_DIR / "data" / "sample_jobs.csv"
    db_path = BASE_DIR / "data" / "job_market.db"

    initialize_database(db_path)
    loaded = load_jobs_from_csv(csv_path=csv_path, db_path=db_path)

    print(f"Database ready at: {db_path}")
    print(f"Loaded {loaded} job listings.")


if __name__ == "__main__":
    main()
