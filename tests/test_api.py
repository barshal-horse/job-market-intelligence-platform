from __future__ import annotations

from fastapi.testclient import TestClient

from app.api.main import app


client = TestClient(app)


def test_health_and_overview_endpoints() -> None:
    health_response = client.get("/health")
    overview_response = client.get("/analytics/overview")

    assert health_response.status_code == 200
    assert health_response.json() == {"status": "ok"}
    assert overview_response.status_code == 200
    assert overview_response.json()["total_jobs"] >= 24


def test_jobs_filters_and_salary_summary() -> None:
    jobs_response = client.get("/jobs", params={"skill": "dbt", "min_salary": 1500000})
    salary_response = client.get("/analytics/salary-summary")

    assert jobs_response.status_code == 200
    assert salary_response.status_code == 200
    assert len(jobs_response.json()) >= 1
    assert any(item["category"] == "Applied AI" for item in salary_response.json())
