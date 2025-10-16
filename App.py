# App.py
import streamlit as st
from database import init_database
from auth import check_authentication

# Initialize database
init_database()

# Page configuration
st.set_page_config(
    page_title="BudgetBuddy",
    page_icon="💰",
    layout="wide"
)

# Check authentication FIRST (shows login if not authenticated)
username = check_authentication()

# Define pages
page1 = st.Page("income_monitoring.py", title="Income Monitoring", icon="💵")
page2 = st.Page("expense.py", title="Expense Tracking", icon="💳")
page3 = st.Page("Saving_goal.py", title="Saving Goals", icon="🎯")
page4 = st.Page("visualization.py", title="Spending Visualization", icon="📊")
page5 = st.Page("Description.py",title="About",icon="🆎")
# Create navigation
pg = st.navigation([page1, page2, page3, page4,page5], position="sidebar")

# Sidebar header with user info
with st.sidebar:
    st.markdown("---")
    st.markdown(f"### 👤 User: **{username}**")
    
    # Logout button
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.username = None
        st.rerun()
    
    st.markdown("---")
    st.caption("💰 Your personal finance data")

# Run selected page
pg.run()
