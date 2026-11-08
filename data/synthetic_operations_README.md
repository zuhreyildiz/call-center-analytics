# Synthetic operations data

`synthetic_operations.csv` contains one row for every `call_id` in `call_center_data.csv`.

Join key:

```text
synthetic_operations.call_id = fact_calls.call_id
```

The file keeps common fields such as agent, date, time, topic, answered, and resolved, then adds operational decision-support fields such as team, queue, channel, repeat call, escalation, sentiment, forecast volume, staffing requirement, and staffing gap.

The generator is deterministic. Re-running `scripts/generate_synthetic_operations.py` recreates the same 5,000 rows.
