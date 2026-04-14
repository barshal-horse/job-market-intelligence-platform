from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from html import unescape
from typing import Any

import httpx
from dateutil import parser as date_parser


REMOTIVE_API_URL = "https://remotive.com/api/remote-jobs"
DEFAULT_QUERIES = ["data engineer", "analytics engineer", "data analyst", "machine learning engineer", "ai engineer"]
ALLOWED_KEYWORDS = (
    "data",
    "analytics",
    "analyst",
    "machine learning",
    "ml",
    "ai",
    "llm",
)


@dataclass
class LiveFetchResult:
    provider: str
    fetched: int
    normalized: list[dict]


def _strip_html(value: str) -> str:
    return re.sub(r"<[^>]+>", " ", unescape(value)).replace("\n", " ").strip()


def _parse_salary(raw_salary: str) -> tuple[int, int, str]:
    if not raw_salary:
        return 0, 0, "USD"

    currency = "USD"
    if "€" in raw_salary:
        currency = "EUR"
    elif "£" in raw_salary:
        currency = "GBP"
    elif "₹" in raw_salary or "INR" in raw_salary.upper():
        currency = "INR"

    numbers = [int(match.replace(",", "")) for match in re.findall(r"\d[\d,]*", raw_salary)]
    if not numbers:
        return 0, 0, currency
    if len(numbers) == 1:
        return numbers[0], numbers[0], currency
    return min(numbers[:2]), max(numbers[:2]), currency


def _infer_experience_level(title: str, description: str) -> str:
    text = f"{title} {description}".lower()
    if any(keyword in text for keyword in ("senior", "lead", "staff", "principal")):
        return "Senior"
    if any(keyword in text for keyword in ("mid", "intermediate", "3+ years", "4+ years", "5+ years")):
        return "Mid"
    return "Entry"


def _map_category(title: str, source_category: str, tags: list[str]) -> str:
    title_text = title.lower()
    text = " ".join([title, source_category, *tags]).lower()

    if any(keyword in title_text for keyword in ("data engineer", "data platform", "etl", "pipeline")):
        return "Data Engineering"
    if any(keyword in title_text for keyword in ("analytics engineer", "dbt", "semantic")):
        return "Analytics Engineering"
    if any(keyword in title_text for keyword in ("analyst", "business intelligence", "bi developer")):
        return "Analytics"
    if any(keyword in title_text for keyword in ("ml", "machine learning", "ai engineer", "llm", "data scientist")):
        return "Applied AI"

    if any(keyword in text for keyword in ("dbt", "analytics engineer", "semantic", "warehouse")):
        return "Analytics Engineering"
    if any(keyword in text for keyword in ("analyst", "analytics", "bi", "business intelligence", "reporting")):
        return "Analytics"
    if any(keyword in text for keyword in ("ml", "machine learning", "ai", "llm", "rag", "data scientist")):
        return "Applied AI"
    return "Data Engineering"


def _normalize_remotive_job(job: dict[str, Any]) -> dict | None:
    title = str(job.get("title", "")).strip()
    description = _strip_html(str(job.get("description", "")))
    combined_text = f"{title} {description}".lower()

    if not any(keyword in combined_text for keyword in ALLOWED_KEYWORDS):
        return None

    salary_min, salary_max, currency = _parse_salary(str(job.get("salary", "")))
    posted_date = date_parser.isoparse(str(job.get("publication_date"))).date().isoformat()
    tags = [str(tag).strip() for tag in job.get("tags", []) if str(tag).strip()]

    return {
        "source_id": f"remotive-{job['id']}",
        "title": title,
        "company": str(job.get("company_name", "Unknown")).strip(),
        "location": str(job.get("candidate_required_location") or "Remote").strip(),
        "job_type": str(job.get("job_type") or "Full-time").strip(),
        "experience_level": _infer_experience_level(title, description),
        "category": _map_category(title, str(job.get("category", "")), tags),
        "salary_min": salary_min,
        "salary_max": salary_max,
        "currency": currency,
        "posted_date": posted_date,
        "description": description[:1200],
        "remote_type": "Remote",
        "source": "Remotive",
        "skills": tags or ["python", "sql"],
    }


def fetch_remotive_jobs(queries: list[str] | None = None, limit_per_query: int = 20, timeout: int = 30) -> LiveFetchResult:
    queries = queries or DEFAULT_QUERIES
    normalized: list[dict] = []

    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        response = client.get(REMOTIVE_API_URL)
        response.raise_for_status()
        jobs = response.json().get("jobs", [])

        query_limits = {query.lower(): 0 for query in queries}
        lowered_queries = list(query_limits.keys())

        for job in jobs:
            searchable_text = " ".join(
                [
                    str(job.get("title", "")),
                    str(job.get("category", "")),
                    " ".join(str(tag) for tag in job.get("tags", [])),
                    str(job.get("description", "")),
                ]
            ).lower()

            matched_query = next((query for query in lowered_queries if query in searchable_text), None)
            if not matched_query:
                continue
            if query_limits[matched_query] >= limit_per_query:
                continue

            normalized_job = _normalize_remotive_job(job)
            if normalized_job:
                normalized.append(normalized_job)
                query_limits[matched_query] += 1

    deduplicated = {job["source_id"]: job for job in normalized}
    return LiveFetchResult(provider="Remotive", fetched=len(deduplicated), normalized=list(deduplicated.values()))
