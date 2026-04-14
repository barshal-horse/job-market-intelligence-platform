from __future__ import annotations

import csv
from pathlib import Path

from app.db.database import get_connection


def _upsert_job(connection, row: dict) -> int:
    existing = connection.execute(
        "SELECT job_id FROM jobs WHERE source_id = ?",
        (row["source_id"],),
    ).fetchone()

    if existing:
        job_id = int(existing["job_id"])
        connection.execute(
            """
            UPDATE jobs
            SET title = ?, company = ?, location = ?, job_type = ?,
                experience_level = ?, category = ?, salary_min = ?, salary_max = ?,
                currency = ?, posted_date = ?, description = ?, remote_type = ?, source = ?
            WHERE source_id = ?
            """,
            (
                row["title"],
                row["company"],
                row["location"],
                row["job_type"],
                row["experience_level"],
                row["category"],
                int(row["salary_min"]),
                int(row["salary_max"]),
                row["currency"],
                row["posted_date"],
                row["description"],
                row["remote_type"],
                row["source"],
                row["source_id"],
            ),
        )
        connection.execute("DELETE FROM job_skills WHERE job_id = ?", (job_id,))
        return job_id

    cursor = connection.execute(
        """
        INSERT INTO jobs (
            source_id, title, company, location, job_type,
            experience_level, category, salary_min, salary_max,
            currency, posted_date, description, remote_type, source
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            row["source_id"],
            row["title"],
            row["company"],
            row["location"],
            row["job_type"],
            row["experience_level"],
            row["category"],
            int(row["salary_min"]),
            int(row["salary_max"]),
            row["currency"],
            row["posted_date"],
            row["description"],
            row["remote_type"],
            row["source"],
        ),
    )
    return int(cursor.lastrowid)


def _insert_skills(connection, job_id: int, raw_skills: str | list[str]) -> None:
    if isinstance(raw_skills, str):
        skills = [skill.strip().lower() for skill in raw_skills.split(";") if skill.strip()]
    else:
        skills = [skill.strip().lower() for skill in raw_skills if skill.strip()]

    connection.executemany(
        "INSERT INTO job_skills (job_id, skill) VALUES (?, ?)",
        [(job_id, skill) for skill in skills],
    )


def load_jobs_from_csv(csv_path: Path, db_path: Path) -> int:
    rows_loaded = 0

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)

        with get_connection(db_path) as connection:
            for row in reader:
                job_id = _upsert_job(connection, row)
                _insert_skills(connection, job_id, row["skills"])
                rows_loaded += 1

            connection.commit()

    return rows_loaded


def load_jobs(rows: list[dict], db_path: Path) -> int:
    rows_loaded = 0

    with get_connection(db_path) as connection:
        for row in rows:
            job_id = _upsert_job(connection, row)
            _insert_skills(connection, job_id, row["skills"])
            rows_loaded += 1

        connection.commit()

    return rows_loaded
