#!/bin/bash

echo "🔄 Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
python -m playwright install chromium
python -m spacy download en_core_web_sm

echo "🚀 Starting the scraper..."
python main.py scrape "https://books.toscrape.com" \
  --proxy-file proxies.txt \
  --checkpoint data/checkpoints/checkpoint.json \
  --format json

