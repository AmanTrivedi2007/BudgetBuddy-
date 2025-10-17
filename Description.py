# about.py
import streamlit as st

# Page configuration
st.set_page_config(page_title="About - Finance Tracker", page_icon="💰", layout="wide")

# Header section
st.title("💰 Personal Finance Tracker")
st.markdown("### Your All-in-One Financial Management Solution")
st.markdown("---")

# Introduction
st.write("""
Welcome to your Personal Finance Tracker! This comprehensive application helps you take control 
of your finances with powerful tools for tracking, analyzing, and planning your financial future.
""")

st.markdown("---")

# Features section with columns
st.header("✨ Key Features")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Expense Tracking")
    st.write("""
    - Record daily expenses with categories
    - Track spending patterns over time
    - Add notes and descriptions to transactions
    - Categorize expenses for better insights
    """)
    
    st.subheader("💵 Income Monitoring")
    st.write("""
    - Log multiple income sources
    - Track salary, freelance, and passive income
    - Monitor income trends monthly/yearly
    - Calculate total earnings automatically
    """)
    
    st.subheader("🎯 Saving Goals")
    st.write("""
    - Set and track multiple saving goals
    - Visual progress indicators
    - Calculate time to reach goals
    - Get motivational insights
    """)

with col2:
    st.subheader("📈 Spending Visualization")
    st.write("""
    - Interactive charts and graphs
    - Category-wise spending breakdown
    - Monthly comparison reports
    - Identify spending trends
    """)
    
    st.subheader("💼 Budgeting Tools")
    st.write("""
    - Create custom budgets by category
    - Track budget vs actual spending
    - Get alerts for overspending
    - Smart budget recommendations
    """)
    
    st.subheader("📱 User-Friendly Interface")
    st.write("""
    - Clean and intuitive design
    - Easy navigation between features
    - Real-time data updates
    - Responsive layout for all devices
    """)

st.markdown("---")

# How it works section
st.header("🚀 How It Works")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 1️⃣ Track")
    st.info("Record your income and expenses as they happen. Categorize transactions for better organization.")

with col2:
    st.markdown("#### 2️⃣ Analyze")
    st.info("View detailed visualizations and reports to understand your spending patterns and habits.")

with col3:
    st.markdown("#### 3️⃣ Plan")
    st.info("Set budgets and savings goals. Get insights to make smarter financial decisions.")

st.markdown("---")

# Benefits section
st.header("🌟 Benefits")

benefits = {
    "Financial Awareness": "Understand exactly where your money goes each month",
    "Better Decisions": "Make informed financial choices based on real data",
    "Goal Achievement": "Stay motivated and on track to reach your savings targets",
    "Stress Reduction": "Feel confident about your financial situation",
    "Time Saving": "Automated calculations and reports save you hours"
}

for benefit, description in benefits.items():
    with st.expander(f"✅ {benefit}"):
        st.write(description)

st.markdown("---")

# Technology section
st.header("🔧 Built With")

tech_col1, tech_col2, tech_col3 = st.columns(3)

with tech_col1:
    st.markdown("**Frontend**")
    st.write("- Streamlit")
    st.write("- Python")

with tech_col2:
    st.markdown("**Data Processing**")
    st.write("- Pandas")
    st.write("- NumPy")

with tech_col3:
    st.markdown("**Visualization**")
    st.write("- Plotly")
    st.write("- Matplotlib")

st.markdown("---")

# Getting started section
st.header("🎯 Getting Started")

st.write("""
1. **Navigate** to Income Monitoring to add your income sources
2. **Record** your daily expenses in Expense Tracking
3. **Set** your savings goals in the Saving Goals section
4. **Create** budgets using the Budgeting Tools
5. **Analyze** your financial health with Spending Visualization
""")

st.markdown("---")

# Footer
st.success("💡 **Pro Tip:** Use this app daily for the best results! Consistent tracking leads to better financial insights.")

st.info("📧 For questions or feedback, feel free to reach out!")

# Statistics (optional - can be made dynamic)
st.markdown("---")
st.header("📊 App Statistics")

stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

with stat_col1:
    st.metric("Features", "5", delta="Complete")
    
with stat_col2:
    st.metric("Categories", "10+", delta="Customizable")
    
with stat_col3:
    st.metric("Charts", "Multiple", delta="Interactive")
    
with stat_col4:
    st.metric("Export", "CSV/Excel", delta="Available")
# Description.py
import streamlit as st

