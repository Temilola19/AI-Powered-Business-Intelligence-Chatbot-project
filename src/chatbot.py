from groq import Groq
import os
from dotenv import load_dotenv
import json

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask(question: str, stats: dict, history: list) -> str:

    system_prompt = f"""You are an expert business intelligence analyst for a Brazilian e-commerce company.
You have access to the following real business metrics derived from 100,000+ orders:

{json.dumps(stats, indent=2)}

Your job is to answer business questions clearly and concisely using this data.
- Always reference specific numbers from the data when answering
- If a question cannot be answered from the available data, say so clearly
- Keep answers concise but insightful — 3 to 5 sentences max
- Highlight actionable insights where relevant
- Do not make up data that is not in the stats above
"""

   
    messages = [{"role": "system", "content": system_prompt}]
    messages += history
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b", 
        max_tokens=1000,
        messages=messages
    )

  
    return response.choices[0].message.content


def format_history(history: list) -> list:
    """Keep only the last 10 messages to avoid context overflow."""
    return history[-10:]