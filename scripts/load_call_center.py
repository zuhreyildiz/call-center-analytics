"""Load the call-center CSV into PostgreSQL.

The script is safe to run repeatedly: rows with the same call_id are updated
instead of duplicated.
"""

from __future__ import annotations

import csv
import io
import os
import sys
from pathlib import Path

import psycopg


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_FILE = PROJECT_ROOT / "sql" / "01_schema.sql"
VIEWS_FILE = PROJECT_ROOT / "sql" / "02_analytics_views.sql"
EXPECTED_COLUMNS = [
    "call_id",
    "agent_name",
    "call_date",
    "call_time",
    "topic",
    "answered",
    "resolved",
    "speed_of_answer_seconds",
    "avg_talk_duration",
    "satisfaction_rating",
]

HEADER_ALIASES = {
    "Call Id": "call_id",
    "Agent": "agent_name",
    "Date": "call_date",
    "Time": "call_time",
    "Topic": "topic",
    "Answered (Y/N)": "answered",
    "Resolved": "resolved",
    "Speed of answer in seconds": "speed_of_answer_seconds",
    "AvgTalkDuration": "avg_talk_duration",
    "Satisfaction rating": "satisfaction_rating",
}


def connection_string() -> str:
    return os.getenv(
        "DATABASE_URL",
        "host=localhost port=5432 dbname=call_center_analytics user=postgres",
    )


def normalized_csv(csv_path: Path) -> io.StringIO:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV bulunamadı: {csv_path}")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        sample = file.read(4096)
        file.seek(0)
        delimiter = csv.Sniffer().sniff(sample, delimiters=",;").delimiter
        reader = csv.DictReader(file, delimiter=delimiter)
        actual_columns = [column.strip() for column in (reader.fieldnames or [])]
        normalized_names = [HEADER_ALIASES.get(column, column) for column in actual_columns]
        missing = [column for column in EXPECTED_COLUMNS if column not in normalized_names]
        if missing:
            raise ValueError(
                "CSV başlığında eksik sütun(lar) var: " + ", ".join(missing)
            )

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=EXPECTED_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for row in reader:
            cleaned = {}
            for original_name, value in row.items():
                if original_name is not None:
                    normalized_name = HEADER_ALIASES.get(original_name.strip(), original_name.strip())
                    cleaned[normalized_name] = value.strip() if isinstance(value, str) else value
            writer.writerow({column: cleaned.get(column, "") for column in EXPECTED_COLUMNS})

        output.seek(0)
        return output


def load_csv(csv_path: Path) -> None:
    normalized_data = normalized_csv(csv_path)

    with psycopg.connect(connection_string()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(SCHEMA_FILE.read_text(encoding="utf-8"))
            cursor.execute("TRUNCATE TABLE staging_calls")

            with cursor.copy(
                    "COPY staging_calls (call_id, agent_name, call_date, call_time, "
                    "topic, answered, resolved, speed_of_answer_seconds, "
                    "avg_talk_duration, satisfaction_rating) "
                    "FROM STDIN WITH (FORMAT csv, HEADER true)"
            ) as copy:
                copy.write(normalized_data.getvalue())

            cursor.execute(
                """
                INSERT INTO fact_calls (
                    call_id, agent_name, call_date, call_time, topic,
                    answered, resolved, speed_of_answer_seconds,
                    talk_duration_seconds, satisfaction_rating
                )
                SELECT
                    call_id,
                    agent_name,
                    call_date,
                    call_time,
                    topic,
                    answered,
                    resolved,
                    speed_of_answer_seconds,
                    EXTRACT(EPOCH FROM avg_talk_duration::time)::int,
                    satisfaction_rating
                FROM staging_calls
                WHERE call_id IS NOT NULL AND call_id <> ''
                ON CONFLICT (call_id) DO UPDATE SET
                    agent_name = EXCLUDED.agent_name,
                    call_date = EXCLUDED.call_date,
                    call_time = EXCLUDED.call_time,
                    topic = EXCLUDED.topic,
                    answered = EXCLUDED.answered,
                    resolved = EXCLUDED.resolved,
                    speed_of_answer_seconds = EXCLUDED.speed_of_answer_seconds,
                    talk_duration_seconds = EXCLUDED.talk_duration_seconds,
                    satisfaction_rating = EXCLUDED.satisfaction_rating,
                    loaded_at = CURRENT_TIMESTAMP
                """
            )
            cursor.execute(VIEWS_FILE.read_text(encoding="utf-8"))

            cursor.execute("SELECT COUNT(*) FROM staging_calls")
            staged_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM fact_calls")
            fact_count = cursor.fetchone()[0]

        connection.commit()

    print(f"Staging'e alınan satır: {staged_count}")
    print(f"fact_calls toplam satır: {fact_count}")


if __name__ == "__main__":
    csv_argument = Path(sys.argv[1]) if len(sys.argv) > 1 else PROJECT_ROOT / "data" / "call_center_data.csv"
    load_csv(csv_argument)
