from flask import Flask, render_template, request, jsonify, session
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from etl import load_and_merge, get_summary_stats
from analysis import get_all_charts
from chatbot import ask, format_history
import json
from dotenv import load_dotenv
import os

load_dotenv() 

api_key = os.getenv("GROQ_API_KEY")

app = Flask(__name__)
app.secret_key = "olist-bi-secret-2024"


print("Loading data pipeline...")
df = load_and_merge()
stats = get_summary_stats(df)
charts = get_all_charts(df)
print("Data ready.")


@app.route("/")
def index():
    return render_template("index.html", stats=stats, charts=json.dumps(charts))


@app.route("/chat", methods=["POST"])
def chat():
    data     = request.json
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "No question provided"}), 400

    
    history = session.get("history", [])

    try:
        answer = ask(question, stats, format_history(history))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
    history.append({"role": "user",      "content": question})
    history.append({"role": "assistant", "content": answer})
    session["history"] = history[-10:]

    return jsonify({"answer": answer})


@app.route("/reset", methods=["POST"])
def reset():
    session.pop("history", None)
    return jsonify({"status": "reset"})


if __name__ == "__main__":
    app.run(debug=True)
