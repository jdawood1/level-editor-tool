import csv
import time
from pathlib import Path

LOG = Path(__file__).resolve().parent.parent / "build" / "telemetry.csv"
LOG.parent.mkdir(exist_ok=True)


def log_event(action: str, duration: float, meta: dict):
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    first = not LOG.exists()
    with open(LOG, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if first:
            w.writerow(["timestamp", "action", "duration_s", "meta"])
        w.writerow([ts, action, f"{duration:.6f}", repr(meta)])
