# File: Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    python -m spacy download en_core_web_sm && \
    playwright install chromium && \
    playwright install-deps

COPY . .
CMD ["python", "main.py"]