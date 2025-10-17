# App.py - Main Application with All Features

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

# Define all pages (including NEW pages)
page1 = st.Page("Description.py", title="Home", icon="🏠")
page2 = st.Page("income_monitoring.py", title="Income Monitoring", icon="💵")
page3 = st.Page("expense.py", title="Expense Tracking", icon="💳")
page4 = st.Page("budget_manager.py", title="Budget Manager", icon="💰")
page5 = st.Page("recurring_transactions.py", title="Recurring Transactions", icon="🔁")
page6 = st.Page("Saving_goal.py", title="Savings Goals", icon="🎯")
page7 = st.Page("visualization.py", title="Visualizations", icon="📊")

# Create navigation with all pages
pg = st.navigation(
    [page1, page2, page3, page4, page5, page6, page7], 
    position="sidebar"
)

# Sidebar with user info and settings
with st.sidebar:
    st.markdown("---")
    
    # User info section
    if st.session_state.get('full_name'):
        st.markdown(f"### 👤 {st.session_state.full_name}")
        st.caption(f"@{username}")
    else:
        st.markdown(f"### 👤 {username}")
    
    st.markdown("---")
    
    # Dark Mode Toggle (NEW)
    st.markdown("### ⚙️ Settings")
    
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
            /* Dark mode styles */
            .stApp {
                background-color: #1E1E1E;
                color: #E0E0E0;
            }
            .stSidebar {
                background-color: #2D2D2D;
            }
            .stMarkdown {
                color: #E0E0E0;
            }
            .stTextInput input, .stNumberInput input, .stTextArea textarea {
                background-color: #3D3D3D;
                color: #E0E0E0;
                border-color: #555555;
            }
            .stSelectbox select {
                background-color: #3D3D3D;
                color: #E0E0E0;
            }
            .stButton button {
                background-color: #4A4A4A;
                color: #E0E0E0;
                border-color: #666666;
            }
            .stButton button:hover {
                background-color: #5A5A5A;
                border-color: #777777;
            }
            div[data-testid="stMetricValue"] {
                color: #E0E0E0;
            }
            </style>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Show Tutorial Button (NEW)
    if st.button("📖 Show Tutorial", use_container_width=True):
        # Reset onboarding to show again
        if 'onboarding_completed' in st.session_state:
            del st.session_state.onboarding_completed
        if 'onboarding_step' in st.session_state:
            del st.session_state.onboarding_step
        st.success("Tutorial will appear on next page!")
        st.rerun()
    
    st.markdown("---")
    
    # Logout button
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        st.session_state.username = None
        st.session_state.full_name = None
        st.session_state.dark_mode = False
        if 'onboarding_completed' in st.session_state:
            del st.session_state.onboarding_completed
        st.rerun()
    
    st.markdown("---")
    
    # Footer info
    st.caption("💰 Your personal finance data")
    st.caption("🔒 Private & Secure")
    st.caption("📊 Real-time insights")

# Show onboarding tutorial for first-time users (NEW)
# CORRECTED: Changed from onboarding to boarding
from boarding import show_onboarding_tutorial

if 'onboarding_completed' not in st.session_state:
    # Show tutorial
    tutorial_completed = show_onboarding_tutorial()
    if not tutorial_completed:
        st.stop()  # Stop until tutorial is completed or skipped

# Run the selected page
pg.run()
