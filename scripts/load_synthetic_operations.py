"""Load synthetic operational data into PostgreSQL."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import psycopg


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_FILE = PROJECT_ROOT / "sql" / "03_operations_schema.sql"
DEFAULT_CSV = PROJECT_ROOT / "data" / "synthetic_operations.csv"
COPY_COLUMNS = (
    "call_id, agent_name, call_date, call_time, topic, answered, resolved, "
    "team, queue, channel, wait_seconds, talk_seconds, satisfaction_rating, "
    "repeat_call, escalated, sentiment, sla_target_seconds, "
    "forecast_call_volume, required_staff, actual_staff, staffing_gap"
)


def connection_string() -> str:
    return os.getenv(
        "DATABASE_URL",
        "host=localhost port=5432 dbname=call_center_analytics user=postgres",
    )


def load_csv(csv_path: Path) -> None:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV bulunamadı: {csv_path}")

    with psycopg.connect(connection_string()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(SCHEMA_FILE.read_text(encoding="utf-8"))
            cursor.execute("TRUNCATE TABLE fact_operations")

            with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
                with cursor.copy(
                    f"COPY fact_operations ({COPY_COLUMNS}) FROM STDIN WITH "
                    "(FORMAT csv, HEADER true, DELIMITER ';', NULL '')"
                ) as copy:
                    while chunk := csv_file.read(1024 * 1024):
                        copy.write(chunk)

            cursor.execute("SELECT COUNT(*) FROM fact_operations")
            loaded_count = cursor.fetchone()[0]
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM fact_operations operations
                LEFT JOIN fact_calls calls USING (call_id)
                WHERE calls.call_id IS NULL
                """
            )
            unmatched_count = cursor.fetchone()[0]

        connection.commit()

    print(f"fact_operations toplam satır: {loaded_count}")
    print(f"fact_calls ile eşleşmeyen call_id: {unmatched_count}")


if __name__ == "__main__":
    csv_argument = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV
    load_csv(csv_argument)
