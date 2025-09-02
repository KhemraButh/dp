import sqlite3
import os
import pandas as pd

DB_PATH = "loancam.db"
CSV_PATH = "loancamdata.csv"  # optional CSV with data to populate

# -----------------------------
# Define table columns and types
# -----------------------------
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

# -----------------------------
# Create DB if it doesn't exist
# -----------------------------
if not os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Build CREATE TABLE SQL
    columns_sql = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
    create_table_sql = f"CREATE TABLE loancamdata ({columns_sql});"
    cur.execute(create_table_sql)
    conn.commit()
    print(f"Database created at {DB_PATH} with table 'loancamdata'.")

    # -----------------------------
    # Optionally populate from CSV
    # -----------------------------
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        df.to_sql("loancamdata", conn, if_exists="replace", index=False)
        print(f"Data loaded from {CSV_PATH} into 'loancamdata'.")
    
    conn.close()
else:
    print(f"Database {DB_PATH} already exists.")
