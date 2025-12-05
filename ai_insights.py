import streamlit as st
import pandas as pd
import google.generativeai as genai
import matplotlib.pyplot as plt
from datetime import datetime

from database import get_all_expenses
from auth import check_authentication

st.set_page_config(page_title="AI Insights - BudgetBuddy", page_icon="🧠", layout="wide")

# ✅ Configure YOUR custom model from AI Studio
try:
    API_KEY = st.secrets["GOOGLE_AI_API_KEY"]
    genai.configure(api_key=API_KEY)
    
    # YOUR CUSTOM MODEL from AI Studio
    model = genai.GenerativeModel('gen-lang-client-0670597071')
    AI_READY = True
    st.success("✅ Connected to YOUR custom AI model!")
except:
    AI_READY = False
    st.error("❌ Add GOOGLE_AI_API_KEY to Streamlit Secrets!")

st.title("🤖 AI Budget Advisor")
st.markdown("**Powered by YOUR Google AI Studio Model**")

username = check_authentication()
if not username:
    st.stop()

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

@st.cache_data
def load_spending_data():
    expenses = get_all_expenses(username)
    if not expenses:
        st.warning("👆 Add expenses first!")
        st.stop()
    df = pd.DataFrame(expenses, columns=['id', 'category', 'amount', 'date', 'description'])
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = pd.to_numeric(df['amount'])
    return df.dropna()

def ask_ai(prompt):
    """✅ Uses YOUR custom model"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error: {str(e)}"

df = load_spending_data()

# Stats
col1, col2, col3 = st.columns(3)
total = df['amount'].sum()
top_cat = df.groupby('category')['amount'].sum().idxmax()
top_amt = df.groupby('category')['amount'].sum().max()

with col1: st.metric("💰 Total", f"₹{total:,.0f}")
with col2: st.metric("🔥 Top Category", top_cat)
with col3: st.metric("📊 Transactions", len(df))

# Pie chart
st.subheader("📊 Spending Breakdown")
totals = df.groupby('category')['amount'].sum()
fig, ax = plt.subplots(figsize=(8,6))
ax.pie(totals.values, labels=totals.index, autopct='%1.1f%%')
ax.set_title("Category Spending")
st.pyplot(fig)

# AI Chat
st.markdown("---")
st.subheader("💬 Chat with YOUR AI Model")

for chat in st.session_state.chat_history[-6:]:
    st.markdown(f"**You:** {chat['q']}")
    st.markdown(f"**🤖 AI:** {chat['a']}")
    st.markdown("─" * 40)

question = st.text_input("Ask about your budget...", key="question")
if st.button("🤖 Ask AI", type="primary") and question:
    if AI_READY:
        context = f"Total spent ₹{total:,.0f}. Top category {top_cat} ₹{top_amt:,.0f}."
        prompt = f"Indian finance expert. {context}\nQ: {question}\nA:"
        
        with st.spinner("AI thinking..."):
            answer = ask_ai(prompt)
            st.session_state.chat_history.append({"q": question, "a": answer})
            st.rerun()
    else:
        st.error("❌ API Key missing!")

if st.button("🗑️ Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()

st.markdown("*✅ YOUR custom model: gen-lang-client-0670597071 • 🔒 Secure*")
