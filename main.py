# File: main.py
import argparse
import asyncio
import json
import yaml
from pathlib import Path
from core.scraper import AdvancedScraper, ScrapeConfig
from core.storage import DataExporter


def load_config(config_path: str = "config/config.yaml") -> ScrapeConfig:
    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)
    return ScrapeConfig(**raw)


def parse_args():
    parser = argparse.ArgumentParser(description="Advanced Web Scraper")
    parser.add_argument("url", help="Target URL to scrape")
    parser.add_argument("--config", default="config/config.yaml", help="Path to YAML config file")
    parser.add_argument("--proxy-file", help="Path to proxy list file", default=None)
    parser.add_argument("--checkpoint", help="Path to checkpoint file", default="data/checkpoints/default.json")
    parser.add_argument("--format", choices=["json", "csv"], default="json", help="Export format")
    return parser.parse_args()


async def main():
    args = parse_args()
    config = load_config(args.config)

    scraper = AdvancedScraper(
        config=config,
        headless=True,
        proxy_file=args.proxy_file
    )

    results = await scraper.run(args.url, args.checkpoint)

    exporter = DataExporter(format=args.format)
    export_path = "data/exports/results." + args.format
    exporter.export(results, export_path)

    print("Scraping completed successfully")


if __name__ == "__main__":
    asyncio.run(main())

