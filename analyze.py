import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def load_csv(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        raise
    except pd.errors.EmptyDataError:
        raise


def run_analysis(processed_dir: Path, raw_dir: Path) -> None:
    customers_path = processed_dir / "customers_clean.csv"
    orders_path = processed_dir / "orders_clean.csv"
    products_path = raw_dir / "products.csv"

    customers = load_csv(customers_path)
    orders = load_csv(orders_path)
    products = load_csv(products_path)

    orders_with_customers = orders.merge(
        customers, on="customer_id", how="left", suffixes=("", "_customer")
    )

    full_data = orders_with_customers.merge(
        products,
        left_on="product",
        right_on="product_name",
        how="left",
        suffixes=("", "_product"),
    )

    missing_customer = orders_with_customers["name"].isna().sum()
    missing_product = full_data["product_id"].isna().sum()

    print(f"Orders without matching customer: {missing_customer}")
    print(f"Orders without matching product: {missing_product}")

    completed = full_data[full_data["status"] == "completed"].copy()

    monthly_revenue = (
        completed.groupby("order_year_month")["amount"].sum().reset_index()
    )
    monthly_revenue = monthly_revenue.sort_values("order_year_month")
    monthly_revenue.rename(columns={"amount": "total_revenue"}, inplace=True)
    monthly_revenue.to_csv(processed_dir / "monthly_revenue.csv", index=False)

    top_customers = (
        completed.groupby(["customer_id", "name", "region"])["amount"]
        .sum()
        .reset_index()
    )
    top_customers.rename(columns={"amount": "total_spend"}, inplace=True)
    top_customers = top_customers.sort_values("total_spend", ascending=False).head(10)

    if not completed["order_date"].isna().all():
        completed["order_date"] = pd.to_datetime(completed["order_date"], errors="coerce")
        latest_date = completed["order_date"].max()
        window_start = latest_date - pd.Timedelta(days=90)

        recent_orders = completed[
            (completed["order_date"] >= window_start)
            & (completed["order_date"] <= latest_date)
        ]
        active_customers = set(recent_orders["customer_id"].dropna().unique().tolist())
        top_customers["churned"] = ~top_customers["customer_id"].isin(active_customers)
    else:
        top_customers["churned"] = True

    top_customers.to_csv(processed_dir / "top_customers.csv", index=False)

    category_perf = (
        completed.groupby("category")
        .agg(
            total_revenue=("amount", "sum"),
            average_order_value=("amount", "mean"),
            num_orders=("order_id", "count"),
        )
        .reset_index()
    )
    category_perf.to_csv(processed_dir / "category_performance.csv", index=False)

    full_data["amount"] = pd.to_numeric(full_data["amount"], errors="coerce").fillna(0)
    customers_per_region = customers.groupby("region")["customer_id"].nunique()
    orders_per_region = full_data.groupby("region")["order_id"].nunique()
    revenue_per_region = full_data[full_data["status"] == "completed"].groupby("region")[
        "amount"
    ].sum()

    regional = (
        pd.DataFrame(
            {
                "num_customers": customers_per_region,
                "num_orders": orders_per_region,
                "total_revenue": revenue_per_region,
            }
        )
        .fillna(0)
        .reset_index()
    )

    regional["avg_revenue_per_customer"] = regional.apply(
        lambda row: row["total_revenue"] / row["num_customers"]
        if row["num_customers"] > 0
        else 0,
        axis=1,
    )

    regional.rename(columns={"region": "region"}, inplace=True)
    regional.to_csv(processed_dir / "regional_analysis.csv", index=False)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run analysis on cleaned data.")
    parser.add_argument(
        "--processed-dir",
        type=str,
        default=str(Path(__file__).parent / "data" / "processed"),
        help="Directory containing cleaned CSVs.",
    )
    parser.add_argument(
        "--raw-dir",
        type=str,
        default=str(Path(__file__).parent / "data" / "raw"),
        help="Directory containing raw CSVs (for products).",
    )
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    processed_dir = Path(args.processed_dir)
    raw_dir = Path(args.raw_dir)

    run_analysis(processed_dir=processed_dir, raw_dir=raw_dir)


if __name__ == "__main__":
    main()

