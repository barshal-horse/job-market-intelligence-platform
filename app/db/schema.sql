DROP TABLE IF EXISTS job_skills;
DROP TABLE IF EXISTS jobs;

CREATE TABLE jobs (
    job_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT NOT NULL,
    job_type TEXT NOT NULL,
    experience_level TEXT NOT NULL,
    category TEXT NOT NULL,
    salary_min INTEGER NOT NULL,
    salary_max INTEGER NOT NULL,
    currency TEXT NOT NULL,
    posted_date TEXT NOT NULL,
    description TEXT NOT NULL,
    remote_type TEXT NOT NULL,
    source TEXT NOT NULL
);

CREATE TABLE job_skills (
    job_id INTEGER NOT NULL,
    skill TEXT NOT NULL,
    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
);

CREATE INDEX idx_jobs_location ON jobs(location);
CREATE INDEX idx_jobs_category ON jobs(category);
CREATE INDEX idx_skills_skill ON job_skills(skill);
