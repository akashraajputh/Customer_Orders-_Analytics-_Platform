import argparse
import logging
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def load_csv(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except FileNotFoundError as exc:
        logger.error("File not found: %s", path)
        raise
    except pd.errors.EmptyDataError as exc:
        logger.error("CSV is empty: %s", path)
        raise


def clean_customers(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    report = {}

    report["rows_before"] = len(df)
    report["nulls_before"] = df.isna().sum().to_dict()

    for col in ["name", "region"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    if "region" in df.columns:
        df["region"] = df["region"].replace({"nan": np.nan})
        df["region"] = df["region"].fillna("Unknown")

    if "email" in df.columns:
        df["email"] = df["email"].astype(str).str.strip().str.lower()
        is_valid = df["email"].str.contains("@") & df["email"].str.contains(".")
        is_valid &= df["email"].ne("") & df["email"].ne("nan")
        df["is_valid_email"] = is_valid
    else:
        df["is_valid_email"] = False

    if "signup_date" in df.columns:
        df["signup_date_parsed"] = pd.to_datetime(
            df["signup_date"], errors="coerce", format=None
        )
        bad_dates = df["signup_date"].notna() & df["signup_date_parsed"].isna()
        if bad_dates.any():
            logger.warning(
                "Unparseable signup_date values encountered: %d rows",
                int(bad_dates.sum()),
            )
        df["signup_date"] = df["signup_date_parsed"].dt.date.astype("datetime64[ns]")
        df = df.drop(columns=["signup_date_parsed"])

    if "customer_id" in df.columns:
        if "signup_date" in df.columns:
            df = df.sort_values("signup_date")
        df = df.drop_duplicates(subset=["customer_id"], keep="last")

    report["rows_after"] = len(df)
    report["nulls_after"] = df.isna().sum().to_dict()
    report["duplicates_removed"] = report["rows_before"] - report["rows_after"]

    return df, report


def parse_order_date(value: str):
    if pd.isna(value):
        return pd.NaT
    value = str(value).strip()
    if not value:
        return pd.NaT
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y"):
        try:
            return pd.to_datetime(value, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.NaT


def clean_orders(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    report = {}
    report["rows_before"] = len(df)
    report["nulls_before"] = df.isna().sum().to_dict()

    df["order_date"] = df["order_date"].apply(parse_order_date)

    if {"customer_id", "order_id"}.issubset(df.columns):
        mask_unrecoverable = df["customer_id"].isna() & df["order_id"].isna()
        df = df.loc[~mask_unrecoverable].copy()

    if "amount" in df.columns:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        grouped_median = df.groupby("product")["amount"].transform("median")
        global_median = df["amount"].median()
        df["amount"] = df["amount"].fillna(grouped_median)
        df["amount"] = df["amount"].fillna(global_median)

    status_map = {
        "done": "completed",
        "complete": "completed",
        "completed": "completed",
        "pending": "pending",
        "in_progress": "pending",
        "in progress": "pending",
        "cancelled": "cancelled",
        "canceled": "cancelled",
        "refunded": "refunded",
        "refund": "refunded",
    }
    if "status" in df.columns:
        df["status"] = (
            df["status"]
            .astype(str)
            .str.strip()
            .str.lower()
            .map(status_map)
            .fillna("pending")
        )

    if "order_date" in df.columns:
        df["order_year_month"] = df["order_date"].dt.strftime("%Y-%m")

    report["rows_after"] = len(df)
    report["nulls_after"] = df.isna().sum().to_dict()

    return df, report


def print_report(title: str, report: dict) -> None:
    logger.info("=== %s Cleaning Report ===", title)
    logger.info("Rows before: %s, after: %s", report["rows_before"], report["rows_after"])
    logger.info("Duplicates removed: %s", report.get("duplicates_removed", 0))
    logger.info("Nulls before: %s", report["nulls_before"])
    logger.info("Nulls after: %s", report["nulls_after"])


def run_cleaning(raw_dir: Path, processed_dir: Path) -> None:
    processed_dir.mkdir(parents=True, exist_ok=True)

    customers_path = raw_dir / "customers.csv"
    orders_path = raw_dir / "orders.csv"

    customers_df = load_csv(customers_path)
    customers_clean, customers_report = clean_customers(customers_df)
    customers_clean.to_csv(processed_dir / "customers_clean.csv", index=False)
    print_report("Customers", customers_report)

    orders_df = load_csv(orders_path)
    orders_clean, orders_report = clean_orders(orders_df)
    orders_clean.to_csv(processed_dir / "orders_clean.csv", index=False)
    print_report("Orders", orders_report)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Clean raw CSV data.")
    parser.add_argument(
        "--raw-dir",
        type=str,
        default=str(Path(__file__).parent / "data" / "raw"),
        help="Directory containing raw CSV files.",
    )
    parser.add_argument(
        "--processed-dir",
        type=str,
        default=str(Path(__file__).parent / "data" / "processed"),
        help="Directory to save cleaned CSV files.",
    )
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir)
    processed_dir = Path(args.processed_dir)

    run_cleaning(raw_dir=raw_dir, processed_dir=processed_dir)


if __name__ == "__main__":
    main()

