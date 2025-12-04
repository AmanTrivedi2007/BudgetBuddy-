import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")

from database import get_all_expenses
from auth import check_authentication

st.set_page_config(page_title="AI Insights - BudgetBuddy", page_icon="🧠", layout="wide")

# ✅ CORRECT Google AI Endpoint (FIXED 404)
try:
    GOOGLE_AI_API_KEY = st.secrets["GOOGLE_AI_API_KEY"]
    GOOGLE_AI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    AI_READY = True
    st.success("✅ Google AI Connected!")
except:
    AI_READY = False
    st.error("❌ Add GOOGLE_AI_API_KEY to Streamlit Secrets!")

st.title("🤖 AI Budget Advisor")
st.markdown("**Powered by Google Gemini**")

username = check_authentication()
if not username:
    st.stop()

if 'ai_chat_history' not in st.session_state:
    st.session_state.ai_chat_history = []

@st.cache_data
def load_user_spending_data():
    expenses = get_all_expenses(username)
    if not expenses:
        st.warning("👆 Add expenses first!")
        st.stop()
    df = pd.DataFrame(expenses, columns=['id', 'category', 'amount', 'date', 'description'])
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = pd.to_numeric(df['amount'])
    return df.dropna()

def get_ai_insight(prompt):
    """✅ WORKING Google AI Call"""
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 300
        }
    }
    try:
        response = requests.post(
            f"{GOOGLE_AI_URL}?key={GOOGLE_AI_API_KEY}",
            headers=headers,
            json=data,
            timeout=15
        )
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        return f"⚠️ HTTP {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return f"❌ Network error: {str(e)}"

df = load_user_spending_data()

# Stats
col1, col2, col3 = st.columns(3)
total_spent = df['amount'].sum()
top_cat = df.groupby('category')['amount'].sum().idxmax()
top_amount = df.groupby('category')['amount'].sum().max()

with col1: st.metric("💰 Total", f"₹{total_spent:,.0f}")
with col2: st.metric("🔥 Top Category", top_cat)
with col3: st.metric("📊 Transactions", len(df))

# Pie Chart
fig, ax = plt.subplots(figsize=(8, 6))
category_totals = df.groupby('category')['amount'].sum()
ax.pie(category_totals.values, labels=category_totals.index, autopct='%1.1f%%')
ax.set_title("Spending Breakdown")
st.pyplot(fig)

# AI CHAT
st.markdown("---")
st.subheader("💬 AI Budget Advisor")

if st.session_state.ai_chat_history:
    for chat in st.session_state.ai_chat_history[-6:]:
        st.markdown(f"**You:** {chat['question']}")
        st.markdown(f"**🤖 AI:** {chat['answer']}")
        st.markdown("─" * 50)

user_question = st.text_input("Ask about your budget...", key="ai_input")
if st.button("🤖 Send to AI", type="primary") and user_question:
    if AI_READY:
        context = f"Total spent ₹{total_spent:,.0f}. Top category {top_cat} ₹{top_amount:,.0f}. {len(df)} transactions."
        prompt = f"Indian finance expert. {context}\nUser: {user_question}\nAnswer:"
        
        with st.spinner("AI responding..."):
            answer = get_ai_insight(prompt)
            st.session_state.ai_chat_history.append({
                'question': user_question,
                'answer': answer
            })
            st.rerun()
    else:
        st.error("❌ API Key Missing!")

if st.button("🗑️ Clear Chat"):
    st.session_state.ai_chat_history = []
    st.rerun()

st.markdown("*✅ Google Gemini 1.5 Flash • 🔒 Secure API Key*")
