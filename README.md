# Job Market Intelligence Platform

A portfolio-ready data application that transforms raw job listings into an analytics warehouse, exposes hiring intelligence through a REST API, and visualizes market signals in an interactive dashboard.

## Overview

This project is designed to demonstrate the kind of work expected from a strong early-career `Data / Analytics / Applied AI Engineer`:

- ingesting and modeling operational data
- building analytics-friendly storage
- exposing reusable application endpoints
- turning raw data into decision-ready insights

The included dataset focuses on India-based `analytics`, `data engineering`, and `applied AI` roles so the project is easy to explain in interviews and directly relevant to salary and skill-trend conversations.

## Key Capabilities

- job listing ingestion from CSV into a normalized SQLite warehouse
- separate skill fact table for demand and salary analysis
- FastAPI endpoints for reusable market intelligence queries
- Streamlit dashboard with overview, market signals, and filtered listing explorer views
- automatic local bootstrap so a fresh clone can run without manual database prep
- test coverage for both analytics functions and public API endpoints

## Architecture

```text
sample_jobs.csv
      |
      v
scripts/bootstrap.py
      |
      v
SQLite warehouse
  - jobs
  - job_skills
      |
      +--> app/services/analytics.py
                |
                +--> FastAPI app
                +--> Streamlit dashboard
```

## Tech Stack

- `Python 3.12`
- `SQLite`
- `Pandas`
- `FastAPI`
- `Streamlit`
- `Plotly`
- `Pytest`

## Project Structure

```text
app/
  api/
    main.py
  db/
    database.py
    schema.sql
  services/
    analytics.py
    bootstrap.py
    ingest.py
  dashboard.py
data/
  sample_jobs.csv
scripts/
  bootstrap.py
tests/
  test_analytics.py
  test_api.py
```

## Quickstart

### 1. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Seed the local analytics database

```powershell
python scripts\bootstrap.py
```

### 3b. Optional: Fetch live jobs from Remotive

This project also supports live ingestion from Remotive's public jobs API, filtered toward `data`, `analytics`, and `AI` roles.

```powershell
python scripts\fetch_live_jobs.py
```

You can also provide targeted search queries:

```powershell
python scripts\fetch_live_jobs.py --query "data engineer" --query "ml engineer" --limit-per-query 15
```

### 4. Run the API

```powershell
uvicorn app.api.main:app --reload
```

API docs will be available at `http://127.0.0.1:8000/docs`.

### 5. Run the dashboard

```powershell
streamlit run app/dashboard.py
```

## Example Questions This Project Answers

- Which skills appear most often across data and AI roles?
- Which cities currently show the highest concentration of openings?
- Which role categories have the highest average salary bands?
- Which skills are associated with higher-paying roles?
- Which jobs match a target skill, salary floor, and location preference?
- What do current live remote data and AI listings emphasize most often?

## API Endpoints

| Endpoint | Purpose |
| --- | --- |
| `/health` | service health check |
| `/analytics/overview` | top-level metrics for jobs, companies, skills, and average salary |
| `/analytics/top-skills` | most in-demand skills |
| `/analytics/top-locations` | cities with the highest number of openings |
| `/analytics/role-distribution` | role mix across analytics, data engineering, and applied AI |
| `/analytics/high-paying-skills` | skills ranked by average salary |
| `/analytics/salary-summary` | salary summary grouped by role category |
| `/jobs` | filtered listing explorer with category, location, remote type, skill, salary floor, and search |

## Testing

Run the full verification suite with:

```powershell
.\.venv\Scripts\python -m pytest -q
```

The test suite covers:

- database bootstrap and ingestion
- analytics summary outputs
- filtering behavior
- API endpoint health and response shapes


## Data Sources

- local seed dataset in `data/sample_jobs.csv`
- optional live ingestion from Remotive public jobs API via `scripts/fetch_live_jobs.py`
