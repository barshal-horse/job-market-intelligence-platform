from __future__ import annotations

from app.services.live_sources import _normalize_remotive_job, _parse_salary


def test_parse_salary_handles_ranges() -> None:
    salary_min, salary_max, currency = _parse_salary("$120,000 - $150,000")

    assert salary_min == 120000
    assert salary_max == 150000
    assert currency == "USD"


def test_normalize_remotive_job_maps_data_role() -> None:
    raw_job = {
        "id": 123,
        "title": "Data Engineer",
        "company_name": "Example",
        "category": "Software Development",
        "tags": ["Python", "SQL", "Airflow"],
        "job_type": "Full-Time",
        "publication_date": "2026-04-14T10:00:00",
        "candidate_required_location": "Worldwide",
        "salary": "$120,000 - $150,000",
        "description": "<p>Build data pipelines and analytics models.</p>",
    }

    normalized = _normalize_remotive_job(raw_job)

    assert normalized is not None
    assert normalized["source_id"] == "remotive-123"
    assert normalized["category"] == "Data Engineering"
    assert normalized["skills"] == ["Python", "SQL", "Airflow"]
    assert normalized["salary_max"] == 150000
