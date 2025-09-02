import streamlit as st
import sqlite3
import pandas as pd
from sqlalchemy import create_engine
import requests
import os

# -------------------------
# Database
# -------------------------
DB_PATH = "loancam.db"

if not os.path.exists(DB_PATH):
    st.error("Database not found. Place 'loancam.db' in the folder.")
else:
    engine = create_engine(f"sqlite:///{DB_PATH}")

# -------------------------
# Hugging Face LLaMA API
# -------------------------
HF_API_TOKEN = st.secrets["HF_API_TOKEN"]
HF_MODEL = "meta-llama/Llama-3.1-8B"

def generate_llm_advice(changes: list, loan_type: str) -> str:
    prompt = f"""You are a financial advisor helping {loan_type} loan applicants.
Changes: {"; ".join(changes)}
Explain how these changes improve approval chances."""

    API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
        if response.status_code == 200:
            result = response.json()
            # Hugging Face often returns [{"generated_text": "..."}]
            if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
                return result[0]["generated_text"]
            elif isinstance(result, dict) and "error" in result:
                return f"HF API Error: {result['error']}"
            else:
                return str(result)
        else:
            return f"HF API error {response.status_code}: {response.text}"
    except Exception as e:
        return f"AI Advice could not be generated due to: {str(e)}"

# -------------------------
# Streamlit UI
# -------------------------
st.title("Loan Approval Test App")

if st.button("Test DB Connection"):
    try:
        with engine.connect() as conn:
            df = pd.read_sql("SELECT * FROM loancamdata LIMIT 5", conn)
            st.success("✅ Connected to database!")
            st.dataframe(df)
    except Exception as e:
        st.error(f"DB Error: {str(e)}")

st.subheader("Generate LLM Advice")
changes = st.text_area("Enter changes (comma-separated)").split(",")
loan_type = st.selectbox("Loan Type", ["Personal Loan", "Home Loan", "SME Loan"])
if st.button("Generate Advice"):
    if changes:
        advice = generate_llm_advice(changes, loan_type)
        st.write(advice)
    else:
        st.warning("Please enter some changes.")
