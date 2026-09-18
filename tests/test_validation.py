import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

def cli(script, rows, *, options=(), extra_json=None):
    with tempfile.TemporaryDirectory() as temp:
        source = Path(temp) / "input.csv"
        if isinstance(rows, list) and (not rows or isinstance(rows[0], dict)):
            fields = list(rows[0]) if rows else ["score", "language"]
            with source.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
        args = [sys.executable, str(ROOT / "scripts" / script), str(source)]
        if extra_json is not None:
            output = Path(temp) / "outputs.json"
            output.write_text(json.dumps(extra_json), encoding="utf-8")
            args.append(str(output))
        return subprocess.run([*args, *options], text=True, capture_output=True, cwd=ROOT, timeout=10)

def event(video, key, start, end):
    return {"video_id": video, "event_id": key, "start_ms": str(start), "end_ms": str(end)}

class TimestampTests(unittest.TestCase):
    def test_overlap_report_includes_nested_unsorted_ranges(self):
        rows = [event("v", "later", 10, 20), event("v", "outer", 0, 30), event("v", "inner", 5, 8)]
        result = cli("check_timestamps.py", rows)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Invalid timestamp ranges: 0", result.stdout)
        self.assertIn("Overlapping event pairs: 2", result.stdout)
        self.assertIn("outer", result.stdout)

    def test_touching_and_different_videos_are_not_overlaps(self):
        rows = [event("v", "one", 0, 10), event("v", "two", 10, 20), event("other", "three", 0, 20)]
        result = cli("check_timestamps.py", rows, options=["--strict"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Overlapping event pairs: 0", result.stdout)

    def test_short_csv_row_is_a_clear_data_error(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "events.csv"
            source.write_text("video_id,event_id,start_ms,end_ms\nv,one,0\n")
            result = subprocess.run([sys.executable, str(ROOT / "scripts/check_timestamps.py"), str(source)], text=True, capture_output=True, cwd=ROOT, timeout=10)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn("Traceback", result.stderr)
            self.assertIn("invalid timestamp data", result.stderr)

    def test_report_mode_remains_successful_but_strict_fails(self):
        for rows in [[event("v", "bad", 20, 10)], [event("v", "one", 0, 20), event("v", "two", 10, 30)]]:
            with self.subTest(rows=rows):
                report = cli("check_timestamps.py", rows)
                strict = cli("check_timestamps.py", rows, options=["--strict"])
                self.assertEqual(report.returncode, 0)
                self.assertEqual(strict.returncode, 1)
                self.assertEqual(report.stdout, strict.stdout)

if __name__ == "__main__":
    unittest.main()
