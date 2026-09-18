"""Report invalid ranges and same-video overlapping event pairs."""
from __future__ import annotations

import argparse
import csv
from itertools import combinations
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "video_events.csv"


def timestamp_issues(rows):
    invalid = []
    valid = []
    for row in rows:
        start, end = int(row["start_ms"]), int(row["end_ms"])
        if end <= start:
            invalid.append(row)
        else:
            valid.append((row, start, end))
    overlaps = []
    for (first, start_a, end_a), (second, start_b, end_b) in combinations(valid, 2):
        if first["video_id"] == second["video_id"] and max(start_a, start_b) < min(end_a, end_b):
            overlaps.append((first, second))
    return invalid, overlaps


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path, nargs="?", default=DATA)
    parser.add_argument("--strict", action="store_true", help="Exit 1 when any invalid range or overlap needs review.")
    args = parser.parse_args()
    with args.csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    try:
        invalid, overlaps = timestamp_issues(rows)
    except (ValueError, KeyError, TypeError) as error:
        parser.error(f"invalid timestamp data: {error}")

    print("Timestamp QA")
    print("------------")
    print(f"Rows reviewed: {len(rows)}")
    print(f"Invalid timestamp ranges: {len(invalid)}")
    for row in invalid:
        print(f"- {row['video_id']} {row['event_id']}: end_ms <= start_ms")
    print(f"Overlapping event pairs: {len(overlaps)}")
    for first, second in overlaps:
        print(f"- {first['video_id']} {first['event_id']} / {second['event_id']}: overlap needs review")
    return int(args.strict and bool(invalid or overlaps))


if __name__ == "__main__":
    raise SystemExit(main())
