# App.py - Main Application with Onboarding Tutorial

import streamlit as st
from database import init_database
from auth import check_authentication

# Initialize database
init_database()

# Page configuration
st.set_page_config(
    page_title="BudgetBuddy",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check authentication FIRST
username = check_authentication()

# Initialize dark mode in session state
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# ===========================
# SHOW ONBOARDING TUTORIAL FOR NEW USERS
# ===========================
from boarding import show_onboarding_tutorial

# Check if tutorial should be shown
if show_onboarding_tutorial():
    # Tutorial is active - stop here and don't show the rest of the app
    st.stop()

# ===========================
# MAIN APP (Shows only after tutorial is completed/skipped)
# ===========================

# Define all pages
page1 = st.Page("Description.py", title="Home", icon="🏠")
page2 = st.Page("income_monitoring.py", title="Income Monitoring", icon="💵")
page3 = st.Page("expense.py", title="Expense Tracking", icon="💳")
page4 = st.Page("budget_manager.py", title="Budget Manager", icon="💰")
page5 = st.Page("recurring_transactions.py", title="Recurring Transactions", icon="🔁")
page6 = st.Page("Saving_goal.py", title="Savings Goals", icon="🎯")
page7 = st.Page("visualization.py", title="Advanced Visualizations", icon="📊")

# Create navigation with all pages
pg = st.navigation(
    [page1, page2, page3, page4, page5, page6, page7],
    position="sidebar"
)

# ===========================
# SIDEBAR - User Info & Settings
# ===========================
with st.sidebar:
    st.markdown("---")
    
    # User info section
    if st.session_state.get('full_name'):
        st.markdown(f"### 👤 {st.session_state.full_name}")
        st.caption(f"@{username}")
    else:
        st.markdown(f"### 👤 {username}")
    
    st.markdown("---")
    
    # Settings Section
    st.markdown("### ⚙️ Settings")
    
    # Dark Mode Toggle
    dark_mode = st.toggle(
        "🌙 Dark Mode",
        value=st.session_state.dark_mode,
        help="Toggle dark/light theme"
    )
    
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.rerun()
    
    # Apply dark mode CSS
    if st.session_state.dark_mode:
        st.markdown("""
        <style>
            .stApp {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            .stSidebar {
                background-color: #2d2d2d;
            }
            .stMarkdown {
                color: #ffffff;
            }
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tutorial Controls
    st.markdown("### 📚 Help & Tutorials")
    
    # Show Tutorial Button
    if st.button("📖 Restart Tutorial", use_container_width=True):
        # Reset onboarding to show again
        from boarding import reset_onboarding
        reset_onboarding()
        st.success("✅ Tutorial reset! Reloading...")
        st.rerun()
    
    st.markdown("---")
    
    # Quick Tips
    with st.expander("💡 Quick Tips"):
        st.markdown("""
        **Daily Tasks:**
        - Log expenses immediately
        - Check your dashboard
        
        **Weekly Reviews:**
        - Review spending trends
        - Update budget limits
        
        **Monthly Goals:**
        - Export data for records
        - Adjust savings goals
        """)
    
    st.markdown("---")
    
    # Logout button
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        # Clear all session state
        keys_to_clear = ['username', 'full_name', 'dark_mode', 'onboarding_completed', 'onboarding_step']
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
    st.markdown("---")
    
    # Footer info
    st.caption("💰 BudgetBuddy v3.0")
    st.caption("🔒 Your data is private & secure")
    st.caption("📊 Real-time financial insights")
    st.caption("🎯 Smart budget management")

# Run the selected page
pg.run()
