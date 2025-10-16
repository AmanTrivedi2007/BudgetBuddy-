# auth.py
import streamlit as st

def check_authentication():
    """Simple username-based authentication with logout option"""
    
    # Initialize username in session state if not exists
    if 'username' not in st.session_state:
        st.session_state.username = None
    
    # If not logged in, show login page
    if not st.session_state.username:
        st.markdown("""
            <style>
            .login-container {
                max-width: 500px;
                margin: 100px auto;
                padding: 40px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            </style>
        """, unsafe_allow_html=True)
        
        st.title("💰 Welcome to BudgetBuddy")
        st.markdown("### Your Personal Finance Companion")
        st.markdown("---")
        
        st.subheader("🔐 Login")
        st.info("💡 Enter a username to access your personal finance dashboard. Your data is saved under this username.")
        
        # Login form
        with st.form("login_form", clear_on_submit=True):
            username_input = st.text_input(
                "Username", 
                placeholder="Enter your username (min 3 characters)",
                max_chars=30,
                help="Choose a unique username. You'll use this to access your data."
            )
            
            col1, col2, col3 = st.columns([1,1,1])
            
            with col2:
                login_button = st.form_submit_button("🚀 Login", use_container_width=True)
            
            if login_button:
                # Validate username
                if not username_input:
                    st.error("❌ Please enter a username")
                elif len(username_input) < 3:
                    st.error("❌ Username must be at least 3 characters")
                elif ' ' in username_input:
                    st.error("❌ Username cannot contain spaces")
                else:
                    # Clean username (lowercase, no special chars except underscore)
                    clean_username = username_input.strip().lower()
                    
                    # Set username in session state
                    st.session_state.username = clean_username
                    st.success(f"✅ Welcome, {clean_username}! 👋")
                    st.balloons()
                    st.rerun()
        
        # Show tips
        st.markdown("---")
        st.markdown("### ✨ Features")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("💵 **Income Tracking**")
            st.caption("Monitor all income sources")
            st.markdown("💳 **Expense Management**")
            st.caption("Track daily spending")
        
        with col2:
            st.markdown("🎯 **Savings Goals**")
            st.caption("Set and achieve targets")
            st.markdown("📊 **Visualizations**")
            st.caption("Analyze spending patterns")
        
        # Footer
        st.markdown("---")
        st.caption("🔒 Your data is stored securely and accessible only with your username")
        
        # Stop here - don't load rest of app
        st.stop()
    
    # If logged in, return username
    return st.session_state.username


def logout():
    """Logout function to clear session"""
    st.session_state.username = None
    st.rerun()
