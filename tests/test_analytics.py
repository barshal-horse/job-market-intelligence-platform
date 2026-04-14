from __future__ import annotations

from pathlib import Path

from app.db.database import initialize_database
from app.services.analytics import (
    get_high_paying_skills,
    get_jobs,
    get_overview,
    get_role_distribution,
    get_top_locations,
    get_top_skills,
)
from app.services.ingest import load_jobs_from_csv


def build_test_database(tmp_path: Path) -> Path:
    db_path = tmp_path / "test_jobs.db"
    csv_path = Path(__file__).resolve().parents[1] / "data" / "sample_jobs.csv"
    initialize_database(db_path)
    load_jobs_from_csv(csv_path, db_path)
    return db_path


def test_overview_metrics(tmp_path: Path) -> None:
    db_path = build_test_database(tmp_path)
    overview = get_overview(db_path)

    assert overview["total_jobs"] == 24
    assert overview["unique_companies"] >= 20
    assert overview["unique_locations"] >= 5
    assert overview["unique_skills"] >= 20


def test_top_skills_contains_sql(tmp_path: Path) -> None:
    db_path = build_test_database(tmp_path)
    skills = get_top_skills(limit=5, db_path=db_path)

    assert any(item["skill"] == "sql" for item in skills)


def test_locations_and_roles_return_data(tmp_path: Path) -> None:
    db_path = build_test_database(tmp_path)

    assert len(get_top_locations(limit=5, db_path=db_path)) == 5
    assert any(item["category"] == "Data Engineering" for item in get_role_distribution(db_path))


def test_high_paying_skills_and_jobs_filters(tmp_path: Path) -> None:
    db_path = build_test_database(tmp_path)

    high_paying_skills = get_high_paying_skills(limit=5, db_path=db_path)
    remote_jobs = get_jobs(remote_type="Remote", db_path=db_path)

    assert len(high_paying_skills) == 5
    assert all(job["remote_type"] == "Remote" for job in remote_jobs)
