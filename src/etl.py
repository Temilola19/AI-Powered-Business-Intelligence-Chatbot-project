import pandas as pd

DATA_PATH = "data/raw"


def load_and_merge():
    print("Loading datasets...")

    orders         = pd.read_csv(f"{DATA_PATH}/olist_orders_dataset.csv")
    order_items    = pd.read_csv(f"{DATA_PATH}/olist_order_items_dataset.csv")
    order_payments = pd.read_csv(f"{DATA_PATH}/olist_order_payments_dataset.csv")
    order_reviews  = pd.read_csv(f"{DATA_PATH}/olist_order_reviews_dataset.csv")
    customers      = pd.read_csv(f"{DATA_PATH}/olist_customers_dataset.csv")
    products       = pd.read_csv(f"{DATA_PATH}/olist_products_dataset.csv")
    translation    = pd.read_csv(f"{DATA_PATH}/product_category_name_translation.csv")

    print("Merging...")

    df = orders.merge(customers, on="customer_id", how="left")
    df = df.merge(order_items, on="order_id", how="left")

    payments = order_payments.groupby("order_id")["payment_value"].sum().reset_index()
    payments.columns = ["order_id", "total_payment"]
    df = df.merge(payments, on="order_id", how="left")

    reviews = order_reviews.groupby("order_id")["review_score"].mean().reset_index()
    df = df.merge(reviews, on="order_id", how="left")

    products = products.merge(translation, on="product_category_name", how="left")
    df = df.merge(
        products[["product_id", "product_category_name_english"]],
        on="product_id",
        how="left"
    )

    print("Cleaning...")

    df["order_purchase_timestamp"]      = pd.to_datetime(df["order_purchase_timestamp"])
    df["order_delivered_customer_date"] = pd.to_datetime(df["order_delivered_customer_date"])
    df["order_estimated_delivery_date"] = pd.to_datetime(df["order_estimated_delivery_date"])

    df["delivery_delay_days"] = (
        df["order_delivered_customer_date"] - df["order_estimated_delivery_date"]
    ).dt.days

    df["order_year"]  = df["order_purchase_timestamp"].dt.year
    df["order_month"] = df["order_purchase_timestamp"].dt.month
    df["revenue"]     = df["price"] + df["freight_value"]

    df["product_category_name_english"] = df["product_category_name_english"].fillna("Unknown")
    df["customer_state"]                = df["customer_state"].fillna("Unknown")
    df = df.dropna(subset=["total_payment"])

    purchase_counts = df.groupby("customer_unique_id")["order_id"].nunique().reset_index()
    purchase_counts.columns = ["customer_unique_id", "total_orders"]
    df = df.merge(purchase_counts, on="customer_unique_id", how="left")
    df["is_churned"] = (df["total_orders"] == 1).astype(int)

    print("Done:", df.shape)
    return df


def get_summary_stats(df):
    # --- Basic KPIs ---
    stats = {
        "total_orders":     int(df["order_id"].nunique()),
        "total_revenue":    float(df["revenue"].sum()),
        "avg_order_value":  float(df["total_payment"].mean()),
        "avg_review_score": float(df["review_score"].mean()),
        "churn_rate_pct":   float(df["is_churned"].mean() * 100),
    }

    # --- Top 10 product categories by revenue ---
    top_cats = (
        df.groupby("product_category_name_english", as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=False)
        .head(10)
        .rename(columns={"product_category_name_english": "category"})
    )
    stats["top_categories"] = top_cats[["category", "revenue"]].to_dict(orient="records")

    # --- Churn rate by state (deduplicated to customer level) ---
    customers = df[["customer_unique_id", "customer_state", "is_churned"]].drop_duplicates(
        subset="customer_unique_id"
    )
    churn_by_state = (
        customers.groupby("customer_state", as_index=False)["is_churned"]
        .mean()
    )
    churn_by_state["churn_rate_pct"] = (churn_by_state["is_churned"] * 100).round(2)
    churn_by_state = (
        churn_by_state.rename(columns={"customer_state": "state"})[["state", "churn_rate_pct"]]
        .sort_values("churn_rate_pct", ascending=False)
        .head(15)
    )
    stats["churn_by_state"] = churn_by_state.to_dict(orient="records")

    return stats