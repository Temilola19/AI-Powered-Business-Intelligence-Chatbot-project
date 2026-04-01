import os
from dotenv import load_dotenv

load_dotenv()  # must be before any src imports so GROQ_API_KEY is set in time

from flask import Flask, render_template, request, jsonify, session
from src.etl import load_and_merge, get_summary_stats
from src.analysis import get_all_charts
from src.chatbot import ask, format_history

app = Flask(__name__)
app.secret_key = "olist-bi-local"

print("Loading data...")
df     = load_and_merge()
stats  = get_summary_stats(df)
charts = get_all_charts(df)
print("Ready!")


@app.route("/")
def index():
    return render_template("index.html", stats=stats, charts=charts)


@app.route("/chat", methods=["POST"])
def chat():
    question = request.json.get("question", "")
    history  = session.get("history", [])
    answer   = ask(question, stats, format_history(history))
    history.append({"role": "user",      "content": question})
    history.append({"role": "assistant", "content": answer})
    session["history"] = history[-10:]
    return jsonify({"answer": answer})


@app.route("/reset", methods=["POST"])
def reset():
    session.pop("history", None)
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True)
