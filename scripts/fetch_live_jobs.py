from __future__ import annotations

import argparse
from pathlib import Path
import sys


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.services.ingest import load_jobs
from app.services.bootstrap import ensure_seed_data
from app.services.live_sources import DEFAULT_QUERIES, fetch_remotive_jobs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch live jobs into the local analytics database.")
    parser.add_argument(
        "--query",
        action="append",
        dest="queries",
        help="Search query to send to the live provider. Repeat the flag to add multiple queries.",
    )
    parser.add_argument(
        "--limit-per-query",
        type=int,
        default=20,
        help="Maximum jobs to ingest per query.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db_path = BASE_DIR / "data" / "job_market.db"
    ensure_seed_data(db_path=db_path)

    queries = args.queries or DEFAULT_QUERIES
    result = fetch_remotive_jobs(queries=queries, limit_per_query=args.limit_per_query)
    loaded = load_jobs(result.normalized, db_path)

    print(f"Provider: {result.provider}")
    print(f"Queries: {', '.join(queries)}")
    print(f"Fetched and normalized: {result.fetched}")
    print(f"Loaded into database: {loaded}")


if __name__ == "__main__":
    main()
