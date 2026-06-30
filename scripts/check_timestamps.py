"""Check timestamp validity for synthetic video annotations."""
from __future__ import annotations

import csv
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "video_events.csv"
with DATA.open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))

invalid = []
for row in rows:
    if int(row["end_ms"]) <= int(row["start_ms"]):
        invalid.append(row)

print("Timestamp QA")
print("------------")
print(f"Rows reviewed: {len(rows)}")
print(f"Invalid timestamp ranges: {len(invalid)}")
for row in invalid:
    print(f"- {row['video_id']} {row['event_id']}: end_ms <= start_ms")
