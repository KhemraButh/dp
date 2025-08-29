# app.py
import streamlit as st
import pandas as pd
import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# -------------------------------
# Database connection (SQLite file)
# -------------------------------
db_url = "sqlite:///loancam.db"  # SQLite DB file in the same folder
engine = create_engine(db_url)

# -------------------------------
# Function to test DB query
# -------------------------------
def test_connection():
    try:
        with engine.connect() as conn:
            query = text("SELECT * FROM loancamdata LIMIT 5")
            result = conn.execute(query)
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            return df
    except SQLAlchemyError as e:
        st.error(f"Database error: {str(e)}")
        return pd.DataFrame()

# -------------------------------
# Streamlit Interface
# -------------------------------
st.title("🔗 SQLite Database Connectivity Test")

st.write("This small app tests if the SQLite database connection works correctly.")

if st.button("Test DB Connection"):
    df = test_connection()
    if not df.empty:
        st.success("✅ Successfully connected to SQLite database!")
        st.dataframe(df)
    else:
        st.error("❌ Could not retrieve data from the SQLite database.")
