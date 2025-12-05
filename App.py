# App.py - Main Application with Onboarding Tutorial

import streamlit as st
import time
from database import init_database
from auth import check_authentication

# Initialize database FIRST
import os

# Initialize DB only if missing (do NOT recreate every run)
import os
from persistent_storage import get_db_path  # ✅ Add this import

# Initialize ONLY if missing
if not os.path.exists(get_db_path()):
    from database import init_database
    init_database()





username = check_authentication()


# Page configuration
st.set_page_config(
    page_title="BudgetBuddy - Smart Finance Manager",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check authentication FIRST
username = check_authentication()

# If not authenticated, stop here (auth.py handles login UI)
if not username or 'username' not in st.session_state:
    st.stop()

# Initialize session state variables
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# ===========================
# SHOW ONBOARDING TUTORIAL (ONLY ONCE PER USER)
# ===========================
from boarding import show_onboarding_tutorial

# Show tutorial if not completed
if show_onboarding_tutorial():
    st.stop()  # Stop here - show only tutorial, nothing else

# ===========================
# MAIN APP - Shows only after tutorial completion
# ===========================

# Define all pages
page1 = st.Page("Description.py", title="Home", icon="🏠")
page2 = st.Page("income_monitoring.py", title="Income Monitoring", icon="💵")
page3 = st.Page("expense.py", title="Expense Tracking", icon="💳")
page4 = st.Page("budget_manager.py", title="Budget Manager", icon="💰")
page5 = st.Page("recurring_transactions.py", title="Recurring Transactions", icon="🔁")
page6 = st.Page("Saving_goal.py", title="Savings Goals", icon="🎯")
page7 = st.Page("visualization.py", title="Advanced Visualizations", icon="📊")
page8 = st.Page("ai_insights.py", title="🤖 AI Insights", icon="🧠")
  

# Create navigation
pg = st.navigation(
    [page1, page2, page3, page4, page5, page6, page7,page8],
    position="sidebar"
)

# ===========================
# SIDEBAR - User Info, Settings & Controls
# ===========================
with st.sidebar:
    st.markdown("---")
    
    # User info section with profile card
    if st.session_state.get('full_name'):
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 15px; 
                    border-radius: 10px; 
                    text-align: center; 
                    color: white;
                    margin-bottom: 10px;'>
            <h3 style='margin: 0;'>👤 {st.session_state.full_name}</h3>
            <p style='margin: 5px 0 0 0; opacity: 0.9;'>@{username}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 15px; 
                    border-radius: 10px; 
                    text-align: center; 
                    color: white;
                    margin-bottom: 10px;'>
            <h3 style='margin: 0;'>👤 {username}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # LOGOUT BUTTON - Moved to top (prominent position)
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("✅ Logged out successfully!")
        time.sleep(0.5)
        st.rerun()
    
    st.markdown("---")
    
    # Settings Section
    st.markdown("### ⚙️ Settings")
    
    # Dark Mode Toggle
    dark_mode = st.toggle(
        "🌙 Dark Mode",
        value=st.session_state.dark_mode,
        help="Toggle between dark and light theme"
    )
    
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.rerun()
    
    # Apply dark mode CSS
    if st.session_state.dark_mode:
        st.markdown("""
        <style>
            .stApp {
                background-color: #0e1117;
                color: #fafafa;
            }
            .stSidebar {
                background-color: #262730;
            }
            .stMarkdown, .stText {
                color: #fafafa;
            }
            div[data-testid="stMetricValue"] {
                color: #fafafa;
            }
            .stButton button {
                background-color: #1f2937;
                color: #fafafa;
            }
            .stButton button:hover {
                background-color: #374151;
            }
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tutorial & Help Section
    st.markdown("### 📚 Help & Tutorials")
    
    # Restart Tutorial Button
    if st.button("📖 Restart Tutorial", use_container_width=True):
        from boarding import reset_onboarding
        reset_onboarding()
        st.success("✅ Tutorial reset! Reloading...")
        time.sleep(0.5)
        st.rerun()
    
    # Quick Tips Expander
    with st.expander("💡 Quick Tips", expanded=False):
        st.markdown("""
        **Daily Habits:**
        - 📝 Log expenses immediately
        - 📊 Check dashboard every morning
        - 🎯 Update savings progress
        
        **Weekly Reviews:**
        - 📈 Review spending trends
        - 💰 Check budget alerts
        - 🔁 Verify recurring transactions
        
        **Monthly Tasks:**
        - 🔄 Adjust budget limits
        - 📥 Export data for records
        - 🎯 Set new savings goals
        
        **Pro Tips:**
        - ✨ Use filters for detailed analysis
        - ✨ Hover over charts for insights
        - ✨ Set budget alerts at 75% & 90%
        """)
    
    st.markdown("---")
    
    # App Info & Version
    st.markdown("### ℹ️ App Info")
    
    col1, col2 = st.columns(2)
    with col1:
        st.caption("💰 **BudgetBuddy**")
        st.caption("📊 **Version 3.0**")
    with col2:
        st.caption("🔒 **Secure**")
        st.caption("🌐 **2025 Edition**")
    
    st.markdown("---")
    
    # Feature badges
    st.markdown("""
    <div style='text-align: center; padding: 10px;'>
        <span style='background: #2ecc71; color: white; padding: 5px 10px; border-radius: 15px; font-size: 0.75em; margin: 2px;'>✅ Real-time Analytics</span><br>
        <span style='background: #3498db; color: white; padding: 5px 10px; border-radius: 15px; font-size: 0.75em; margin: 2px;'>📊 20+ Charts</span><br>
        <span style='background: #e74c3c; color: white; padding: 5px 10px; border-radius: 15px; font-size: 0.75em; margin: 2px;'>🔐 Encrypted</span><br>
        <span style='background: #f39c12; color: white; padding: 5px 10px; border-radius: 15px; font-size: 0.75em; margin: 2px;'>💡 AI Insights</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Footer with copyright
    st.markdown("""
    <div style='text-align: center; padding: 10px; color: #666; font-size: 0.85em;'>
        <p style='margin: 2px;'>Made with ❤️ using Streamlit</p>
        <p style='margin: 2px;'>© 2025 BudgetBuddy</p>
        <p style='margin: 2px;'>Your financial companion</p>
    </div>
    """, unsafe_allow_html=True)

# Run the selected page
pg.run()
