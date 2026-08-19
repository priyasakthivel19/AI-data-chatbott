import os
import requests
import pandas as pd
import re
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={API_KEY}"

def generate_pandas_code(df, question):
    """Ask Gemini to generate pandas code for the given question"""

    prompt = f"""You are a Python data analyst. Given a pandas DataFrame `df` with these columns:
{list(df.columns)}

Column data types: {df.dtypes.to_dict()}

Write ONLY a single line of pandas code (no explanation, no markdown, no ```python) to answer this question:
"{question}"

The code should store the final answer in a variable called `result`.
Example format: result = df['column'].sum()
"""

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0
        }
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"Status: {response.status_code} | Response: {response.text}")

    result_json = response.json()
    code = result_json["candidates"][0]["content"]["parts"][0]["text"]

    # Clean up markdown code fences if present
    code = re.sub(r"```python|```", "", code).strip()
    return code


def ask_question(df, question):
    """Generate pandas code for the question, execute it, and return the answer"""
    try:
        code = generate_pandas_code(df, question)

        # Execute the generated code safely
        local_vars = {"df": df, "pd": pd}
        exec(code, {}, local_vars)
        result = local_vars.get("result", "Could not find a result")

        return f"**Answer:** {result}\n\n*Generated code:* `{code}`"
    except Exception as e:
        return f"Error: {str(e)}"