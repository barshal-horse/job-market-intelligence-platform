from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.db.database import DB_PATH, get_connection


def _read_dataframe(query: str, db_path: Path | None = None, params: tuple | None = None) -> pd.DataFrame:
    with get_connection(db_path or DB_PATH) as connection:
        return pd.read_sql_query(query, connection, params=params or ())


def get_overview(db_path: Path | None = None) -> dict:
    jobs = _read_dataframe("SELECT * FROM jobs", db_path)
    skills = _read_dataframe("SELECT * FROM job_skills", db_path)

    average_salary = ((jobs["salary_min"] + jobs["salary_max"]) / 2).mean()

    return {
        "total_jobs": int(len(jobs)),
        "unique_companies": int(jobs["company"].nunique()),
        "unique_locations": int(jobs["location"].nunique()),
        "unique_skills": int(skills["skill"].nunique()),
        "average_salary": round(float(average_salary), 2),
    }


def get_top_skills(limit: int = 10, db_path: Path | None = None) -> list[dict]:
    query = """
        SELECT skill, COUNT(*) AS demand
        FROM job_skills
        GROUP BY skill
        ORDER BY demand DESC, skill ASC
        LIMIT ?
    """
    frame = _read_dataframe(query, db_path, (limit,))
    return frame.to_dict(orient="records")


def get_top_locations(limit: int = 10, db_path: Path | None = None) -> list[dict]:
    query = """
        SELECT location, COUNT(*) AS openings
        FROM jobs
        GROUP BY location
        ORDER BY openings DESC, location ASC
        LIMIT ?
    """
    frame = _read_dataframe(query, db_path, (limit,))
    return frame.to_dict(orient="records")


def get_role_distribution(db_path: Path | None = None) -> list[dict]:
    query = """
        SELECT category, COUNT(*) AS openings
        FROM jobs
        GROUP BY category
        ORDER BY openings DESC, category ASC
    """
    frame = _read_dataframe(query, db_path)
    return frame.to_dict(orient="records")


def get_high_paying_skills(limit: int = 10, db_path: Path | None = None) -> list[dict]:
    query = """
        SELECT
            js.skill,
            ROUND(AVG((j.salary_min + j.salary_max) / 2.0), 2) AS avg_salary,
            COUNT(*) AS openings
        FROM job_skills js
        JOIN jobs j ON j.job_id = js.job_id
        GROUP BY js.skill
        HAVING COUNT(*) >= 2
        ORDER BY avg_salary DESC, openings DESC, js.skill ASC
        LIMIT ?
    """
    frame = _read_dataframe(query, db_path, (limit,))
    return frame.to_dict(orient="records")


def get_jobs(
    category: str | None = None,
    location: str | None = None,
    remote_type: str | None = None,
    skill: str | None = None,
    min_salary: int | None = None,
    search: str | None = None,
    db_path: Path | None = None,
) -> list[dict]:
    filters = []
    params: list[str | int] = []
    joins = ""

    if category:
        filters.append("category = ?")
        params.append(category)
    if location:
        filters.append("location = ?")
        params.append(location)
    if remote_type:
        filters.append("remote_type = ?")
        params.append(remote_type)
    if skill:
        joins = "JOIN job_skills js ON js.job_id = jobs.job_id"
        filters.append("js.skill = ?")
        params.append(skill.lower())
    if min_salary is not None:
        filters.append("salary_max >= ?")
        params.append(min_salary)
    if search:
        filters.append("(title LIKE ? OR company LIKE ? OR description LIKE ?)")
        search_value = f"%{search}%"
        params.extend([search_value, search_value, search_value])

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
    query = f"""
        SELECT
            DISTINCT jobs.title, jobs.company, jobs.location, jobs.category, jobs.experience_level,
            jobs.salary_min, jobs.salary_max, jobs.remote_type, jobs.posted_date, jobs.source
        FROM jobs
        {joins}
        {where_clause}
        ORDER BY jobs.salary_max DESC, jobs.posted_date DESC
    """
    frame = _read_dataframe(query, db_path, tuple(params))
    return frame.to_dict(orient="records")


def get_salary_summary_by_category(db_path: Path | None = None) -> list[dict]:
    query = """
        SELECT
            category,
            ROUND(AVG((salary_min + salary_max) / 2.0), 2) AS avg_salary,
            MIN(salary_min) AS min_salary,
            MAX(salary_max) AS max_salary,
            COUNT(*) AS openings
        FROM jobs
        GROUP BY category
        ORDER BY avg_salary DESC, category ASC
    """
    frame = _read_dataframe(query, db_path)
    return frame.to_dict(orient="records")
