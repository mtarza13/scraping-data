# File: core/storage.py
import json
import csv
from pathlib import Path
from typing import List
from core.scraper import ScrapeResult


class DataExporter:
    def __init__(self, format: str = "json"):
        self.format = format

    def export(self, results: List[ScrapeResult], path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        if self.format == "json":
            with open(path, "w", encoding="utf-8") as f:
                json.dump([r.dict() for r in results], f, ensure_ascii=False, indent=2)

        elif self.format == "csv":
            if not results:
                return
            keys = set()
            for r in results:
                keys.update(r.data.keys())
            keys = list(keys)

            with open(path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                header = ["url", "status", "timestamp"] + keys
                writer.writerow(header)
                for r in results:
                    row = [r.url, r.status, r.timestamp]
                    for key in keys:
                        row.append(", ".join(r.data.get(key, [])))
                    writer.writerow(row)

