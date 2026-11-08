CREATE OR REPLACE VIEW vw_daily_operations AS
SELECT
    call_date,
    COUNT(*) AS total_calls,
    COUNT(*) FILTER (WHERE answered = 'Y') AS answered_calls,
    COUNT(*) FILTER (WHERE answered = 'N') AS unanswered_calls,
    COUNT(*) FILTER (WHERE resolved = 'Y') AS resolved_calls,
    ROUND(
        COUNT(*) FILTER (WHERE answered = 'Y')::numeric / NULLIF(COUNT(*), 0),
        4
    ) AS answer_rate,
    ROUND(
        COUNT(*) FILTER (WHERE resolved = 'Y')::numeric
        / NULLIF(COUNT(*) FILTER (WHERE answered = 'Y'), 0),
        4
    ) AS resolution_rate,
    ROUND(AVG(speed_of_answer_seconds), 2) AS avg_speed_of_answer_seconds,
    ROUND(AVG(talk_duration_seconds), 2) AS avg_talk_duration_seconds,
    ROUND(AVG(satisfaction_rating), 2) AS avg_satisfaction
FROM fact_calls
GROUP BY call_date;

CREATE OR REPLACE VIEW vw_agent_performance AS
SELECT
    agent_name,
    COUNT(*) AS total_calls,
    COUNT(*) FILTER (WHERE answered = 'Y') AS answered_calls,
    COUNT(*) FILTER (WHERE resolved = 'Y') AS resolved_calls,
    ROUND(
        COUNT(*) FILTER (WHERE resolved = 'Y')::numeric
        / NULLIF(COUNT(*) FILTER (WHERE answered = 'Y'), 0),
        4
    ) AS resolution_rate,
    ROUND(AVG(speed_of_answer_seconds), 2) AS avg_speed_of_answer_seconds,
    ROUND(AVG(talk_duration_seconds), 2) AS avg_talk_duration_seconds,
    ROUND(AVG(satisfaction_rating), 2) AS avg_satisfaction
FROM fact_calls
GROUP BY agent_name;

CREATE OR REPLACE VIEW vw_topic_performance AS
SELECT
    topic,
    COUNT(*) AS total_calls,
    COUNT(*) FILTER (WHERE answered = 'Y') AS answered_calls,
    COUNT(*) FILTER (WHERE resolved = 'Y') AS resolved_calls,
    ROUND(
        COUNT(*) FILTER (WHERE resolved = 'Y')::numeric
        / NULLIF(COUNT(*) FILTER (WHERE answered = 'Y'), 0),
        4
    ) AS resolution_rate,
    ROUND(AVG(speed_of_answer_seconds), 2) AS avg_speed_of_answer_seconds,
    ROUND(AVG(talk_duration_seconds), 2) AS avg_talk_duration_seconds,
    ROUND(AVG(satisfaction_rating), 2) AS avg_satisfaction
FROM fact_calls
GROUP BY topic;

CREATE OR REPLACE VIEW vw_data_quality AS
SELECT
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE call_id IS NULL OR call_id = '') AS missing_call_ids,
    COUNT(*) FILTER (WHERE call_date IS NULL) AS missing_dates,
    COUNT(*) FILTER (WHERE agent_name IS NULL OR agent_name = '') AS missing_agents,
    COUNT(*) FILTER (WHERE topic IS NULL OR topic = '') AS missing_topics,
    COUNT(*) FILTER (WHERE satisfaction_rating IS NULL) AS missing_satisfaction,
    COUNT(DISTINCT call_id) AS distinct_call_ids,
    MAX(loaded_at) AS last_loaded_at
FROM fact_calls;
