from __future__ import annotations

import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "job_market.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path or DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(db_path: Path | None = None) -> Path:
    target_path = db_path or DB_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)

    with get_connection(target_path) as connection:
        schema = SCHEMA_PATH.read_text(encoding="utf-8")
        connection.executescript(schema)
        connection.commit()

    return target_path


def database_exists(db_path: Path | None = None) -> bool:
    target_path = db_path or DB_PATH
    return target_path.exists() and target_path.stat().st_size > 0
