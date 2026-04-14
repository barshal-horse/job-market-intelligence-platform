from __future__ import annotations

import csv
from pathlib import Path

from app.db.database import get_connection


def load_jobs_from_csv(csv_path: Path, db_path: Path) -> int:
    rows_loaded = 0

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)

        with get_connection(db_path) as connection:
            for row in reader:
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

                job_id = cursor.lastrowid
                skills = [skill.strip().lower() for skill in row["skills"].split(";") if skill.strip()]
                connection.executemany(
                    "INSERT INTO job_skills (job_id, skill) VALUES (?, ?)",
                    [(job_id, skill) for skill in skills],
                )
                rows_loaded += 1

            connection.commit()

    return rows_loaded
