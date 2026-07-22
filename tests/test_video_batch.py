import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from video_batch import estimated_cost, identifier, load_jobs, status_of


class VideoBatchTests(unittest.TestCase):
    def test_cost(self):
        jobs = [{"duration": 5}, {"duration": 10}]
        self.assertEqual(estimated_cost(jobs, Decimal("0.08")), Decimal("1.20"))

    def test_response_helpers(self):
        self.assertEqual(identifier({"data": {"task_id": "task-1"}}), "task-1")
        self.assertEqual(status_of({"data": {"status": "Completed"}}), "completed")

    def test_load_jobs(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "jobs.jsonl"
            path.write_text('{"id":"a","model":"sora","prompt":"waves","duration":5}\n', encoding="utf-8")
            self.assertEqual(load_jobs(path)[0]["model"], "sora")


if __name__ == "__main__":
    unittest.main()
