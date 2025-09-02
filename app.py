import streamlit as st
import sqlite3
import pandas as pd
import os
import tempfile

# -------------------------
# Database Setup (Streamlit Cloud Compatible)
# -------------------------
@st.cache_resource
def init_database():
    """Initialize SQLite database"""
    # Create in a temp location that works on Streamlit Cloud
    db_path = os.path.join(tempfile.gettempdir(), "loancam.db")
    conn = sqlite3.connect(db_path)
    
    # Create table if it doesn't exist
    conn.execute('''
        CREATE TABLE IF NOT EXISTS loancamdata (
            Application_ID TEXT PRIMARY KEY,
            Full_Name TEXT,
            Age INTEGER,
            Location TEXT,
            Date TEXT,
            Loan_Type TEXT,
            Marital_Status TEXT,
            Collateral_Type TEXT,
            Collateral_Value REAL,
            Employee_Status TEXT,
            Income REAL,
            Loan_Term INTEGER,
            Loan_Amount REAL,
            Debt REAL,
            Guarantor TEXT,
            Customer_Status TEXT,
            Customer_Relation TEXT,
            Interest_Rate REAL,
            Loan_Reason TEXT,
            Credit_History INTEGER,
            Loan_Status TEXT,
            RM_Code TEXT,
            Dti REAL,
            LVR REAL
        )
    ''')
    
    # Add sample data if table is empty
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM loancamdata")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ('KH00001', 'John Doe', 35, 'Phnom Penh', '2024-01-15', 'Home Loan', 
             'Married', 'House', 50000.0, 'Full-time', 3000.0, 360, 25000.0, 
             500.0, 'Yes', 'Existing', 'Loan', 5.5, 'Home purchase', 4, 
             'Approved', 'RM01', 16.7, 50.0),
            ('KH00002', 'Jane Smith', 28, 'Siem Reap', '2024-01-16', 'Personal Loan', 
             'Single', 'Car', 15000.0, 'Full-time', 2000.0, 24, 5000.0, 
             200.0, 'No', 'New', 'None', 7.0, 'Education', 3, 
             'Pending', 'RM02', 10.0, 33.3)
        ]
        conn.executemany('INSERT INTO loancamdata VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', sample_data)
        conn.commit()
    
    return conn

# Initialize database
conn = init_database()

# -------------------------
# AI Advice Generation (Streamlit Cloud Compatible)
# -------------------------
def generate_ai_advice(changes: list, loan_type: str) -> str:
    """
    Generate advice using available AI services with fallbacks
    """
    # Clean changes
    changes = [change.strip() for change in changes if change.strip()]
    
    if not changes:
        return "Please provide specific changes to get advice."
    
    # Try Hugging Face if API token is available
    hf_token = st.secrets.get("HF_API_TOKEN", "")
    if hf_token:
        try:
            return generate_huggingface_advice(changes, loan_type, hf_token)
        except:
            pass  # Fall through to other methods
    
    # Fallback: Rule-based advice
    return generate_rule_based_advice(changes, loan_type)

def generate_huggingface_advice(changes: list, loan_type: str, api_token: str) -> str:
    """Use a smaller, faster model that actually works"""
    import requests
    
    # Use a smaller model that won't timeout
    model = "microsoft/DialoGPT-medium"  # Small and fast
    
    prompt = f"""As a financial advisor, provide 2-3 brief suggestions for a {loan_type} applicant based on these desired changes: {', '.join(changes)}.
    
Provide practical, actionable advice in simple language. Focus on how these changes improve approval chances."""

    API_URL = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {api_token}"}

    try:
        response = requests.post(API_URL, headers=headers, json={
            "inputs": prompt,
            "parameters": {
                "max_length": 200,
                "temperature": 0.7,
                "do_sample": True
            }
        }, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                if "generated_text" in result[0]:
                    return result[0]["generated_text"].replace(prompt, "").strip()
            return str(result)
        else:
            return f"API error: {response.status_code}"
            
    except Exception as e:
        raise Exception(f"Hugging Face error: {str(e)}")

def generate_rule_based_advice(changes: list, loan_type: str) -> str:
    """Fallback rule-based advice when AI is unavailable"""
    advice = []
    
    for change in changes:
        change_lower = change.lower()
        
        if any(word in change_lower for word in ['income', 'salary', 'revenue']):
            advice.append("• Increase verifiable income sources through employment documents or business records")
        elif any(word in change_lower for word in ['debt', 'loan', 'liability']):
            advice.append("• Reduce existing debt-to-income ratio by paying down current obligations")
        elif any(word in change_lower for word in ['credit', 'score', 'history']):
            advice.append("• Improve credit history by ensuring all existing accounts are in good standing")
        elif any(word in change_lower for word in ['collateral', 'asset', 'property']):
            advice.append("• Provide additional collateral documentation to strengthen your application")
        elif any(word in change_lower for word in ['guarantor', 'co-signer']):
            advice.append("• Consider adding a creditworthy guarantor to support your application")
        elif any(word in change_lower for word in ['employment', 'job', 'business']):
            advice.append("• Demonstrate stable employment or business history with documentation")
    
    if advice:
        return f"For your {loan_type} application, I recommend:\n\n" + "\n".join(advice)
    else:
        return f"For {loan_type} applications, focus on improving income verification, reducing existing debts, and providing strong collateral documentation."

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Loan Approval Advisor", layout="wide")
st.title("🏦 Loan Approval Advisor")

# Database Section
st.header("📊 Database Connection")
if st.button("Test Database Connection"):
    try:
        df = pd.read_sql_query("SELECT * FROM loancamdata LIMIT 5", conn)
        st.success("✅ Successfully connected to database!")
        st.dataframe(df)
        
        # Show database info
        count = pd.read_sql_query("SELECT COUNT(*) as total_records FROM loancamdata", conn)
        st.info(f"Total records in database: {count['total_records'].iloc[0]}")
        
    except Exception as e:
        st.error(f"Database error: {str(e)}")

# AI Advice Section
st.header("🤖 AI Loan Advisor")
st.write("Get personalized advice for improving your loan application")

col1, col2 = st.columns(2)

with col1:
    loan_type = st.selectbox(
        "Loan Type",
        ["Personal Loan", "Home Loan", "SME Loan", "Auto Loan", "Education Loan"],
        help="Select the type of loan you're applying for"
    )

with col2:
    changes_input = st.text_area(
        "Desired Improvements",
        placeholder="Enter changes you'd like to make (one per line)\nExample: Increase income by 20%\nImprove credit score\nReduce existing debt",
        help="List the changes you're considering for your loan application"
    )

if st.button("Generate Advice", type="primary"):
    if changes_input.strip():
        changes = [line.strip() for line in changes_input.split('\n') if line.strip()]
        
        with st.spinner("Generating personalized advice..."):
            advice = generate_ai_advice(changes, loan_type)
            
            st.success("Here's your personalized advice:")
            st.markdown(f"**For {loan_type} Application:**")
            st.write(advice)
            
            # Additional tips
            st.info("💡 **Additional Tips:**\n\n- Always provide complete documentation\n- Maintain stable employment history\n- Keep debt-to-income ratio below 40%\n- Consider adding a guarantor if possible")
    else:
        st.warning("Please enter some changes or improvements you'd like to make.")

# Footer
st.markdown("---")
st.caption("Note: AI advice is generated based on common lending practices. Actual approval depends on individual lender policies.")
