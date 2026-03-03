## Architecture Overview

- **Data layer**: raw CSVs in `data/raw` (`customers.csv`, `orders.csv`, `products.csv`).
- **ETL layer (Python + pandas)**:
  - `clean_data.py` cleans and standardizes the raw datasets.
  - `analyze.py` merges cleaned data and produces aggregated insights.
  - Outputs are stored in `data/processed` and treated as the source of truth for the app.
- **Backend layer (FastAPI)**:
  - `backend/main.py` exposes read‑only REST endpoints on top of the processed CSVs.
  - Each endpoint reads the relevant CSV on every request, so the API always reflects the latest ETL run.
- **Frontend layer (Vanilla JS + Chart.js)**:
  - `frontend/index.html`, `styles.css`, `script.js` render a single‑page dashboard.
  - The UI calls the FastAPI endpoints via `fetch` and visualizes them using Chart.js and HTML tables.

**Data flow**

1. `data/raw/*.csv` → `clean_data.py` → `data/processed/customers_clean.csv`, `orders_clean.csv`.
2. Cleaned files + `data/raw/products.csv` → `analyze.py` → analytics CSVs in `data/processed`:
   - `monthly_revenue.csv`
   - `top_customers.csv`
   - `category_performance.csv`
   - `regional_analysis.csv`
3. FastAPI reads these analytics CSVs and serves JSON.
4. The frontend fetches JSON and renders charts/tables in the browser.

## Tech Stack Used

- **Language**: Python 3.11 (compatible with 3.9+).
- **Data processing**:
  - `pandas` for cleaning, joins, and aggregations.
  - `numpy` for numeric operations and NaN handling.
- **Backend**:
  - `FastAPI` for the REST API.
  - `uvicorn` as the ASGI server.
  - CORS middleware so the browser (on a different port) can call the API.
- **Frontend**:
  - Plain HTML/CSS and JavaScript (no React, to keep setup simple).
  - `Chart.js` (via CDN) for the revenue trend and category charts.
  - Native `fetch` API for HTTP calls and DOM updates.
- **Testing**:
  - `pytest` for unit tests around the data‑cleaning functions in `clean_data.py`.

# Analytics Assignment Solution

## Setup

1. Create a virtual environment (Python 3.9+).
2. Install backend dependencies:

```bash
pip install -r backend/requirements.txt
```

## Data Pipeline

1. Ensure raw CSVs are present in `data/raw` (sample files are provided).
2. Run cleaning:

```bash
python clean_data.py
```

3. Run analysis:

```bash
python analyze.py
```

Cleaned and analytics CSVs will appear in `data/processed`.

## Backend API

Start the FastAPI server from the `backend` directory:

```bash
uvicorn main:app --reload
```

Endpoints:

- `GET /health`
- `GET /api/revenue`
- `GET /api/top-customers`
- `GET /api/categories`
- `GET /api/regions`

## Frontend

Serve the `frontend` folder with any static file server (or open `index.html` directly).

The dashboard expects the backend API to be running at `http://localhost:8000`.

## Tests

Pytest tests (optional bonus) can be added under `tests/` and run with:

```bash
pytest
```

