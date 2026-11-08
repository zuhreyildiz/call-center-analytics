"""Generate deterministic synthetic operational data for the call-center model."""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "call_center_data.csv"
OUTPUT = ROOT / "data" / "synthetic_operations.csv"

TEAMS = ["North Operations", "Central Operations", "South Operations"]
QUEUES = ["General Support", "Technical Support", "Billing", "Retention"]
CHANNELS = ["Phone", "Chat", "Email"]
SENTIMENTS = ["Positive", "Neutral", "Negative"]


def bounded(value: float, low: int, high: int) -> int:
    return max(low, min(high, round(value)))


def main() -> None:
    random.seed(20261108)

    with SOURCE.open("r", encoding="utf-8-sig", newline="") as source_file:
        source_rows = list(csv.DictReader(source_file, delimiter=";"))

    fieldnames = [
        "call_id",
        "agent_name",
        "call_date",
        "call_time",
        "topic",
        "answered",
        "resolved",
        "team",
        "queue",
        "channel",
        "wait_seconds",
        "talk_seconds",
        "satisfaction_rating",
        "repeat_call",
        "escalated",
        "sentiment",
        "sla_target_seconds",
        "forecast_call_volume",
        "required_staff",
        "actual_staff",
        "staffing_gap",
    ]

    output_rows = []
    for index, row in enumerate(source_rows):
        call_id = row["Call Id"]
        answered = row["Answered (Y/N)"] == "Y"
        resolved = row["Resolved"] == "Y"
        wait_seconds = (
            int(row["Speed of answer in seconds"])
            if row["Speed of answer in seconds"].strip()
            else random.randint(60, 180)
        )
        talk_duration = row["AvgTalkDuration"].strip()
        if talk_duration:
            talk_time = datetime.strptime(talk_duration, "%H:%M:%S")
            talk_seconds = talk_time.hour * 3600 + talk_time.minute * 60 + talk_time.second
        else:
            talk_seconds = random.randint(30, 360)
        satisfaction = row["Satisfaction rating"].strip()
        topic = row["Topic"]

        queue = {
            "Technical Support": "Technical Support",
            "Payment related": "Billing",
            "Admin Support": "General Support",
            "Contract related": "Retention",
            "Streaming": "General Support",
        }.get(topic, "General Support")
        channel = random.choices(CHANNELS, weights=[72, 18, 10], k=1)[0]
        team = random.choice(TEAMS)

        if not answered:
            satisfaction = ""
            sentiment = random.choices(SENTIMENTS, weights=[5, 20, 75], k=1)[0]
            repeat_call = "Y"
            escalated = "Y"
        else:
            if satisfaction:
                rating = int(float(satisfaction))
            else:
                rating = 3
            sentiment = "Positive" if rating >= 4 else "Negative" if rating <= 2 else "Neutral"
            repeat_call = "Y" if (not resolved or rating <= 2) and random.random() < 0.45 else "N"
            escalated = "Y" if (not resolved or rating <= 2) and random.random() < 0.30 else "N"

        interval_start = datetime.strptime(f"{row['Date']} {row['Time']}", "%Y-%m-%d %H:%M:%S")
        interval_key = interval_start.replace(minute=(interval_start.minute // 30) * 30, second=0)
        hour_factor = 1.35 if 10 <= interval_key.hour <= 12 or 14 <= interval_key.hour <= 16 else 0.80
        forecast_volume = bounded(145 * hour_factor + random.gauss(0, 12), 60, 240)
        required_staff = max(3, round(forecast_volume / 22))
        actual_staff = max(2, required_staff + random.choice([-2, -1, 0, 0, 1]))

        output_rows.append(
            {
                "call_id": call_id,
                "agent_name": row["Agent"],
                "call_date": row["Date"],
                "call_time": row["Time"],
                "topic": topic,
                "answered": row["Answered (Y/N)"],
                "resolved": row["Resolved"],
                "team": team,
                "queue": queue,
                "channel": channel,
                "wait_seconds": wait_seconds,
                "talk_seconds": talk_seconds,
                "satisfaction_rating": satisfaction,
                "repeat_call": repeat_call,
                "escalated": escalated,
                "sentiment": sentiment,
                "sla_target_seconds": 60,
                "forecast_call_volume": forecast_volume,
                "required_staff": required_staff,
                "actual_staff": actual_staff,
                "staffing_gap": actual_staff - required_staff,
            }
        )

    with OUTPUT.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Üretilen satır: {len(output_rows)}")
    print(f"Dosya: {OUTPUT}")


if __name__ == "__main__":
    main()
