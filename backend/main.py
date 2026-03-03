from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"


app = FastAPI(title="Analytics Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def read_csv_or_404(filename: str):
    path = DATA_DIR / filename
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Data not found")
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=404, detail="Data file is empty")
    return df.to_dict(orient="records")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/revenue")
def get_revenue():
    return read_csv_or_404("monthly_revenue.csv")


@app.get("/api/top-customers")
def get_top_customers():
    return read_csv_or_404("top_customers.csv")


@app.get("/api/categories")
def get_categories():
    return read_csv_or_404("category_performance.csv")


@app.get("/api/regions")
def get_regions():
    return read_csv_or_404("regional_analysis.csv")

