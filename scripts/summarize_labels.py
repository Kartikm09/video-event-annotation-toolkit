"""Summarize synthetic video annotation labels."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "video_events.csv"
with DATA.open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))

labels = Counter(row["label"] for row in rows)
statuses = Counter(row["review_status"] for row in rows)
print("Video label summary")
print("-------------------")
for label, count in labels.most_common():
    print(f"- {label}: {count}")
print("Review statuses:")
for status, count in statuses.most_common():
    print(f"- {status}: {count}")
