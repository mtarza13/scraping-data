# scraping-data
# 🕷️ scraping_v2

Advanced web scraping project built in Python. It supports proxies, Docker-based execution, structured modules for scalability, and optional REST API access.

---

## 📁 Project Structure & Components

### `main.py`
- **Entry point** of the project.
- Loads settings, initializes core logic, and launches the scraping process.

---

### `core/`
- Contains the **core spiders and data extraction logic**.
- Includes modules for spiders, parsers, and pipelines.

#### Example:
- `spider.py`: Contains crawling logic.
- `parser.py`: Handles HTML parsing and data extraction.
- `pipeline.py`: Manages post-processing or storage of scraped data.

---

### `utils/`
- Collection of **helper functions** used across the project.

#### Examples:
- `proxy_manager.py`: Loads and rotates proxies.
- `email_extractor.py`: Extracts emails from HTML/text.
- `logging_util.py`: Custom logger configuration.

---

### `config/`
- Configurable files in JSON or YAML format.
- Includes:
  - Request headers
  - Pagination and scraping depth
  - Domain restrictions

---

### `data/`
- Stores all **scraped output results**.
- Formats supported: `.json`, `.csv`, `.xlsx`, etc.

---

### `api/` *(optional)*
- REST API layer using **Flask** or **FastAPI**.
- Allows remote control: submit URLs, trigger scraping jobs, or view results.

---

### `tests/`
- **Unit tests** and integration tests for reliability.

---

### `proxies.txt`
- List of proxy IPs used to rotate traffic and avoid bans.

---

### `run_scraper.sh`
- Simple shell script to run the main scraper or launch Docker.

---

### `requirements.txt`
- All dependencies listed here:
  - `scrapy`
  - `requests`
  - `beautifulsoup4`
  - `fake_useragent`
  - `lxml`, etc.

---

### `Dockerfile` and `docker-compose.yml`
- Enables full containerization of the scraper.
- Useful for portable and isolated deployments.

---

## 🚀 Getting Started

```bash
# 1. Clone the repository
git clone https://github.com/mtarza13/scraping-data

# 2. Navigate into the directory
cd scraping_v2

# 3. Set up a virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the scraper
python main.py

