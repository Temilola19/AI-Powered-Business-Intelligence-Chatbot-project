import pandas as pd
import numpy as np
import os

DATA_PATH = "data/raw"

def load_and_merge():
    """Load all Olist CSVs and merge into one master dataframe."""

    print("Loading datasets...")
    orders         = pd.read_csv(f"{DATA_PATH}/olist_orders_dataset.csv")
    order_items    = pd.read_csv(f"{DATA_PATH}/olist_order_items_dataset.csv")
    order_payments = pd.read_csv(f"{DATA_PATH}/olist_order_payments_dataset.csv")
    order_reviews  = pd.read_csv(f"{DATA_PATH}/olist_order_reviews_dataset.csv")
    customers      = pd.read_csv(f"{DATA_PATH}/olist_customers_dataset.csv")
    products       = pd.read_csv(f"{DATA_PATH}/olist_products_dataset.csv")
    sellers        = pd.read_csv(f"{DATA_PATH}/olist_sellers_dataset.csv")
    translation    = pd.read_csv(f"{DATA_PATH}/product_category_name_translation.csv")

    print("Merging datasets...")

    df = orders.merge(customers, on="customer_id", how="left")
    df = df.merge(order_items, on="order_id", how="left")

    payments_agg = order_payments.groupby("order_id").agg(
        total_payment=("payment_value", "sum"),
        payment_installments=("payment_installments", "max"),
        payment_type=("payment_type", "first")
    ).reset_index()
    df = df.merge(payments_agg, on="order_id", how="left")

    reviews_agg = order_reviews.sort_values("review_creation_date").groupby("order_id").last().reset_index()
    df = df.merge(reviews_agg[["order_id", "review_score"]], on="order_id", how="left")

    products = products.merge(translation, on="product_category_name", how="left")
    df = df.merge(products[["product_id", "product_category_name_english", "product_weight_g"]], on="product_id", how="left")
    df = df.merge(sellers[["seller_id", "seller_state"]], on="seller_id", how="left")

    print("Cleaning data...")
    df = clean(df)

    print(f"ETL complete. Shape: {df.shape}")
    return df


def clean(df):
    """Clean and engineer features."""

    date_cols = ["order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date"]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    df["delivery_delay_days"] = (
        df["order_delivered_customer_date"] - df["order_estimated_delivery_date"]
    ).dt.days

    df["order_year"]    = df["order_purchase_timestamp"].dt.year
    df["order_month"]   = df["order_purchase_timestamp"].dt.month
    df["order_quarter"] = df["order_purchase_timestamp"].dt.quarter
    df["revenue"]       = df["price"] + df["freight_value"]

    df["product_category_name_english"] = df["product_category_name_english"].fillna("unknown")
    df = df.dropna(subset=["total_payment"])

    purchase_counts = df.groupby("customer_unique_id")["order_id"].nunique().reset_index()
    purchase_counts.columns = ["customer_unique_id", "total_orders"]
    df = df.merge(purchase_counts, on="customer_unique_id", how="left")
    df["is_churned"] = (df["total_orders"] == 1).astype(int)

    return df


def get_summary_stats(df):
    """Return key business metrics — all native Python types for JSON serialization."""

    def to_str_dict(series):
        return {str(k): round(float(v), 2) for k, v in series.items()}

    stats = {
        "total_orders":           int(df["order_id"].nunique()),
        "total_revenue":          round(float(df["revenue"].sum()), 2),
        "avg_order_value":        round(float(df["total_payment"].mean()), 2),
        "avg_review_score":       round(float(df["review_score"].mean()), 2),
        "churn_rate_pct":         round(float(df["is_churned"].mean() * 100), 2),
        "avg_delivery_delay_days":round(float(df["delivery_delay_days"].mean()), 2),
        "late_delivery_pct":      round(float((df["delivery_delay_days"] > 0).mean() * 100), 2),
        "top_categories":  to_str_dict(df.groupby("product_category_name_english")["revenue"].sum().nlargest(5)),
        "revenue_by_state":to_str_dict(df.groupby("customer_state")["revenue"].sum().nlargest(10)),
        "orders_by_year":  to_str_dict(df.groupby("order_year")["order_id"].nunique()),
        "revenue_by_year": to_str_dict(df.groupby("order_year")["revenue"].sum()),
    }

    return stats


if __name__ == "__main__":
    df = load_and_merge()
    print(get_summary_stats(df))
