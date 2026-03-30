import pandas as pd
import json


def revenue_by_month(df):
    """Monthly revenue trend."""
    monthly = (
        df[df["order_year"].isin([2017, 2018])]
        .groupby(["order_year", "order_month"])["revenue"]
        .sum()
        .reset_index()
    )
    monthly["period"] = monthly["order_year"].astype(str) + "-" + monthly["order_month"].astype(str).str.zfill(2)
    monthly = monthly.sort_values("period")
    return monthly[["period", "revenue"]].to_dict(orient="records")


def top_categories(df, n=10):
    """Top N product categories by revenue."""
    cats = (
        df.groupby("product_category_name_english")["revenue"]
        .sum()
        .nlargest(n)
        .reset_index()
    )
    cats.columns = ["category", "revenue"]
    return cats.to_dict(orient="records")


def churn_by_state(df):
    """Churn rate by customer state."""
    state_churn = (
        df.groupby("customer_state")["is_churned"]
        .mean()
        .mul(100)
        .round(2)
        .reset_index()
    )
    state_churn.columns = ["state", "churn_rate"]
    state_churn = state_churn.sort_values("churn_rate", ascending=False).head(15)
    return state_churn.to_dict(orient="records")


def review_score_distribution(df):
    """Distribution of review scores."""
    dist = (
        df["review_score"]
        .value_counts()
        .sort_index()
        .reset_index()
    )
    dist.columns = ["score", "count"]
    return dist.to_dict(orient="records")


def delivery_performance(df):
    """On time vs late delivery breakdown."""
    on_time = int((df["delivery_delay_days"] <= 0).sum())
    late    = int((df["delivery_delay_days"] > 0).sum())
    return [
        {"status": "On Time / Early", "count": on_time},
        {"status": "Late", "count": late}
    ]


def get_all_charts(df):
    return {
        "revenue_by_month":        revenue_by_month(df),
        "top_categories":          top_categories(df),
        "churn_by_state":          churn_by_state(df),
        "review_score_distribution": review_score_distribution(df),
        "delivery_performance":    delivery_performance(df),
    }