# Custom CSS for better styling
st.markdown("""
    <style>
    .big-font {
        font-size: 60px !important;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }
    .subtitle {
        text-align: center;
        font-size: 24px;
        color: #666;
        margin-bottom: 40px;
    }
    .feature-box {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin-bottom: 20px;
    }
    .version-badge {
        display: inline-block;
        padding: 5px 15px;
        background: #667eea;
        color: white;
        border-radius: 20px;
        font-size: 14px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Header with animation
st.markdown('<p class="big-font">💰 BudgetBuddy</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Your Personal Finance Companion</p>', unsafe_allow_html=True)

# Version badge
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.markdown('<center><span class="version-badge">Version 2.0 - Secure Login Edition</span></center>', unsafe_allow_html=True)

st.markdown("---")

# Welcome message with emoji
st.markdown("""
## 🎉 Welcome to BudgetBuddy!

Take complete control of your finances with our comprehensive financial management application. 
Track income, manage expenses, achieve savings goals, and visualize your spending patterns—all in one secure, 
user-friendly platform designed specifically for your success.
""")

st.markdown("---")

# Key Features Section with enhanced design
st.header("✨ Powerful Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-box">
        <h3>💵 Income Monitoring</h3>
        <p>Track all your income sources efficiently:</p>
        <ul>
            <li>📊 Log salary, freelance, and passive income</li>
            <li>📈 Monitor income trends over time</li>
            <li>💼 Multiple income source management</li>
            <li>📥 Export income reports as CSV</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-box">
        <h3>🎯 Savings Goals</h3>
        <p>Achieve your financial dreams:</p>
        <ul>
            <li>🎪 Create unlimited savings goals</li>
            <li>📊 Visual progress tracking</li>
            <li>💰 Automatic balance deduction</li>
            <li>📝 Transaction history for each goal</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-box">
        <h3>🔒 Secure Authentication</h3>
        <p>Your data is protected:</p>
        <ul>
            <li>🔐 SHA-256 password encryption</li>
            <li>👤 Unique username generation</li>
            <li>🛡️ Personal data isolation</li>
            <li>🔑 Secure login system</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-box">
        <h3>💳 Expense Tracking</h3>
        <p>Never lose track of spending:</p>
        <ul>
            <li>🏷️ 8+ expense categories</li>
            <li>⚠️ Overspending prevention</li>
            <li>📊 Real-time balance updates</li>
            <li>🔍 Filter and sort transactions</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-box">
        <h3>📊 Visual Analytics</h3>
        <p>Understand your finances at a glance:</p>
        <ul>
            <li>🍰 Pie charts for category breakdown</li>
            <li>📈 Line charts for spending trends</li>
            <li>🔥 Heatmaps for monthly analysis</li>
            <li>💯 Financial health score</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-box">
        <h3>📱 User Experience</h3>
        <p>Designed for simplicity:</p>
        <ul>
            <li>🎨 Clean, modern interface</li>
            <li>⚡ Fast and responsive</li>
            <li>📱 Works on all devices</li>
            <li>🌐 No installation required</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# How It Works - Interactive
st.header("🚀 How It Works")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["1️⃣ Sign Up", "2️⃣ Track Income", "3️⃣ Manage Expenses", "4️⃣ Set Goals", "5️⃣ Analyze Data"])

with tab1:
    st.markdown("""
    ### 📝 Create Your Account
    
    **Getting started is easy:**
    1. Click on **Sign Up** button
    2. Enter your full name (e.g., "Rahul Kumar")
    3. System generates unique username (e.g., "rahulk")
    4. Set a secure password (minimum 6 characters)
    5. Remember your username for future logins
    
    ✅ **Pro Tip:** Write down your username immediately after signup!
    """)
    st.success("✨ Your data is encrypted and secure from day one!")

with tab2:
    st.markdown("""
    ### 💵 Monitor Your Income
    
    **Add all income sources:**
    1. Navigate to **Income Monitoring** page
    2. Click **Add New Income** button
    3. Select source (Salary, Freelance, Business, etc.)
    4. Enter amount and date
    5. Add optional notes
    
    📊 **Features:**
    - View total income instantly
    - Download income reports
    - Track income trends
    - Manage multiple sources
    """)
    st.info("💡 Regular tracking helps you understand your earning patterns!")

with tab3:
    st.markdown("""
    ### 💳 Track Your Expenses
    
    **Stay on top of spending:**
    1. Go to **Expense Tracking** page
    2. Add expense with category
    3. System checks available balance
    4. Prevents overspending automatically
    5. View spending by category
    
    🔍 **Smart Features:**
    - Balance validation before spending
    - Category-wise breakdown
    - Filter and sort options
    - Monthly spending reports
    """)
    st.warning("⚠️ App prevents you from spending more than you have!")

with tab4:
    st.markdown("""
    ### 🎯 Achieve Your Goals
    
    **Make dreams reality:**
    1. Visit **Saving Goals** page
    2. Create goal (e.g., "New Laptop - ₹60,000")
    3. Add money from available balance
    4. Track progress with visual bars
    5. Withdraw if needed
    
    🎪 **Goal Management:**
    - Multiple goals support
    - Progress tracking
    - Transaction history
    - Goal completion alerts
    """)
    st.success("🎉 Stay motivated watching your progress!")

with tab5:
    st.markdown("""
    ### 📊 Visualize Your Finances
    
    **Make data-driven decisions:**
    1. Check **Spending Visualization** page
    2. View pie charts, bar graphs
    3. Analyze spending trends
    4. Monitor financial health score
    5. Export data as CSV
    
    📈 **Analytics Include:**
    - Category distribution
    - Monthly comparisons
    - Income vs expense trends
    - Financial health rating (0-100)
    """)
    st.info("📊 Data visualization helps spot patterns and save money!")

st.markdown("---")

# Benefits Section with metrics
st.header("🌟 Why Choose BudgetBuddy?")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("⚡ Speed", "Instant", delta="Real-time updates")
with col2:
    st.metric("🔒 Security", "SHA-256", delta="Bank-level encryption")
with col3:
    st.metric("📱 Access", "Anywhere", delta="Cloud-based")
with col4:
    st.metric("💰 Cost", "Free", delta="Always free")

st.markdown("---")

# Benefits expandable
benefits = {
    "💡 Financial Awareness": "Understand exactly where your money goes each month with detailed breakdowns and insights.",
    "🎯 Goal Achievement": "Stay motivated and on track to reach your savings targets with visual progress tracking.",
    "⚠️ Overspending Prevention": "Never spend more than you have. App validates balance before every transaction.",
    "📊 Data-Driven Decisions": "Make informed financial choices based on real data, not guesswork.",
    "⏱️ Time Saving": "Automated calculations save hours of manual tracking and Excel sheets.",
    "🔒 Privacy Protection": "Each user has isolated data. Your finances stay private and secure.",
    "📈 Trend Analysis": "Identify spending patterns and adjust habits for better financial health.",
    "🎉 Motivation Boost": "Celebrate goal completions and track financial progress visually."
}

st.subheader("✅ Key Benefits")
cols = st.columns(2)
for idx, (benefit, description) in enumerate(benefits.items()):
    with cols[idx % 2]:
        with st.expander(benefit):
            st.write(description)

st.markdown("---")

# Tech Stack
st.header("🛠️ Technology Stack")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("**🎨 Frontend**")
    st.write("• Streamlit")
    st.write("• Python 3.13")
    st.write("• Custom CSS")

with col2:
    st.markdown("**📊 Visualization**")
    st.write("• Matplotlib")
    st.write("• Seaborn")
    st.write("• Pandas")

with col3:
    st.markdown("**💾 Database**")
    st.write("• SQLite")
    st.write("• SQL")
    st.write("• Relational DB")

with col4:
    st.markdown("**🔐 Security**")
    st.write("• SHA-256")
    st.write("• Salt Hashing")
    st.write("• Encryption")

st.markdown("---")

# Pro Tips Section
st.header("💡 Pro Tips for Success")

tip_col1, tip_col2 = st.columns(2)

with tip_col1:
    st.success("""
    **📝 Daily Habits:**
    - Track expenses as they happen
    - Review spending every evening
    - Update goals weekly
    - Set alerts for overspending
    """)

with tip_col2:
    st.info("""
    **🎯 Best Practices:**
    - Keep emergency fund (3-6 months)
    - Don't spend >70% of income
    - Save 20% minimum monthly
    - Invest remaining wisely
    """)

st.markdown("---")

# Statistics
st.header("📊 App Features Overview")

feat_col1, feat_col2, feat_col3, feat_col4 = st.columns(4)

with feat_col1:
    st.metric("Core Pages", "5", help="Income, Expense, Goals, Visualization, About")
with feat_col2:
    st.metric("Expense Categories", "8+", help="Food, Transport, Bills, Entertainment, etc.")
with feat_col3:
    st.metric("Chart Types", "7+", help="Pie, Bar, Line, Heatmap, Progress, etc.")
with feat_col4:
    st.metric("Export Formats", "CSV", help="Download all data as CSV files")

st.markdown("---")

# Version History
with st.expander("📜 Version History"):
    st.markdown("""
    **Version 2.0 (Current)** - October 2025
    - ✅ Added secure login with SHA-256 encryption
    - ✅ Unique username generation system
    - ✅ Multi-user support with data isolation
    - ✅ Enhanced UI/UX design
    
    **Version 1.0** - October 2025
    - ✅ Basic income tracking
    - ✅ Expense management
    - ✅ Savings goals
    - ✅ Data visualization
    - ✅ Balance validation
    """)

st.markdown("---")

# Footer with style
st.markdown("""
    <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); border-radius: 10px;'>
        <h3>🎉 Ready to Take Control of Your Finances?</h3>
        <p style='font-size: 18px;'>Start tracking today and achieve your financial goals!</p>
        <br>
        <p style='color: #666;'>Made with ❤️ using Streamlit | Version 2.0 | © 2025 BudgetBuddy</p>
        <p style='color: #666; font-size: 12px;'>🔒 Your data is encrypted and secure</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Final call to action
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.success("💡 **Pro Tip:** Use BudgetBuddy daily for 30 days to see real financial improvements!")
