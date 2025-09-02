import streamlit as st
import sqlite3
import os
import pandas as pd

DB_PATH = "loancam.db"
CSV_PATH = "loancamdata.csv"  # Make sure this file is in the repo/folder

st.title("📊 LoanCam SQLite Database Test & Init")

# -----------------------------
# Initialize Database
# -----------------------------
if st.button("Initialize Database"):
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # Define columns and types
        columns = {
            "Application_ID": "TEXT",
            "Full_Name": "TEXT",
            "Age": "INTEGER",
            "Location": "TEXT",
            "Date": "TEXT",
            "Loan_Type": "TEXT",
            "Marital_Status": "TEXT",
            "Collateral_Type": "TEXT",
            "Collateral_Value": "REAL",
            "Employee_Status": "TEXT",
            "Income": "REAL",
            "Loan_Term": "INTEGER",
            "Loan_Amount": "REAL",
            "Monthly_Payment": "REAL",
            "Debt": "REAL",
            "Dti": "REAL",
            "LVR": "REAL",
            "Guarantor": "TEXT",
            "Customer_Status": "TEXT",
            "Customer_Relation": "TEXT",
            "Interest_Rate": "REAL",
            "Loan_Reason": "TEXT",
            "Credit_History": "INTEGER",
            "Loan_Status": "TEXT",
            "Loan_Binary_Status": "INTEGER",
            "Guarantor_Binary": "INTEGER",
            "Customer_Status_Encoded": "REAL",
            "RM_Code": "TEXT",
            "id_card": "TEXT",
            "land_plan": "TEXT"
        }

        # Create table
        columns_sql = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
        create_table_sql = f"CREATE TABLE loancamdata ({columns_sql});"
        cur.execute(create_table_sql)
        conn.commit()

        # Load CSV if exists
        if os.path.exists(CSV_PATH):
            df = pd.read_csv(CSV_PATH)
            df.to_sql("loancamdata", conn, if_exists="replace", index=False)
            st.success(f"Database created and loaded from {CSV_PATH}")
        else:
            st.success(f"Database created at {DB_PATH} with empty table 'loancamdata'")

        conn.close()
    else:
        st.info(f"Database {DB_PATH} already exists.")

# -----------------------------
# Test Database Connection
# -----------------------------
if st.button("Test Database"):
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql("SELECT * FROM loancamdata LIMIT 5;", conn)
        st.dataframe(df)
        conn.close()
    else:
        st.error("Database not found. Please initialize it first.")
