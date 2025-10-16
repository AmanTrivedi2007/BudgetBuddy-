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
