# Contact Center Operations & Customer Experience Analytics

An end-to-end portfolio project for analyzing contact-center operations, agent performance, customer experience, and data quality with PostgreSQL and Power BI.

## Dashboard pages

- **Executive Overview** — total calls, monthly volume, answer rate, average satisfaction, and response speed
- **Agent Performance** — calls, satisfaction, and response speed by agent
- **Topic Performance** — call volume, satisfaction, and response speed by topic
- **Customer Experience** — answered/unanswered, resolved/unresolved, and satisfaction analysis
- **Data Quality** — completeness checks and missing satisfaction records

## Live Power BI dashboard

The dashboard can be viewed without signing in through Power BI's **Publish to web** feature:

> **Live report link:** Add the Power BI `app.powerbi.com/view?...` link here after publishing the report.

Important: Publish to web makes the report and its data publicly accessible. Use this option only with the synthetic portfolio data in this repository—never with confidential customer or company data.

## Key findings from the current dataset

- 5,000 total calls
- 4,054 answered calls (81.08%)
- 946 unanswered calls (18.92%)
- Average satisfaction: 3.40 / 5
- Average speed of answer: 67.52 seconds
- 4,054 records contain a satisfaction rating; 946 records are missing one

## Architecture

```text
CSV -> PostgreSQL staging_calls -> fact_calls / analytics views -> Power BI
```

The loader refreshes the staging table, validates the original Kaggle headers, converts talk duration to seconds, and upserts records into `fact_calls` by `call_id`.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Load data

```bash
python3 scripts/load_call_center.py data/call_center_data.csv
```

## SQL objects

- `fact_calls` — cleaned analytical fact table
- `vw_daily_operations` — daily operational trends
- `vw_agent_performance` — agent-level KPIs
- `vw_topic_performance` — topic-level KPIs
- `vw_data_quality` — completeness and quality checks

## Skills demonstrated

SQL data modeling, ETL validation, KPI definition, operational analytics, Power BI dashboard design, data-quality analysis, and communicating insights to non-technical stakeholders.
