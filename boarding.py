# onboarding.py - Welcome Tutorial for New Users
import streamlit as st

def show_onboarding_tutorial():
    """
    Display interactive onboarding tutorial for new users.
    Call this function from App.py after successful login.
    """
    
    # Initialize session state for onboarding
    if 'onboarding_completed' not in st.session_state:
        st.session_state.onboarding_completed = False
    
    if 'onboarding_step' not in st.session_state:
        st.session_state.onboarding_step = 0
    
    # Don't show if already completed
    if st.session_state.onboarding_completed:
        return False
    
    # Tutorial steps content
    steps = [
        {
            "title": "👋 Welcome to BudgetBuddy!",
            "emoji": "🎉",
            "content": """
            ### Your Personal Finance Companion
            
            **Congratulations on taking control of your finances!**
            
            BudgetBuddy helps you:
            - 💵 **Track Income & Expenses** - Know where your money goes
            - 🎯 **Set Savings Goals** - Achieve your financial dreams
            - 💰 **Manage Budgets** - Never overspend again
            - 🔁 **Auto-add Recurring Transactions** - Save time on repetitive tasks
            - 📊 **Visualize Spending** - Beautiful charts and insights
            
            Let's take a quick 2-minute tour to get you started! 🚀
            """,
            "tips": [
                "✅ This tutorial appears only once",
                "✅ You can skip anytime",
                "✅ Takes less than 2 minutes"
            ]
        },
        {
            "title": "🔒 Your Data is 100% Secure",
            "emoji": "🔐",
            "content": """
            ### Bank-Level Security
            
            **We take your privacy seriously!**
            
            **Your Security Features:**
            - 🔐 **Password Encryption**: SHA-256 + unique salt
            - 🔐 **Email Encryption**: SHA-256 hashing
            - 🔐 **Username Encryption**: SHA-256 hashing
            - ⏱️ **Auto-logout**: After 30 minutes of inactivity
            - 🚫 **Rate Limiting**: 5 login attempts per 15 minutes
            - 💾 **Local Storage**: Your data stays on your device
            
            **Important to Remember:**
            """,
            "tips": [
                "📝 **Save your username** - You'll need it to login",
                "🔑 **Choose a strong password** - At least 6 characters",
                "🔄 **Reset password anytime** - Use username + email verification"
            ]
        },
        {
            "title": "💰 Track Your Money",
            "emoji": "💵",
            "content": """
            ### Core Features Overview
            
            **1. Income Monitoring** 💵
            - Add salary, freelance income, business revenue
            - Categorize income sources
            - See total monthly income
            
            **2. Expense Tracking** 💳
            - Log daily expenses (food, transport, shopping)
            - Categorize spending
            - Track where money goes
            
            **3. Savings Goals** 🎯
            - Set target amounts (vacation, gadget, emergency fund)
            - Track progress with visual indicators
            - Add/withdraw money anytime
            
            **4. Data Visualizations** 📊
            - Pie charts, bar charts, line graphs
            - Spending trends over time
            - Category-wise breakdowns
            """,
            "tips": [
                "💡 Start by adding your monthly salary",
                "💡 Log expenses daily for accuracy",
                "💡 Set at least one savings goal"
            ]
        },
        {
            "title": "🔁 NEW: Advanced Features",
            "emoji": "⚡",
            "content": """
            ### Smart Automation & Budget Control
            
            **Recurring Transactions** 🔁
            - **Auto-add monthly salary** - Never forget to log income
            - **Auto-track rent/subscriptions** - Netflix, Spotify, etc.
            - **Custom frequencies** - Daily, weekly, monthly, yearly
            - **Upcoming view** - See what's coming in next 7 days
            
            **Budget Limits** 💰
            - **Set spending limits** - ₹10K for food, ₹5K for transport
            - **Real-time alerts** - At 50%, 75%, 90%, 100%
            - **Color-coded status** - Green (safe), Yellow (warning), Red (exceeded)
            - **Monthly reset** - Fresh start every month
            
            **Dark Mode** 🌙
            - Easy on the eyes at night
            - Toggle anytime from sidebar
            """,
            "tips": [
                "⚡ Set up recurring salary first",
                "⚡ Add budget limits for top 3 categories",
                "⚡ Enable dark mode if you prefer"
            ]
        },
        {
            "title": "📱 Quick Start Guide",
            "emoji": "🚀",
            "content": """
            ### Get Started in 5 Steps
            
            **Step 1: Add Your Income** 💵
            - Go to "Income Monitoring"
            - Add your monthly salary
            - Set as recurring (optional)
            
            **Step 2: Set a Savings Goal** 🎯
            - Go to "Savings Goal"
            - Create your first goal (e.g., Emergency Fund)
            - Set target amount
            
            **Step 3: Log Your Expenses** 💳
            - Go to "Expense Tracking"
            - Add today's expenses
            - Categorize properly
            
            **Step 4: Set Budget Limits** 💰
            - Go to "Budget Manager"
            - Set limits for Food, Transport, etc.
            - Enable 75%, 90% alerts
            
            **Step 5: Add Recurring Transactions** 🔁
            - Go to "Recurring Transactions"
            - Add monthly rent, subscriptions
            - Never forget again!
            """,
            "tips": [
                "📌 Do these 5 steps now (takes 5 minutes)",
                "📌 Check dashboard daily for updates",
                "📌 Review budgets weekly"
            ]
        },
        {
            "title": "🎓 Pro Tips & Best Practices",
            "emoji": "💡",
            "content": """
            ### Master BudgetBuddy Like a Pro
            
            **Daily Habits:**
            - 📝 Log expenses immediately (don't wait)
            - 📊 Check dashboard every morning
            - 🎯 Update savings goal progress weekly
            
            **Weekly Reviews:**
            - 📈 Review spending trends
            - 💰 Check budget alerts
            - 🔁 Verify recurring transactions processed
            
            **Monthly Tasks:**
            - 🔄 Adjust budget limits if needed
            - 📊 Export data for records (CSV)
            - 🎯 Set new savings goals
            
            **Need Help?**
            - 💬 Every page has helpful tips
            - 📖 Expand info sections (ℹ️ icons)
            - 🔑 Use "Forgot Password" if needed
            """,
            "tips": [
                "🌟 Consistency is key - log daily!",
                "🌟 Review weekly for best results",
                "🌟 Celebrate when you achieve goals!"
            ]
        },
        {
            "title": "🎉 You're All Set!",
            "emoji": "✅",
            "content": """
            ### Ready to Start Your Financial Journey
            
            **You've Learned:**
            - ✅ How to track income and expenses
            - ✅ Setting up savings goals
            - ✅ Using budget limits with alerts
            - ✅ Auto-adding recurring transactions
            - ✅ Best practices for success
            
            **Remember:**
            - 🔐 Your data is secure and encrypted
            - 💾 Everything is saved automatically
            - 🔄 You can edit/delete anything anytime
            - 📊 Check visualizations for insights
            
            **Quick Access Guide:**
            - 📂 **Sidebar**: Navigate between pages
            - 🏠 **Home**: Overview dashboard
            - 💵 **Income**: Add salary, earnings
            - 💳 **Expenses**: Log spending
            - 🎯 **Goals**: Track savings
            - 💰 **Budget**: Set limits
            - 🔁 **Recurring**: Auto-transactions
            - 📊 **Visualizations**: Charts & graphs
            
            **Let's build your financial future together!** 💪
            """,
            "tips": [
                "🎯 Start with Step 1: Add your salary",
                "🎯 Set one goal today",
                "🎯 Enable dark mode if you like"
            ]
        }
    ]
    
    # Get current step
    current_step = st.session_state.onboarding_step
    step = steps[current_step]
    
    # Create centered container with custom styling
    st.markdown("""
        <style>
        .onboarding-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .onboarding-content {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .emoji-large {
            font-size: 64px;
            text-align: center;
            margin: 20px 0;
        }
        .tip-box {
            background: #E6F3FF;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #4169E1;
            margin: 10px 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Display step content
    with st.container():
        # Large emoji
        st.markdown(f'<div class="emoji-large">{step["emoji"]}</div>', unsafe_allow_html=True)
        
        # Title
        st.markdown(f"## {step['title']}")
        
        # Progress indicator
        progress = (current_step + 1) / len(steps)
        st.progress(progress)
        st.caption(f"Step {current_step + 1} of {len(steps)}")
        
        st.markdown("---")
        
        # Main content
        st.markdown(step["content"])
        
        # Tips section
        if step["tips"]:
            st.markdown("### 💡 Quick Tips:")
            for tip in step["tips"]:
                st.markdown(f"- {tip}")
        
        st.markdown("---")
        
        # Navigation buttons
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        
        with col1:
            if current_step > 0:
                if st.button("⬅️ Back", use_container_width=True):
                    st.session_state.onboarding_step -= 1
                    st.rerun()
        
        with col2:
            if st.button("⏭️ Skip Tutorial", use_container_width=True, type="secondary"):
                st.session_state.onboarding_completed = True
                st.info("✅ Tutorial skipped! You can explore on your own.")
                st.balloons()
                return True
        
        with col3:
            # Restart button
            if current_step > 0:
                if st.button("🔄 Restart", use_container_width=True):
                    st.session_state.onboarding_step = 0
                    st.rerun()
        
        with col4:
            if current_step < len(steps) - 1:
                if st.button("Next ➡️", use_container_width=True, type="primary"):
                    st.session_state.onboarding_step += 1
                    st.rerun()
            else:
                if st.button("🎉 Get Started!", use_container_width=True, type="primary"):
                    st.session_state.onboarding_completed = True
                    st.success("🎉 Tutorial completed! Welcome to BudgetBuddy!")
                    st.balloons()
                    return True
    
    return False


# Alternative: Modal-style onboarding (shows on first login)
def show_onboarding_modal():
    """
    Show onboarding as a modal/popup.
    Use this instead of show_onboarding_tutorial() if you prefer modal style.
    """
    
    # Check if user has seen onboarding
    if 'first_login' not in st.session_state:
        st.session_state.first_login = True
    
    if not st.session_state.first_login:
        return
    
    # Show welcome modal
    with st.expander("👋 Welcome to BudgetBuddy! Click to start tutorial", expanded=True):
        st.markdown("""
        ### Hi there! 🎉
        
        Welcome to your new financial companion!
        
        **Quick Tour (2 minutes):**
        - Learn how to track income & expenses
        - Set up savings goals
        - Use budget limits & alerts
        - Auto-add recurring transactions
        
        Click **"Start Tour"** below or **"Skip"** to explore on your own.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Start Tour", use_container_width=True, type="primary"):
                show_onboarding_tutorial()
        
        with col2:
            if st.button("⏭️ Skip for Now", use_container_width=True):
                st.session_state.first_login = False
                st.rerun()


# Function to reset onboarding (for testing or re-showing)
def reset_onboarding():
    """Reset onboarding state to show tutorial again"""
    if 'onboarding_completed' in st.session_state:
        del st.session_state.onboarding_completed
    if 'onboarding_step' in st.session_state:
        del st.session_state.onboarding_step
    if 'first_login' in st.session_state:
        del st.session_state.first_login
