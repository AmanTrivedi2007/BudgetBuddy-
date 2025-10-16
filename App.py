# App.py
import streamlit as st
from database import init_database

# Initialize database on app start
init_database()

# Page configuration
st.set_page_config(
    page_title="BudgetBuddy",
    page_icon="💰",
    layout="wide"
)

# Define pages
page1 = st.Page("income_monitoring.py", title="Income Monitoring", icon="💵")
page2 = st.Page("expense_tracking.py", title="Expense Tracking", icon="💳")
page3 = st.Page("Saving_goal.py", title="Saving Goals", icon="🎯")
page4 = st.Page("visualization.py", title="Spending Visualization", icon="📊")

# Create navigation
pg = st.navigation([page1, page2, page3, page4], position="sidebar")

# Add sidebar header
with st.sidebar:
    st.title("💰 BudgetBuddy")
    st.caption("Your Personal Finance Companion")

# Run the selected page
pg.run()
