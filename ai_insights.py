import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns
import requests
sns.set_style("whitegrid")

from database import get_all_expenses
from auth import check_authentication

st.set_page_config(page_title="AI Insights - BudgetBuddy", page_icon="🧠", layout="wide")

# Securely load Google AI API key from Streamlit Secrets
try:
    GOOGLE_AI_API_KEY = st.secrets["GOOGLE_AI_API_KEY"]
    GOOGLE_AI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    AI_AVAILABLE = True
except Exception:
    AI_AVAILABLE = False
    st.warning("🔑 Add your Google AI API key to Streamlit Secrets for full AI features!")

st.title("🧠 AI Budget Insights & Advisor")
st.markdown("**ML Predictions + Smart Chat Assistant**")

# Authentication
username = check_authentication()
if not username:
    st.stop()

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'ml_model_trained' not in st.session_state:
    st.session_state.ml_model_trained = False

@st.cache_data
def load_user_data():
    expenses_list = get_all_expenses(username)
    if not expenses_list or len(expenses_list) == 0:
        st.warning("👆 **Add 5+ expenses first** in Expense Tracker!")
        st.stop()
    df = pd.DataFrame(expenses_list, columns=['id', 'category', 'amount', 'date', 'description'])
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df = df[df['amount'] > 0]
    if df.empty:
        st.warning("❌ No valid expense data found!")
        st.stop()
    return df

def get_google_ai_response(prompt):
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 300
        }
    }
    try:
        response = requests.post(f"{GOOGLE_AI_URL}?key={GOOGLE_AI_API_KEY}", 
                               headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        return "🔧 AI service temporarily unavailable. Try ML predictions!"
    except:
        return "💡 **Quick Tip**: Track daily expenses and set category budgets to save 20-30% monthly!"

df = load_user_data()

with st.expander("🔍 Preview Your Data", expanded=False):
    st.dataframe(df.head(10), use_container_width=True)

col1, col2, col3 = st.columns(3)
with col1:
    total_spent = df['amount'].sum()
    st.metric("💰 Total Spent", f"₹{total_spent:,.0f}")
with col2:
    avg_monthly = df.groupby(df['date'].dt.to_period('M'))['amount'].sum().mean()
    st.metric("📅 Avg Monthly", f"₹{avg_monthly:,.0f}")
with col3:
    top_cat = df.groupby('category')['amount'].sum().idxmax()
    top_cat_amount = df.groupby('category')['amount'].sum().max()
    st.metric("🔥 Top Category", f"{top_cat}")

st.markdown("---")
st.subheader("📈 Next Month Spending Predictions")

if st.button("🚀 Train AI Model & Predict", type="primary", use_container_width=True):
    with st.spinner("🤖 Training ML model on YOUR data..."):
        df_ml = df.copy()
        df_ml['month'] = df_ml['date'].dt.month
        df_ml['day_of_week'] = df_ml['date'].dt.dayofweek
        
        le = LabelEncoder()
        df_ml['category_code'] = le.fit_transform(df_ml['category'])
        
        X = df_ml[['category_code', 'month', 'day_of_week']]
        y = df_ml['amount']
        
        model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=6)
        model.fit(X, y)
        
        next_month = (datetime.now().month % 12) + 1
        predictions = {}
        for cat in df['category'].unique():
            cat_code = le.transform([cat])[0]
            pred = model.predict([[cat_code, next_month, 3]])[0]
            predictions[cat] = max(0, pred)
        
        st.session_state.ml_model_trained = True
        st.session_state.predictions = predictions
        st.session_state.model_accuracy = model.score(X, y)
        st.session_state.category_encoder = le
        
        pred_df = pd.DataFrame([
            {'Category': cat, 'Predicted': amt, '% of Total': f"{amt/total_spent*100:.1f}%"}
            for cat, amt in sorted(predictions.items(), key=lambda x: x[1], reverse=True)
        ])
        
        st.success(f"✅ Model Accuracy: {st.session_state.model_accuracy:.1%}")
        st.dataframe(pred_df.style.format({'Predicted': '₹{:.0f}'}), 
                     use_container_width=True, height=350)
        
        top_pred = pred_df.iloc[0]
        st.error(f"⚠️ {top_pred['Category']} is predicted to cost ₹{top_pred['Predicted']:,.0f} next month!")

st.subheader("📊 Spending Trends")
monthly_spending = df.groupby([df['date'].dt.to_period('M'), 'category'])['amount'].sum().reset_index()
monthly_spending['date'] = monthly_spending['date'].astype(str)

fig, ax = plt.subplots(figsize=(14, 7))
top_categories = monthly_spending.groupby('category')['amount'].sum().nlargest(6).index
colors = plt.cm.Set3(np.linspace(0, 1, len(top_categories)))
for i, cat in enumerate(top_categories):
    cat_data = monthly_spending[monthly_spending['category'] == cat]
    ax.plot(cat_data['date'], cat_data['amount'], marker='o', linewidth=3, 
            label=cat, color=colors[i], markersize=8)
ax.set_title("Your Spending Evolution (Top Categories)", fontsize=16, fontweight='bold')
ax.set_ylabel("Amount Spent (₹)", fontsize=12)
ax.tick_params(axis='x', rotation=45)
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
ax.grid(True, alpha=0.3)
plt.tight_layout()
st.pyplot(fig)

st.markdown("---")
st.subheader("💬 AI Budget Advisor")

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if st.button("💭 Clear Chat History", type="secondary"):
    st.session_state.chat_history = []
    st.experimental_rerun()

prompt = st.chat_input("Ask about your budget, spending patterns, or get saving tips...")

if prompt:
    context = f"""
User's financial data:
- Total spent: ₹{total_spent:,.0f}
- Average monthly: ₹{avg_monthly:,.0f}
- Top category: {top_cat} (₹{top_cat_amount:,.0f})
"""
    if st.session_state.get('ml_model_trained', False):
        context += f"\nNext month predictions: {st.session_state.predictions}"

    full_prompt = f"{context}\n\nQ: {prompt}\nA:"

    if AI_AVAILABLE:
        with st.chat_message("assistant"):
            with st.spinner("AI thinking..."):
                ai_response = get_google_ai_response(full_prompt)
                st.markdown(ai_response)
                st.session_state.chat_history.append({'user': prompt, 'ai': ai_response})
    else:
        st.chat_message("assistant").markdown(
            "🔑 **Add Google AI API key to Streamlit Secrets** to enable AI chat!"
            "\nML predictions work without API."
        )

for chat in st.session_state.chat_history[-10:]:
    with st.chat_message("user"):
        st.markdown(chat['user'])
    with st.chat_message("assistant"):
        st.markdown(chat['ai'])

st.markdown("---")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📊 Data Points", len(df))
with col2:
    if st.session_state.get('ml_model_trained', False):
        st.metric("🎯 ML Accuracy", f"{st.session_state['model_accuracy']:.1%}")
with col3:
    st.metric("💬 Chat Messages", len(st.session_state.chat_history))

st.markdown(
    "*🔒 Your data is private • 🤖 Powered by scikit-learn and Google AI Studio • "
    "📈 Model accuracy adapts to your data*"
)

def get_google_ai_response(prompt):
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 300,
        }
    }
    try:
        response = requests.post(f"{GOOGLE_AI_URL}?key={GOOGLE_AI_API_KEY}",
                                 headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return "⚠️ AI service temporarily unavailable. Try again later!"
    except Exception:
        return "⚠️ Error contacting AI service."
