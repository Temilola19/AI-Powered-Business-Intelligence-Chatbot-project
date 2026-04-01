import os
import json
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def format_history(history):
    """Convert session history into LLM-friendly format"""
    return [
        {"role": msg["role"], "content": msg["content"]}
        for msg in history
        if msg["role"] in ["user", "assistant"]
    ]


def ask(question, stats, history):
    messages = [
        {
            "role": "system",
            "content": f"""You are an expert business intelligence analyst for an e-commerce dataset (Olist, a Brazilian marketplace).

You have access to the following metrics — always use these exact numbers in your answers:

## Summary KPIs
- Total orders: {stats['total_orders']:,}
- Total revenue: R$ {stats['total_revenue']:,.2f}
- Average order value: R$ {stats['avg_order_value']:,.2f}
- Average review score: {stats['avg_review_score']:.2f} / 5
- Overall churn rate: {stats['churn_rate_pct']:.2f}%

## Top 10 Product Categories by Revenue
{json.dumps(stats.get('top_categories', []), indent=2)}

## Top 15 States by Churn Rate (% of one-time buyers)
{json.dumps(stats.get('churn_by_state', []), indent=2)}

Rules:
- Always use real numbers from the data above — never say data is unavailable.
- Be concise but insightful; give business interpretation, not just raw figures.
- When asked about categories or churn by state, reference the lists above directly."""
        }
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": question})

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.3,
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"