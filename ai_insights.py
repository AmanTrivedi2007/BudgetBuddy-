import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import matplotlib.pyplot as plt

from database import get_all_expenses
from auth import check_authentication

st.set_page_config(page_title="AI Insights", page_icon="🧠", layout="wide")

try:
    API_KEY = st.secrets["GOOGLE_AI_API_KEY"]
    AI_READY = True
except:
    AI_READY = False

st.title("🤖 AI Budget Advisor")

username = check_authentication()
if not username:
    st.stop()

@st.cache_data
def load_data():
    expenses = get_all_expenses(username)
    if not expenses:
        st.warning("Add expenses first!")
        st.stop()
    df = pd.DataFrame(expenses, columns=['id','category','amount','date','description'])
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = pd.to_numeric(df['amount'])
    return df.dropna()

def ask_ai(prompt):
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 200}
    }
    try:
        r = requests.post(f"{url}?key={API_KEY}", headers=headers, json=data)
        if r.status_code == 200:
            return r.json()['candidates'][0]['content']['parts'][0]['text']
        return "API Error"
    except:
        return "Network error"

df = load_data()

# Stats
total = df['amount'].sum()
top_cat = df.groupby('category')['amount'].sum().idxmax()

col1, col2 = st.columns(2)
col1.metric("Total Spent", f"₹{total:,.0f}")
col2.metric("Top Category", top_cat)

# Chart
fig, ax = plt.subplots()
df.groupby('category')['amount'].sum().plot(kind='pie', ax=ax, autopct='%1.1f%%')
st.pyplot(fig)

# Chat
st.subheader("💬 AI Chat")
if 'history' not in st.session_state:
    st.session_state.history = []

for h in st.session_state.history[-4:]:
    st.write(f"**You:** {h['q']}")
    st.write(f"**AI:** {h['a']}")

q = st.text_input("Ask about budget...")
if st.button("Send") and q and AI_READY:
    ctx = f"Total ₹{total:,.0f}, top category {top_cat}."
    prompt = f"Finance expert. {ctx} Q: {q} Answer:"
    with st.spinner("AI..."):
        ans = ask_ai(prompt)
        st.session_state.history.append({"q": q, "a": ans})
        st.rerun()

st.markdown("*Google Gemini Pro • Secure API*")
