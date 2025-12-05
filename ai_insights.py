import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

from database import get_all_expenses
from auth import check_authentication

st.set_page_config(layout="wide")
st.title("🤖 AI Budget Advisor ✅")

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

df = load_data()
total = df['amount'].sum()
top_cat = df.groupby('category')['amount'].sum().idxmax()

col1, col2 = st.columns(2)
col1.metric("💰 Total", f"₹{total:,.0f}")
col2.metric("🔥 Top", top_cat)

# Pie chart
fig, ax = plt.subplots(figsize=(8,6))
df.groupby('category')['amount'].sum().plot(kind='pie', ax=ax, autopct='%1.1f%%')
st.pyplot(fig)

# ✅ WORKING AI CHAT
st.subheader("💬 AI Chat")
if 'history' not in st.session_state:
    st.session_state.history = []

for h in st.session_state.history[-3:]:
    st.markdown(f"**You:** {h['q']}")
    st.markdown(f"**AI:** {h['a']}")

try:
    API_KEY = st.secrets["GOOGLE_AI_API_KEY"]
    q = st.text_input("Ask budget question...")
    if st.button("🤖 Send") and q:
        prompt = f"Total ₹{total:,.0f}, top {top_cat}. Q: {q}"
        url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
        r = requests.post(url+f"?key={API_KEY}", json={"contents":[{"parts":[{"text":prompt}]}]})
        if r.status_code == 200:
            ans = r.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            ans = f"Error {r.status_code}"
        st.session_state.history.append({"q": q, "a": ans})
        st.rerun()
except:
    st.error("Add GOOGLE_AI_API_KEY to secrets!")
