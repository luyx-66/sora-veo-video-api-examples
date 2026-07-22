"""Submit and poll a resumable JSONL batch of asynchronous video jobs."""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.request
from decimal import Decimal
from pathlib import Path


TERMINAL = {"completed", "succeeded", "success", "failed", "error"}


def load_jobs(path: Path) -> list[dict]:
    jobs = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    required = {"id", "model", "prompt", "duration"}
    for job in jobs:
        missing = required - job.keys()
        if missing:
            raise ValueError(f"Job {job.get('id', '<unknown>')} missing: {', '.join(sorted(missing))}")
    if len({job["id"] for job in jobs}) != len(jobs):
        raise ValueError("Job IDs must be unique")
    return jobs


def estimated_cost(jobs: list[dict], price_per_second: Decimal) -> Decimal:
    return sum((Decimal(str(job["duration"])) * price_per_second for job in jobs), Decimal("0"))


def request_json(url: str, api_key: str, payload: dict | None = None) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8") if payload is not None else None,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST" if payload is not None else "GET",
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def identifier(response: dict) -> str:
    value = response.get("task_id") or response.get("id") or response.get("data", {}).get("task_id")
    if not value:
        raise ValueError("Submission response did not contain a task ID")
    return str(value)


def status_of(response: dict) -> str:
    return str(response.get("status") or response.get("data", {}).get("status", "unknown")).lower()


def completed_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {row["id"] for row in (json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()) if row.get("status") in TERMINAL}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a resumable Sora/Veo video API batch.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--base-url", default=os.getenv("AI_API_BASE_URL", "https://api.apimart.ai/v1"))
    parser.add_argument("--estimated-price-per-second", type=Decimal, required=True)
    parser.add_argument("--max-cost", type=Decimal, required=True)
    parser.add_argument("--poll-seconds", type=float, default=5)
    parser.add_argument("--output", type=Path, default=Path("video-results.jsonl"))
    args = parser.parse_args()
    api_key = os.getenv("APIMART_API_KEY")
    if not api_key:
        parser.error("Set APIMART_API_KEY in the environment")

    jobs = [job for job in load_jobs(args.input) if job["id"] not in completed_ids(args.output)]
    estimate = estimated_cost(jobs, args.estimated_price_per_second)
    if estimate > args.max_cost:
        parser.error(f"Estimated cost ${estimate} exceeds --max-cost ${args.max_cost}")

    base_url = args.base_url.rstrip("/")
    with args.output.open("a", encoding="utf-8") as report:
        for job in jobs:
            payload = {key: value for key, value in job.items() if key != "id"}
            task = identifier(request_json(f"{base_url}/videos/generations", api_key, payload))
            while True:
                result = request_json(f"{base_url}/tasks/{task}", api_key)
                status = status_of(result)
                if status in TERMINAL:
                    row = {"id": job["id"], "task_id": task, "status": status, "response": result}
                    report.write(json.dumps(row) + "\n")
                    report.flush()
                    print(json.dumps({"id": job["id"], "task_id": task, "status": status}))
                    break
                time.sleep(args.poll_seconds)


if __name__ == "__main__":
    main()
