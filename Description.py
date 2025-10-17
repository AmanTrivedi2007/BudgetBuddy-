# Description.py

import streamlit as st

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
        animation: fadeIn 1s ease-in;
    }
    
    .feature-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
        border-left: 4px solid #667eea;
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    .version-badge {
        display: inline-block;
        background: #2ecc71;
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .new-feature {
        background: #ff6b6b;
        color: white;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.7em;
        margin-left: 8px;
        font-weight: bold;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# Header with animation
st.markdown('''
<div class="main-header">
    <h1 style="font-size: 3.5em; margin: 0;">💰 BudgetBuddy</h1>
    <p style="font-size: 1.4em; margin: 10px 0;">Your Advanced Personal Finance Companion</p>
    <span class="version-badge">Version 3.0 - 2025 Edition</span>
</div>
''', unsafe_allow_html=True)

# Quick Stats Overview
st.markdown("## 📊 At a Glance")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Features", "8+", delta="Complete Suite", help="Comprehensive financial management tools")
with col2:
    st.metric("Charts", "20+", delta="Interactive", help="Advanced Plotly visualizations with hover & zoom")
with col3:
    st.metric("Security", "100%", delta="Encrypted", help="Your data is protected with industry-standard encryption")
with col4:
    st.metric("Export Options", "Multiple", delta="CSV/Excel", help="Download your data anytime")

st.markdown("---")

# Introduction
st.markdown("## 🎯 Welcome to BudgetBuddy!")

st.write("""
**BudgetBuddy** is your all-in-one financial intelligence platform designed to help you take complete control 
of your finances. With cutting-edge visualizations, smart insights, and powerful tracking tools, managing 
your money has never been easier or more insightful!
""")

st.info("💡 **New in Version 3.0:** Advanced interactive dashboards with 20+ chart types, AI-powered insights, and real-time financial health scoring!")

st.markdown("---")

# Core Features - Updated with new capabilities
st.markdown("## ✨ Comprehensive Feature Suite")

# Feature tabs for better organization
tab1, tab2, tab3, tab4 = st.tabs(["💰 Tracking & Monitoring", "📊 Analytics & Insights", "🎯 Planning & Goals", "🔒 Security & Export"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('''
        <div class="feature-card">
            <h3>📊 Advanced Expense Tracking</h3>
            <ul>
                <li>✅ Record expenses with detailed categorization</li>
                <li>✅ Add custom descriptions and notes</li>
                <li>✅ Track spending patterns over time</li>
                <li>✅ Multiple category support (10+ categories)</li>
                <li>✅ Real-time expense calculations</li>
                <li>✅ Date-based filtering and search</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="feature-card">
            <h3>🔄 Recurring Transactions <span class="new-feature">NEW</span></h3>
            <ul>
                <li>✅ Set up automated recurring expenses</li>
                <li>✅ Daily, weekly, monthly, yearly frequencies</li>
                <li>✅ Never miss regular payments</li>
                <li>✅ Edit or pause recurring transactions</li>
                <li>✅ Automatic transaction generation</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown('''
        <div class="feature-card">
            <h3>💵 Income Monitoring</h3>
            <ul>
                <li>✅ Track multiple income sources</li>
                <li>✅ Salary, freelance, passive income tracking</li>
                <li>✅ Monthly/yearly income trends</li>
                <li>✅ Income diversity analysis</li>
                <li>✅ Automatic total calculations</li>
                <li>✅ Income vs expense comparisons</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="feature-card">
            <h3>📱 Smart Categories</h3>
            <ul>
                <li>✅ Pre-built expense categories</li>
                <li>✅ Customizable category system</li>
                <li>✅ Icon-based visual identification</li>
                <li>✅ Category-wise budget allocation</li>
                <li>✅ Intelligent category suggestions</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)

with tab2:
    st.markdown("### 📈 Advanced Interactive Visualizations <span class='new-feature'>UPGRADED</span>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('''
        <div class="feature-card">
            <h4>🍩 Interactive Charts</h4>
            <ul>
                <li>🎨 <b>Donut Charts</b> - Expense distribution with hover details</li>
                <li>🗺️ <b>Treemaps</b> - Hierarchical spending visualization</li>
                <li>💧 <b>Waterfall Charts</b> - Cash flow breakdown</li>
                <li>🌊 <b>Sankey Diagrams</b> - Money flow visualization</li>
                <li>📦 <b>Box Plots</b> - Expense distribution & outliers</li>
                <li>🔥 <b>Heatmaps</b> - Monthly category spending patterns</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="feature-card">
            <h4>📊 Time Series Analysis</h4>
            <ul>
                <li>📅 Daily spending trends with moving averages</li>
                <li>📈 7-day and 30-day trend analysis</li>
                <li>📆 Weekly spending patterns</li>
                <li>📊 Monthly comparison charts</li>
                <li>🔍 Interactive date range filtering</li>
                <li>📉 Spending velocity metrics</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown('''
        <div class="feature-card">
            <h4>🎯 Smart Insights <span class="new-feature">NEW</span></h4>
            <ul>
                <li>💯 <b>Financial Health Score</b> - Comprehensive rating (0-100)</li>
                <li>📊 Category-wise spending breakdown</li>
                <li>🔝 Top 10 highest expenses tracker</li>
                <li>⚡ Transaction frequency analysis</li>
                <li>⚠️ Spending alerts for over-budget categories</li>
                <li>💡 Personalized recommendations</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="feature-card">
            <h4>📉 Comparative Analysis</h4>
            <ul>
                <li>📈 Month-over-month growth charts</li>
                <li>📊 Income vs expense comparisons</li>
                <li>💰 Savings rate tracking</li>
                <li>📅 Day-of-week spending patterns</li>
                <li>🎯 Category performance metrics</li>
                <li>📍 Trend line predictions</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)

with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('''
        <div class="feature-card">
            <h3>🎯 Savings Goals Tracker</h3>
            <ul>
                <li>✅ Set multiple savings goals</li>
                <li>✅ Visual progress bars (0-100%)</li>
                <li>✅ Track saved vs target amounts</li>
                <li>✅ Goal completion forecasts</li>
                <li>✅ Interactive stacked progress charts</li>
                <li>✅ Motivational achievement status</li>
                <li>✅ Time-to-goal calculations</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="feature-card">
            <h3>💡 Smart Recommendations <span class="new-feature">NEW</span></h3>
            <ul>
                <li>✅ AI-powered financial advice</li>
                <li>✅ Expense control suggestions</li>
                <li>✅ Savings rate optimization tips</li>
                <li>✅ Income diversification guidance</li>
                <li>✅ Goal achievement strategies</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown('''
        <div class="feature-card">
            <h3>💼 Budget Management</h3>
            <ul>
                <li>✅ Create custom category budgets</li>
                <li>✅ Track budget vs actual spending</li>
                <li>✅ Real-time overspending alerts</li>
                <li>✅ Budget utilization percentages</li>
                <li>✅ Smart budget recommendations</li>
                <li>✅ Remaining budget calculations</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="feature-card">
            <h3>📊 Financial Health Dashboard <span class="new-feature">NEW</span></h3>
            <ul>
                <li>✅ Comprehensive health score (0-100)</li>
                <li>✅ Interactive gauge visualization</li>
                <li>✅ Score breakdown by category</li>
                <li>✅ Expense control rating (35 points)</li>
                <li>✅ Savings rate evaluation (30 points)</li>
                <li>✅ Goal planning assessment (20 points)</li>
                <li>✅ Income diversity score (15 points)</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)

with tab4:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('''
        <div class="feature-card">
            <h3>🔒 Security & Privacy</h3>
            <ul>
                <li>🔐 Secure user authentication</li>
                <li>🔒 Password hashing with SHA-256</li>
                <li>👤 Multi-user support</li>
                <li>💾 SQLite database encryption</li>
                <li>🛡️ Session-based access control</li>
                <li>📱 Secure data transmission</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="feature-card">
            <h3>🔍 Advanced Filtering <span class="new-feature">NEW</span></h3>
            <ul>
                <li>📅 Date range filtering (custom, 7/30/90 days)</li>
                <li>🏷️ Category-based filtering</li>
                <li>🔎 Multi-criteria search</li>
                <li>📊 Real-time chart updates</li>
                <li>💾 Save filter preferences</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown('''
        <div class="feature-card">
            <h3>📥 Data Export Options</h3>
            <ul>
                <li>📊 Export to CSV format</li>
                <li>📈 Export to Excel</li>
                <li>💾 Download expense reports</li>
                <li>💰 Download income records</li>
                <li>🎯 Download goals data</li>
                <li>📅 Timestamped file names</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="feature-card">
            <h3>📱 User Experience</h3>
            <ul>
                <li>🎨 Modern, intuitive interface</li>
                <li>⚡ Real-time data updates</li>
                <li>📱 Responsive design</li>
                <li>🖱️ Interactive hover tooltips</li>
                <li>🔍 Zoom & pan on charts</li>
                <li>💫 Smooth animations</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)

st.markdown("---")

# How It Works
st.markdown("## 🚀 How BudgetBuddy Works")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div style='text-align: center; padding: 20px; background: #f0f2f6; border-radius: 10px;'>
        <h2>1️⃣</h2>
        <h4>Track</h4>
        <p>Record income and expenses with detailed categories and descriptions</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='text-align: center; padding: 20px; background: #f0f2f6; border-radius: 10px;'>
        <h2>2️⃣</h2>
        <h4>Visualize</h4>
        <p>Explore 20+ interactive charts with real-time insights</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='text-align: center; padding: 20px; background: #f0f2f6; border-radius: 10px;'>
        <h2>3️⃣</h2>
        <h4>Analyze</h4>
        <p>Get financial health scores and personalized recommendations</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div style='text-align: center; padding: 20px; background: #f0f2f6; border-radius: 10px;'>
        <h2>4️⃣</h2>
        <h4>Achieve</h4>
        <p>Set goals, create budgets, and reach financial freedom</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Technology Stack
st.markdown("## 🔧 Built With Modern Technology")

tech_col1, tech_col2, tech_col3, tech_col4 = st.columns(4)

with tech_col1:
    st.markdown("""
    **Frontend Framework**
    - 🎨 Streamlit 1.28+
    - 🐍 Python 3.8+
    - 💅 Custom CSS
    """)

with tech_col2:
    st.markdown("""
    **Data Processing**
    - 📊 Pandas
    - 🔢 NumPy
    - 🤖 Scikit-learn
    """)

with tech_col3:
    st.markdown("""
    **Visualizations**
    - 📈 Plotly Express
    - 📊 Plotly Graph Objects
    - 🎨 Matplotlib
    - 🌊 Seaborn
    """)

with tech_col4:
    st.markdown("""
    **Database & Security**
    - 💾 SQLite3
    - 🔒 Hashlib (SHA-256)
    - 🛡️ Session Management
    """)

st.markdown("---")

# Benefits Section
st.markdown("## 🌟 Why Choose BudgetBuddy?")

benefits = {
    "💡 Complete Financial Visibility": "Understand exactly where every rupee goes with detailed tracking and 20+ interactive visualizations",
    "🎯 Data-Driven Decisions": "Make informed financial choices based on real-time insights, trends, and AI-powered recommendations",
    "🏆 Goal Achievement": "Stay motivated with visual progress tracking and get personalized strategies to reach your financial targets",
    "⚡ Time-Saving Automation": "Recurring transactions, automatic calculations, and smart categorization save hours every month",
    "📊 Advanced Analytics": "Moving averages, trend predictions, month-over-month comparisons, and statistical analysis at your fingertips",
    "🔒 Bank-Level Security": "Your sensitive financial data is protected with encryption and secure authentication",
    "📱 User-Friendly Experience": "Intuitive interface with hover tooltips, interactive charts, and smooth navigation",
    "💾 Full Data Control": "Export your data anytime in CSV/Excel format - you own your financial information"
}

for benefit, description in benefits.items():
    with st.expander(f"✅ {benefit}"):
        st.write(description)

st.markdown("---")

# What's New Section
st.markdown("## 🆕 What's New in Version 3.0")

st.success("""
**Major Updates & Features:**

✨ **Advanced Interactive Dashboard** - 20+ new chart types including donut charts, treemaps, waterfall charts, Sankey diagrams, heatmaps, and box plots

💯 **Financial Health Score** - Comprehensive 100-point scoring system with AI-powered recommendations

📊 **Time Series Analysis** - Daily, weekly, and monthly trends with 7-day and 30-day moving averages

🔍 **Advanced Filtering** - Date range and category-based filtering with real-time chart updates

📈 **Comparative Analytics** - Month-over-month growth, income vs expense comparisons, and trend predictions

🎯 **Goal Forecasting** - Estimated time to complete each savings goal based on current savings rate

📉 **Spending Insights** - Top expenses, category breakdowns, transaction frequency, and spending velocity

🗓️ **Calendar Analysis** - Day-of-week spending patterns and monthly category heatmaps

💡 **Smart Recommendations** - Personalized financial advice based on your spending habits and health score

📥 **Enhanced Export** - Download all financial data with timestamped CSV files
""")

st.markdown("---")

# Getting Started Guide
st.markdown("## 🎯 Quick Start Guide")

st.markdown("""
### 📝 **Step-by-Step Setup:**

1. **🔐 Create Account** → Register with a unique username and secure password
2. **💵 Add Income** → Navigate to Income Monitoring and log your income sources
3. **📊 Record Expenses** → Use Expense Tracking to add your daily expenses
4. **🔄 Set Recurring** → Configure recurring transactions for regular bills
5. **💼 Create Budget** → Set category budgets in Budget Management
6. **🎯 Define Goals** → Add savings goals in the Saving Goals section
7. **📈 Visualize** → Explore the Advanced Visualization Dashboard
8. **💯 Check Score** → Monitor your Financial Health Score
9. **📥 Export Data** → Download reports for external analysis

### 💡 **Pro Tips:**
- ✅ Track expenses daily for accurate insights
- ✅ Use filters to analyze specific time periods
- ✅ Hover over charts for detailed information
- ✅ Set realistic budgets based on historical data
- ✅ Review your financial health score weekly
- ✅ Export data monthly for backup
""")

st.markdown("---")

# Interactive Features Highlight
st.markdown("## 🖱️ Interactive Features Guide")

feature_col1, feature_col2 = st.columns(2)

with feature_col1:
    st.info("""
    **📊 Chart Interactions:**
    - 🖱️ **Hover** - View detailed data tooltips
    - 🔍 **Click & Drag** - Zoom into specific areas
    - 👆 **Double-click** - Reset zoom to default view
    - 🎨 **Click Legend** - Show/hide data series
    - 📏 **Pan** - Move around zoomed charts
    """)

with feature_col2:
    st.warning("""
    **⚡ Dashboard Features:**
    - 📅 **Date Filters** - Select custom time ranges
    - 🏷️ **Category Filters** - Focus on specific expenses
    - 🔄 **Real-time Updates** - Changes reflect instantly
    - 💾 **Auto-save** - All data saved automatically
    - 📱 **Responsive** - Works on all screen sizes
    """)

st.markdown("---")

# Statistics Dashboard
st.markdown("## 📊 App Capabilities at a Glance")

stat_col1, stat_col2, stat_col3, stat_col4, stat_col5 = st.columns(5)

with stat_col1:
    st.metric("Total Features", "8", delta="Core Modules", help="Complete financial management suite")
with stat_col2:
    st.metric("Chart Types", "20+", delta="Interactive", help="Plotly-powered visualizations")
with stat_col3:
    st.metric("Categories", "10+", delta="Customizable", help="Flexible expense categories")
with stat_col4:
    st.metric("Export Formats", "2", delta="CSV & Excel", help="Multiple export options")
with stat_col5:
    st.metric("Security Level", "High", delta="Encrypted", help="Bank-grade protection")

st.markdown("---")

# Call to Action
st.markdown("""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            padding: 40px; 
            border-radius: 15px; 
            text-align: center; 
            color: white;
            margin: 30px 0;'>
    <h2 style='margin: 0; font-size: 2.5em;'>🚀 Start Your Financial Journey Today!</h2>
    <p style='font-size: 1.3em; margin: 20px 0;'>
        Take control of your finances with BudgetBuddy's powerful analytics and smart insights
    </p>
    <p style='font-size: 1.1em; margin: 10px 0;'>
        Track • Visualize • Analyze • Achieve
    </p>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")

footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])

with footer_col2:
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <p style='font-size: 1.1em; color: #666;'>
            Made with ❤️ using Streamlit | Version 3.0 | © 2025 BudgetBuddy
        </p>
        <p style='font-size: 0.9em; color: #999;'>
            🔒 Your data is encrypted and secure | 📧 For support, contact us
        </p>
    </div>
    """, unsafe_allow_html=True)

# Final Tips
st.success("💡 **Remember:** Consistent tracking is the key to financial success. Use BudgetBuddy daily for best results!")
