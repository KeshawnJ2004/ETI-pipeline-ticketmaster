# Ticketmaster API to PostgreSQL ETL Pipeline

A production-grade, containerized ETL (Extract, Transform, Load) pipeline built in Python. This pipeline queries live regional event data from the Ticketmaster Discovery REST API, enforces strict runtime schema validation using Pydantic, enriches metadata using Pandas, and performs an idempotent batch load into a containerized PostgreSQL database using SQLAlchemy.

---

## Pipeline Architecture




---

## Tech Stack & Tools

* **Language:** Python 3.11+
* **Ingestion:** `requests` (HTTP REST API Client)
* **Data Validation:** `pydantic` (BaseModel)
* **Transformation:** `pandas`
* **Database & ORM:** `postgresql`, `sqlalchemy`, `psycopg2-binary`
* **Infrastructure:** `docker`, `docker-compose`
* **Environment Security:** `python-dotenv`



## Engineering Highlights & Solved Challenges

1. **Defensive API Extraction:** Handles deeply nested JSON structures and missing keys (e.g., undisclosed `priceRanges` or `TBD` event times) using safe `.get()` fallbacks, preventing pipeline crashes (`KeyError` / `IndexError`).
2. **Network Fault Tolerance:** Implemented strict HTTP `timeout=5` limits on network requests to prevent open TCP sockets from hanging indefinitely during API latency or drops.
3. **Runtime Data Integrity:** Enforces schema validation using Pydantic's `BaseModel` before database persistence. Invalid or missing optional fields are safely cast to `None`/`NULL`.
4. **Audit Trailing & Metadata Enrichment:** Appends execution ISO-formatted timestamps (`ingested_at`) to facilitate downstream database auditing.
5. **Containerized Infrastructure:** Database service decoupled from the host system using Docker Compose networking for reproducible local execution.


## Quickstart & Setup Guide

### 1. Prerequisites
* Docker Desktop installed and running
* Python 3.11+

### 2. Environment Configuration
Clone the repository and create a `.env` file in the root folder:

```bash
TICKET_MASTER_API_KEY=your_ticketmaster_api_key
DB_USER=admin
DB_PASSWORD=password123
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ticketmaster_db

[ Ticketmaster API ] (requests + params + timeout=5)
▼
[ Defensive JSON Extraction ] (.get() fallbacks for nested keys)
▼
[ Pydantic Runtime Validation ] (Type safety & schema enforcement)
▼
[ Pandas Transformation ] (DataFrame flattening + ISO timestamps)
▼
[ PostgreSQL Storage ]  <---> [ Docker Container ]



Start the PostgreSQL container:
    docker compose up -d

Execute the pipeline:
    source venv/bin/activate
    pip install -r requirements.txt
    python extract_load.py


