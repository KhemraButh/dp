import streamlit as st
import requests

# -------------------------
# Streamlit Page Config
# -------------------------
st.set_page_config(page_title="Loan Approval Advisor", layout="wide")
st.title("🏦 Loan Approval Advisor")

# -------------------------
# Hugging Face API Config
# -------------------------
HF_MODEL = "microsoft/DialoGPT-medium"  # small model for testing
HF_API_TOKEN = st.secrets.get("HF_API_TOKEN", "")

# -------------------------
# AI Advice Generation
# -------------------------
def generate_hf_advice(changes: list, loan_type: str) -> str:
    """Generate advice using Hugging Face API"""
    if not HF_API_TOKEN:
        return "HF API token not configured. Using fallback advice."

    prompt = (
        f"As a financial advisor, provide 2-3 practical suggestions for a {loan_type} applicant "
        f"based on these changes: {', '.join(changes)}.\n"
        "Explain how each change improves approval chances."
    )

    API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

    try:
        response = requests.post(API_URL, headers=headers, json={
            "inputs": prompt,
            "parameters": {"max_new_tokens": 200, "temperature": 0.7}
        }, timeout=30)

        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and "generated_text" in result[0]:
                return result[0]["generated_text"].replace(prompt, "").strip()
            return str(result)
        else:
            return f"HF API error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Hugging Face API request failed: {str(e)}"

def generate_rule_based_advice(changes: list, loan_type: str) -> str:
    """Fallback advice if HF API fails"""
    advice = []
    for change in changes:
        change_lower = change.lower()
        if any(word in change_lower for word in ['income', 'salary', 'revenue']):
            advice.append("• Increase verifiable income sources (employment, business).")
        elif any(word in change_lower for word in ['debt', 'loan', 'liability']):
            advice.append("• Reduce existing debt-to-income ratio.")
        elif any(word in change_lower for word in ['credit', 'score', 'history']):
            advice.append("• Improve credit history by paying bills on time.")
        elif any(word in change_lower for word in ['collateral', 'asset', 'property']):
            advice.append("• Provide strong collateral documentation.")
        elif any(word in change_lower for word in ['guarantor', 'co-signer']):
            advice.append("• Add a creditworthy guarantor.")
    return "\n".join(advice) if advice else "Focus on improving income, credit, and collateral."

def generate_ai_advice(changes: list, loan_type: str) -> str:
    """Try HF API first, then fallback"""
    if HF_API_TOKEN:
        hf_result = generate_hf_advice(changes, loan_type)
        if "error" not in hf_result.lower():
            return hf_result
    return generate_rule_based_advice(changes, loan_type)

# -------------------------
# Streamlit UI
# -------------------------
st.header("🤖 AI Loan Advisor")

loan_type = st.selectbox(
    "Loan Type",
    ["Personal Loan", "Home Loan", "SME Loan", "Auto Loan", "Education Loan"]
)

changes_input = st.text_area(
    "Desired Improvements (one per line)",
    placeholder="Example:\nIncrease income by 20%\nImprove credit score\nReduce existing debt"
)

if st.button("Generate Advice"):
    if changes_input.strip():
        changes = [line.strip() for line in changes_input.split('\n') if line.strip()]
        with st.spinner("Generating AI advice..."):
            advice = generate_ai_advice(changes, loan_type)
            st.success("✅ Here's your personalized advice:")
            st.write(advice)
    else:
        st.warning("Please enter some changes or improvements.")
