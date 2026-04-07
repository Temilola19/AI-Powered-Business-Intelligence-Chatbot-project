# Olist E-Commerce BI Dashboard

An AI-powered business intelligence dashboard built on the [Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce). Visualizes key metrics across revenue, churn, delivery, and reviews with a conversational AI analyst you can ask questions in plain English.

<img width="1788" height="1002" alt="Screenshot 2026-04-01 at 10 42 40 PM" src="https://github.com/user-attachments/assets/5285841e-10c9-4c05-86ce-2fbeb3de2f72" />


---

## Features

- **5 interactive charts** — revenue trends, top categories, churn by state, review distribution, delivery performance
- **KPI summary bar** — total orders, revenue, avg order value, churn rate, avg review score
- **AI chat analyst** — ask questions about the data in plain English, powered by Groq (Llama 3)
- **Conversation memory** — the chatbot remembers the last 5 exchanges per session

---

## Project Structure

```
your-project/
├── app.py                  # Flask app + routes
├── .env                    # API keys
├── requirements.txt
├── templates/
│   └── index.html          # Frontend dashboard
├── src/
│   ├── __init__.py
│   ├── etl.py              # Data loading & merging
│   ├── analysis.py         # Chart calculations
│   └── chatbot.py          # Groq AI chat logic
└── data/
    └── raw/                # Olist CSV files go here
```

---

## Quickstart

### 1. Clone the repo

```bash
git clone https://github.com/your-username/olist-bi-dashboard.git
cd olist-bi-dashboard
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Download the dataset

Download the Olist dataset from [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) and place all CSV files in `data/raw/`:

```
data/raw/
├── olist_orders_dataset.csv
├── olist_order_items_dataset.csv
├── olist_order_payments_dataset.csv
├── olist_order_reviews_dataset.csv
├── olist_customers_dataset.csv
├── olist_products_dataset.csv
└── product_category_name_translation.csv
```

### 4. Set up your API key

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_key_here
```

Get a free API key at [console.groq.com](https://console.groq.com).

### 5. Run

```bash
python app.py
```

Then open [http://localhost:5000](http://localhost:5000) in your browser.

---

## Requirements

```
flask
groq
pandas
python-dotenv
```

---

## How It Works

| Layer | File | What it does |
|---|---|---|
| ETL | `src/etl.py` | Loads and merges 7 CSV files, engineers features (churn, delay, revenue) |
| Analysis | `src/analysis.py` | Aggregates data into chart-ready JSON |
| Chat | `src/chatbot.py` | Sends stats + conversation history to Groq Llama 3 |
| App | `app.py` | Flask routes, session management, serves the dashboard |
| Frontend | `templates/index.html` | Plotly charts, KPI cards, chat UI |

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Your Groq API key from console.groq.com |

---

## Important

- Add `.env` to your `.gitignore` 
- The dataset is not included in this repo, download it from Kaggle
