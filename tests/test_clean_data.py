import pandas as pd

from clean_data import clean_customers, clean_orders, parse_order_date


def test_clean_customers_deduplicates_and_email():
  df = pd.DataFrame(
      {
          "customer_id": [1, 1],
          "name": [" Alice ", "Alice"],
          "email": ["ALICE@EXAMPLE.COM", "alice@example.com"],
          "region": ["North", "North"],
          "signup_date": ["2023-01-01", "2023-02-01"],
      }
  )
  cleaned, report = clean_customers(df)
  assert len(cleaned) == 1
  row = cleaned.iloc[0]
  assert row["email"] == "alice@example.com"
  assert bool(row["is_valid_email"]) is True
  assert report["duplicates_removed"] == 1


def test_parse_order_date_multiple_formats():
  dates = ["2023-01-01", "01/02/2023", "03-15-2023"]
  parsed = [parse_order_date(d) for d in dates]
  assert all(pd.notna(parsed))


def test_clean_orders_fill_amount_by_product():
  df = pd.DataFrame(
      {
          "order_id": [1, 2, 3],
          "customer_id": [1, 1, 1],
          "product": ["A", "A", "A"],
          "amount": [10.0, None, 30.0],
          "order_date": ["2023-01-01", "2023-01-02", "2023-01-03"],
          "status": ["done", "pending", "completed"],
      }
  )
  cleaned, _ = clean_orders(df)
  assert cleaned["amount"].isna().sum() == 0
  assert set(cleaned["status"].unique()) <= {
      "completed",
      "pending",
      "cancelled",
      "refunded",
  }

