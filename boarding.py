# boarding.py - FINAL VERSION WITH DATABASE PERSISTENCE

import streamlit as st
import time
from database import save_user_preference, get_user_preference, delete_user_preference

# Callback functions for navigation (These run BEFORE the page renders)
def next_step():
    """Increment step counter"""
    st.session_state.onboarding_step += 1

def prev_step():
    """Decrement step counter"""
    st.session_state.onboarding_step -= 1

def skip_tutorial():
    """Skip and complete tutorial - saves to database"""
    # Save to database for persistence
    if 'username' in st.session_state:
        save_user_preference(st.session_state.username, 'onboarding_completed', 'true')
    
    st.session_state.onboarding_completed = True
    st.session_state.onboarding_step = 0

def finish_tutorial():
    """Complete the tutorial - saves to database"""
    # Save to database for persistence
    if 'username' in st.session_state:
        save_user_preference(st.session_state.username, 'onboarding_completed', 'true')
    
    st.session_state.onboarding_completed = True
    st.session_state.onboarding_step = 0
    st.session_state.show_completion = True

def show_onboarding_tutorial():
    """
    Display interactive onboarding tutorial for new users.
    Checks database for completion status - shows only once per user.
    
    Returns:
        bool: True if showing tutorial, False if completed
    """
    # Check if user is logged in
    if 'username' not in st.session_state:
        return False
    
    username = st.session_state.username
    
    # Check database for tutorial completion status
    tutorial_completed_db = get_user_preference(username, 'onboarding_completed', 'false')
    
    # Initialize session state from database
    if 'onboarding_completed' not in st.session_state:
        st.session_state.onboarding_completed = (tutorial_completed_db == 'true')
    
    if 'onboarding_step' not in st.session_state:
        st.session_state.onboarding_step = 0
    
    if 'show_completion' not in st.session_state:
        st.session_state.show_completion = False
    
    # Show completion message if just finished
    if st.session_state.show_completion:
        st.balloons()
        st.success("🎊 **Tutorial Completed!** Welcome to BudgetBuddy!")
        time.sleep(2)
        st.session_state.show_completion = False
        st.rerun()
    
    # Don't show if already completed (from database)
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
- 📊 **Visualize Spending** - Beautiful interactive charts and insights

Let's take a quick 2-minute tour to get you started! 🚀
            """,
            "tips": [
                "✅ This tutorial appears only once per account",
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
- Interactive Plotly charts with hover details
- 20+ chart types (donut, treemap, waterfall, heatmap)
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
            "title": "🔁 Advanced Features",
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

**Interactive Visualizations** 📊
- **20+ Chart Types** - Donut, treemap, waterfall, Sankey, heatmaps
- **Hover Tooltips** - Detailed information on hover
- **Zoom & Pan** - Interactive chart exploration
- **Financial Health Score** - 100-point rating system
            """,
            "tips": [
                "⚡ Set up recurring salary first",
                "⚡ Add budget limits for top 3 categories",
                "⚡ Explore the advanced visualization dashboard"
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

**Step 5: Explore Visualizations** 📊
- Go to "Advanced Visualization"
- View interactive charts
- Check your Financial Health Score
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
- ✅ Exploring interactive visualizations
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
- 📊 **Visualizations**: Interactive charts & health score

**Let's build your financial future together!** 💪
            """,
            "tips": [
                "🎯 Start with Step 1: Add your salary",
                "🎯 Set one goal today",
                "🎯 Explore the visualization dashboard"
            ]
        }
    ]
    
    # Get current step
    current_step = st.session_state.onboarding_step
    
    # Safety check: prevent out of bounds
    if current_step >= len(steps):
        finish_tutorial()
        return False
    
    step = steps[current_step]
    total_steps = len(steps)
    
    # Custom CSS for styling
    st.markdown("""
    <style>
        .emoji-display {
            font-size: 80px;
            text-align: center;
            margin: 20px 0;
            animation: bounce 2s ease infinite;
        }
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        .step-title {
            text-align: center;
            font-size: 2.5em;
            margin: 20px 0;
            color: #667eea;
            font-weight: bold;
        }
        .content-box {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
        }
        .tips-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            margin: 20px 0;
        }
        .progress-bar {
            background: #e0e0e0;
            height: 10px;
            border-radius: 5px;
            margin: 30px 0;
            overflow: hidden;
        }
        .progress-fill {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            height: 100%;
            transition: width 0.5s ease;
        }
        .step-counter {
            text-align: center;
            color: #666;
            font-size: 1.2em;
            margin: 10px 0;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Display step content
    with st.container():
        # Progress bar
        progress = ((current_step + 1) / total_steps) * 100
        st.markdown(f"""
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress}%;"></div>
        </div>
        <div class="step-counter">Step {current_step + 1} of {total_steps}</div>
        """, unsafe_allow_html=True)
        
        # Large emoji
        st.markdown(f'<div class="emoji-display">{step["emoji"]}</div>', unsafe_allow_html=True)
        
        # Title
        st.markdown(f'<h1 class="step-title">{step["title"]}</h1>', unsafe_allow_html=True)
        
        # Content
        st.markdown(f'<div class="content-box">{step["content"]}</div>', unsafe_allow_html=True)
        
        # Tips section
        if step["tips"]:
            st.markdown('<div class="tips-box">', unsafe_allow_html=True)
            st.markdown("### 💡 Quick Tips:")
            for tip in step["tips"]:
                st.markdown(f"- {tip}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation buttons with CALLBACKS (this prevents step skipping!)
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if current_step > 0:
                st.button(
                    "⬅️ Previous", 
                    key=f"prev_{current_step}",
                    on_click=prev_step,  # Callback ensures clean state update
                    use_container_width=True,
                    type="secondary"
                )
            else:
                st.empty()  # Placeholder to maintain layout
        
        with col2:
            st.button(
                "⏭️ Skip Tutorial", 
                key=f"skip_{current_step}",
                on_click=skip_tutorial,  # Callback with database save
                use_container_width=True,
                type="secondary"
            )
        
        with col3:
            if current_step < total_steps - 1:
                st.button(
                    "Next ➡️", 
                    key=f"next_{current_step}",
                    on_click=next_step,  # Callback ensures clean state update
                    use_container_width=True,
                    type="primary"
                )
            else:
                st.button(
                    "🎉 Get Started!", 
                    key=f"finish_{current_step}",
                    on_click=finish_tutorial,  # Callback with database save
                    use_container_width=True,
                    type="primary"
                )
    
    return True


# Function to reset onboarding (for testing/manual reset)
def reset_onboarding():
    """Reset onboarding - deletes from database and session state"""
    if 'username' in st.session_state:
        delete_user_preference(st.session_state.username, 'onboarding_completed')
    
    st.session_state.onboarding_completed = False
    st.session_state.onboarding_step = 0
    if 'show_completion' in st.session_state:
        del st.session_state.show_completion
