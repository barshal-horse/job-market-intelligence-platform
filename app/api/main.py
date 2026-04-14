from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Query

from app.services.analytics import (
    get_high_paying_skills,
    get_jobs,
    get_overview,
    get_role_distribution,
    get_salary_summary_by_category,
    get_top_locations,
    get_top_skills,
)
from app.services.bootstrap import ensure_seed_data


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_seed_data()
    yield


app = FastAPI(title="Job Market Intelligence Platform", version="1.0.0", lifespan=lifespan)


@app.get("/health")
def healthcheck() -> dict:
    return {"status": "ok"}


@app.get("/analytics/overview")
def overview() -> dict:
    return get_overview()


@app.get("/analytics/top-skills")
def top_skills(limit: int = Query(default=10, ge=1, le=25)) -> list[dict]:
    return get_top_skills(limit=limit)


@app.get("/analytics/top-locations")
def top_locations(limit: int = Query(default=10, ge=1, le=25)) -> list[dict]:
    return get_top_locations(limit=limit)


@app.get("/analytics/role-distribution")
def role_distribution() -> list[dict]:
    return get_role_distribution()


@app.get("/analytics/high-paying-skills")
def high_paying_skills(limit: int = Query(default=10, ge=1, le=25)) -> list[dict]:
    return get_high_paying_skills(limit=limit)


@app.get("/analytics/salary-summary")
def salary_summary() -> list[dict]:
    return get_salary_summary_by_category()


@app.get("/jobs")
def jobs(
    category: str | None = None,
    location: str | None = None,
    remote_type: str | None = None,
    skill: str | None = None,
    min_salary: int | None = Query(default=None, ge=0),
    search: str | None = None,
) -> list[dict]:
    return get_jobs(
        category=category,
        location=location,
        remote_type=remote_type,
        skill=skill,
        min_salary=min_salary,
        search=search,
    )
