import pandas as pd


def revenue_by_month(df):
    monthly = (
        df[df["order_year"].isin([2017, 2018])]
        .groupby(["order_year", "order_month"], as_index=False)["revenue"]
        .sum()
        .sort_values(["order_year", "order_month"])
    )
    monthly["period"] = (
        monthly["order_year"].astype(str)
        + "-"
        + monthly["order_month"].astype(str).str.zfill(2)
    )
    return monthly[["period", "revenue"]].to_dict(orient="records")


def top_categories(df, n=10):
    cats = (
        df.groupby("product_category_name_english", as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=False)
        .head(n)
        .rename(columns={"product_category_name_english": "category"})
    )
    # Ensure correct column names regardless of pandas version
    cats = cats[["category", "revenue"]]
    return cats.to_dict(orient="records")


def churn_by_state(df):
    # Deduplicate to one row per customer to get accurate churn rates.
    # is_churned is a customer-level flag but df has one row per order item,
    # so we must unique on customer before aggregating.
    customers = df[["customer_unique_id", "customer_state", "is_churned"]].drop_duplicates(
        subset="customer_unique_id"
    )
    churn = (
        customers.groupby("customer_state", as_index=False)["is_churned"]
        .mean()
    )
    churn["churn_rate"] = (churn["is_churned"] * 100).round(2)
    churn = (
        churn.rename(columns={"customer_state": "state"})[["state", "churn_rate"]]
        .sort_values("churn_rate", ascending=False)
        .head(15)
    )
    return churn.to_dict(orient="records")


def review_score_distribution(df):
    dist = (
        df["review_score"]
        .dropna()
        .value_counts()
        .sort_index()
        .reset_index()
    )
    # pandas ≥2.0 names the columns differently — normalise either way
    dist.columns = ["score", "count"]
    return dist.to_dict(orient="records")


def delivery_performance(df):
    on_time = int((df["delivery_delay_days"] <= 0).sum())
    late    = int((df["delivery_delay_days"] > 0).sum())
    return [
        {"status": "On Time / Early", "count": on_time},
        {"status": "Late",            "count": late},
    ]


def get_all_charts(df):
    return {
        "revenue_by_month":          revenue_by_month(df),
        "top_categories":            top_categories(df),
        "churn_by_state":            churn_by_state(df),
        "review_score_distribution": review_score_distribution(df),
        "delivery_performance":      delivery_performance(df),
    }