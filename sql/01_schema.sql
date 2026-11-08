CREATE TABLE IF NOT EXISTS staging_calls (
    call_id VARCHAR(50),
    agent_name VARCHAR(100),
    call_date DATE,
    call_time TIME,
    topic VARCHAR(100),
    answered VARCHAR(5),
    resolved VARCHAR(5),
    speed_of_answer_seconds INT,
    avg_talk_duration VARCHAR(20),
    satisfaction_rating DECIMAL(3,2)
);

CREATE TABLE IF NOT EXISTS fact_calls (
    call_id VARCHAR(50) PRIMARY KEY,
    agent_name VARCHAR(100),
    call_date DATE,
    call_time TIME,
    topic VARCHAR(100),
    answered VARCHAR(5),
    resolved VARCHAR(5),
    speed_of_answer_seconds INT,
    talk_duration_seconds INT,
    satisfaction_rating DECIMAL(3,2),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
