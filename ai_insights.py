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

# Secure Google AI API from Streamlit Secrets
try:
    GOOGLE_AI_API_KEY = st.secrets["GOOGLE_AI_API_KEY"]
    GOOGLE_AI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
    AI_READY = True
except:
    AI_READY = False

st.title("🤖 AI Budget Advisor")
st.markdown("**Your Personal Finance Assistant - Powered by Google AI**")

# Authentication
username = check_authentication()
if not username:
    st.stop()

# Chat history storage
if 'ai_chat_history' not in st.session_state:
    st.session_state.ai_chat_history = []

@st.cache_data
def load_user_spending_data():
    """Load user's spending data for AI context"""
    expenses = get_all_expenses(username)
    if not expenses:
        st.warning("👆 **Add expenses first** to get AI insights!")
        st.stop()
    
    df = pd.DataFrame(expenses, columns=['id', 'category', 'amount', 'date', 'description'])
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = pd.to_numeric(df['amount'])
    df = df.dropna()
    
    return df

def get_ai_insight(prompt, context=""):
    """Call Google AI API with proper error handling"""
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": f"{context}\n\n{prompt}"}]}],
        "generationConfig": {
            "temperature": 0.8,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 400
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
        else:
            return f"⚠️ API Error {response.status_code}. Check your API key!"
            
    except Exception as e:
        return f"❌ Connection error: {str(e)}"

# Load spending data
df = load_user_spending_data()

# Financial Summary
col1, col2, col3, col4 = st.columns(4)
total_spent = df['amount'].sum()
avg_daily = df['amount'].mean()
categories = df['category'].nunique()
days_with_data = df['date'].nunique()

with col1:
    st.metric("💰 Total Spent", f"₹{total_spent:,.0f}")
with col2:
    st.metric("📊 Categories", categories)
with col3:
    st.metric("📅 Days Tracked", days_with_data)
with col4:
    st.metric("💵 Avg Daily", f"₹{avg_daily:.0f}")

# Category breakdown pie chart
st.subheader("📊 Your Spending Breakdown")
category_totals = df.groupby('category')['amount'].sum().round(0)
fig1, ax1 = plt.subplots(figsize=(10, 8))
colors = plt.cm.Set3(range(len(category_totals)))
wedges, texts, autotexts = ax1.pie(category_totals.values, labels=category_totals.index, 
                                   autopct='%1.1f%%', startangle=90, colors=colors)
ax1.set_title("Spending by Category", fontsize=16, fontweight='bold')
plt.setp(autotexts, size=10, weight="bold")
st.pyplot(fig1)

# Recent spending trends
st.subheader("📈 Recent Trends")
monthly = df.groupby([df['date'].dt.to_period('M'), 'category'])['amount'].sum().unstack(fill_value=0)
monthly['Total'] = monthly.sum(axis=1)
recent_months = monthly.tail(6)
st.dataframe(recent_months.T.round(0).style.format('₹{:.0f}'), use_container_width=True)

# MAIN AI CHAT INTERFACE - FIXED FOR STREAMLIT CLOUD
st.markdown("---")
st.markdown("### 💬 **Chat with Your AI Budget Advisor**")
st.markdown("*Ask about saving money, budget tips, spending patterns, or analysis*")

# Chat history display (last 12 messages)
if st.session_state.ai_chat_history:
    st.markdown("---")
    for i, chat in enumerate(reversed(st.session_state.ai_chat_history[-12:])):
        col1, col2 = st.columns([1, 8])
        with col1:
            st.markdown("👤")
        with col2:
            st.markdown(f"**You** ({chat.get('time', 'recent')}): {chat['question']}")
        
        col1, col2 = st.columns([1, 8])
        with col1:
            st.markdown("🤖")
        with col2:
            st.markdown(f"**AI**: {chat['answer']}")

# Chat input - FIXED VERSION
user_question = st.text_input(
    "💭 Type your question (e.g., 'How can I save on food expenses?')", 
    placeholder="Ask anything about your budget...",
    label_visibility="collapsed"
)

col_btn1, col_btn2 = st.columns([3, 1])
with col_btn1:
    send_button = st.button("Send to AI", type="primary", use_container_width=True)
with col_btn2:
    if st.button("🗑️ Clear History", type="secondary"):
        st.session_state.ai_chat_history = []
        st.rerun()

# Send message to AI
if send_button and user_question.strip():
    # Build rich financial context
    top_category = df.groupby('category')['amount'].sum().idxmax()
    top_amount = df.groupby('category')['amount'].sum().max()
    
    context = f"""
**User Financial Profile:**
• Total spent: ₹{total_spent:,.0f} 
• Tracked {days_with_data} days across {categories} categories
• Biggest spender: {top_category} (₹{top_amount:,.0f})
• Average daily spend: ₹{avg_daily:.0f}

**Recent monthly totals:**
{recent_months['Total'].to_dict()}
"""
    
    full_prompt = f"""
You are a smart personal finance advisor for Indian users. 

{context}

**User asks:** {user_question}

Give practical, actionable advice using ₹ symbol. Be encouraging and specific.
Keep response under 200 words. Focus on savings opportunities.
"""
    
    if AI_READY:
        with st.spinner("🤖 AI analyzing your finances..."):
            ai_answer = get_ai_insight(full_prompt)
            
            # Save to chat history
            st.session_state.ai_chat_history.append({
                'question': user_question,
                'answer': ai_answer,
                'time': datetime.now().strftime('%H:%M'),
                'total_spent': total_spent
            })
            st.rerun()
    else:
        st.error("❌ **AI UNAVAILABLE** - Add `GOOGLE_AI_API_KEY` to Streamlit Secrets!")
        st.info("✅ **Charts & stats work without API!**")

# Quick AI prompts
st.markdown("---")
st.markdown("### 🚀 **Quick Questions**")
quick_prompts = [
    "How can I save money on my biggest expense?",
    "What's my spending pattern like?",
    "Give me 3 budget tips for this month",
    "Should I cut spending in any category?",
    "How much could I save next month?"
]

cols = st.columns(3)
for i, prompt in enumerate(quick_prompts):
    if cols[i%3].button(prompt, key=f"quick_{i}", use_container_width=True):
        st.session_state.user_question_temp = prompt
        st.rerun()

# Stats footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📊 Transactions", len(df))
with col2:
    st.metric("💬 AI Chats", len(st.session_state.ai_chat_history))
with col3:
    st.metric("📈 Categories", df['category'].nunique())

st.markdown("*🔒 Private & Secure • 🤖 Google Gemini Pro • 📱 Works on all devices*")

