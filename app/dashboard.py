from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

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


st.set_page_config(page_title="Job Market Intelligence", layout="wide")
ensure_seed_data()

st.title("Job Market Intelligence Platform")
st.caption("Track skill demand, hiring locations, and salary trends across data and AI roles.")

overview = get_overview()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Jobs", overview["total_jobs"])
col2.metric("Companies", overview["unique_companies"])
col3.metric("Locations", overview["unique_locations"])
col4.metric("Skills", overview["unique_skills"])
col5.metric("Avg Salary", f"${overview['average_salary']:,.0f}")

skills_df = pd.DataFrame(get_top_skills())
locations_df = pd.DataFrame(get_top_locations())
roles_df = pd.DataFrame(get_role_distribution())
salary_df = pd.DataFrame(get_high_paying_skills())
category_salary_df = pd.DataFrame(get_salary_summary_by_category())

tab_overview, tab_market, tab_explorer = st.tabs(["Overview", "Market Signals", "Listings Explorer"])

with tab_overview:
    left, right = st.columns(2)

    with left:
        st.subheader("Top In-Demand Skills")
        st.plotly_chart(
            px.bar(skills_df, x="demand", y="skill", orientation="h", title="Skill demand"),
            use_container_width=True,
        )

    with right:
        st.subheader("Top Hiring Locations")
        st.plotly_chart(
            px.bar(locations_df, x="openings", y="location", orientation="h", title="Open roles by city"),
            use_container_width=True,
        )

with tab_market:
    left, right = st.columns(2)

    with left:
        st.subheader("Role Distribution")
        st.plotly_chart(
            px.pie(roles_df, names="category", values="openings", title="Role categories"),
            use_container_width=True,
        )

    with right:
        st.subheader("Highest Paying Skills")
        st.plotly_chart(
            px.bar(salary_df, x="avg_salary", y="skill", orientation="h", title="Average salary by skill"),
            use_container_width=True,
        )

    st.subheader("Salary by Role Category")
    st.plotly_chart(
        px.bar(
            category_salary_df,
            x="category",
            y="avg_salary",
            color="openings",
            title="Average salary by category",
        ),
        use_container_width=True,
    )

with tab_explorer:
    st.subheader("Explore Listings")

    job_frame = pd.DataFrame(get_jobs())
    category_options = ["All"] + sorted(job_frame["category"].unique().tolist())
    location_options = ["All"] + sorted(job_frame["location"].unique().tolist())
    remote_options = ["All"] + sorted(job_frame["remote_type"].unique().tolist())
    skill_options = ["All"] + sorted(skills_df["skill"].tolist())

    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
    selected_category = filter_col1.selectbox("Category", category_options)
    selected_location = filter_col2.selectbox("Location", location_options)
    selected_remote = filter_col3.selectbox("Remote Type", remote_options)
    selected_skill = filter_col4.selectbox("Skill", skill_options)

    search_term = st.text_input("Search jobs by title, company, or description")
    min_salary = int(job_frame["salary_min"].min())
    max_salary = int(job_frame["salary_max"].max())
    selected_min_salary = st.slider("Minimum salary", min_salary, max_salary, min_salary, step=50000)

    filtered_jobs = get_jobs(
        category=None if selected_category == "All" else selected_category,
        location=None if selected_location == "All" else selected_location,
        remote_type=None if selected_remote == "All" else selected_remote,
        skill=None if selected_skill == "All" else selected_skill,
        min_salary=selected_min_salary,
        search=search_term or None,
    )

    filtered_frame = pd.DataFrame(filtered_jobs)
    st.caption(f"{len(filtered_frame)} listings matched your filters.")
    st.dataframe(filtered_frame, use_container_width=True, hide_index=True)
