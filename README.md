# Analytics Assignment Solution

End-to-end data pipeline and fullstack dashboard: raw CSV ingestion → cleaning → analysis → REST API → interactive web UI.

---

## Deliverables (Submission Checklist)

| File / Folder       | Contents |
|---------------------|----------|
| `clean_data.py`     | Part 1 — data cleaning script |
| `analyze.py`        | Part 2 — merging and analysis script |
| `backend/`          | FastAPI app + `requirements.txt` |
| `frontend/`         | HTML/CSS/JS dashboard files |
| `data/raw/`         | Original CSVs (customers, orders, products) |
| `data/processed/`   | All output CSVs from cleaning and analysis |
| `README.md`         | This file — setup, run instructions, assumptions |
| `tests/`            | Pytest tests for data-cleaning (bonus) |
| `backend/Dockerfile` + `docker-compose.yml` | Docker backend with bind-mount (bonus) |

---

## Assumptions

- Raw CSVs use the exact column names specified: `customer_id`, `name`, `email`, `region`, `signup_date` (customers); `order_id`, `customer_id`, `product`, `amount`, `order_date`, `status` (orders); `product_id`, `product_name`, `category`, `unit_price` (products).
- Dates in `signup_date` and `order_date` are parsed with the three formats implemented (YYYY-MM-DD, DD/MM/YYYY, MM-DD-YYYY); any other format becomes NaT and is logged.
- “Churned” is defined as no completed order in the 90 days before the latest order date in the dataset.
- Regional analysis uses the customer’s `region`; orders without a matching customer are excluded from per-region customer counts but can still contribute to order/revenue counts if region is propagated or handled in the merge.
- No database is used; all outputs are CSV. The backend reads from `data/processed` on each request.

---

## Architecture Overview

- **Data layer**: Raw CSVs in `data/raw` (`customers.csv`, `orders.csv`, `products.csv`).
- **ETL (Python + pandas)**:
  - `clean_data.py` cleans and standardizes raw data; writes `customers_clean.csv`, `orders_clean.csv` to `data/processed`.
  - `analyze.py` merges cleaned data with products, runs analytics; writes `monthly_revenue.csv`, `top_customers.csv`, `category_performance.csv`, `regional_analysis.csv` to `data/processed`.
- **Backend (FastAPI)**: `backend/main.py` serves read-only REST endpoints that read the above CSVs and return JSON. CORS enabled for the frontend.
- **Frontend (Vanilla JS + Chart.js)**: Single-page dashboard that fetches the API and renders revenue trend, top customers, category breakdown, and region summary. Responsive for 1280px desktop and 375px mobile.

**Data flow:** `data/raw` → `clean_data.py` → `data/processed` (cleaned) → `analyze.py` → `data/processed` (analytics) → FastAPI → frontend.

---

## Tech Stack

- **Language**: Python 3.11 (3.9+).
- **Data**: pandas, numpy.
- **Backend**: FastAPI, uvicorn.
- **Frontend**: HTML, CSS, JavaScript, Chart.js (CDN).
- **Testing**: pytest.
- **Bonus**: Docker (Dockerfile + docker-compose, bind-mount for `data/processed`).

---

## Setup

1. Create and activate a virtual environment (Python 3.9+):

```bash
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r backend/requirements.txt pytest
```

---

## How to Run

### 1. Data pipeline (run from project root)

```bash
python clean_data.py
python analyze.py
```

Cleaned and analytics CSVs will appear in `data/processed`.

### 2. Backend API

From project root:

```bash
cd backend
..\.venv\Scripts\python -m uvicorn main:app --reload
```

Or with system `uvicorn` after `pip install`:

```bash
cd backend
uvicorn main:app --reload
```

- Base URL: `http://localhost:8000`
- Health: `GET /health` → `{"status":"ok"}`
- Data: `GET /api/revenue`, `/api/top-customers`, `/api/categories`, `/api/regions` (each reads from the corresponding CSV in `data/processed`; returns 404 if file is missing or empty).

### 3. Frontend

Serve the frontend over HTTP (required for API calls):

```bash
cd frontend
python -m http.server 5500
```

Open in browser: `http://localhost:5500/index.html`. The dashboard expects the backend at `http://localhost:8000`.

### 4. Docker (bonus)

From project root, after running the pipeline so `data/processed` exists:

```bash
docker-compose up --build
```

Backend runs at `http://localhost:8000` with `data/processed` bind-mounted read-only.

### 5. Tests

```bash
pytest
```

Runs tests in `tests/` (e.g. cleaning deduplication, date parsing, status normalization).

---

## Bonus Features Implemented

- Date-range filter on the Revenue Trend chart.
- Search box on the Top Customers table.
- Docker: `backend/Dockerfile` and root `docker-compose.yml` with bind-mount for `data/processed`.
- At least 3 pytest unit tests for data-cleaning functions.
