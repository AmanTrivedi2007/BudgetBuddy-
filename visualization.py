# visualization.py - ADVANCED INTERACTIVE VERSION

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import numpy as np
from database import get_all_income, get_all_expenses, get_all_goals
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import calendar

# Set styles
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.family'] = 'sans-serif'

# Page configuration
st.set_page_config(page_title="Budget Dashboard", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .insight-box {
        background: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Advanced Budget Intelligence Dashboard")
st.markdown("### Your Complete Financial Analytics Platform")

# Get current logged-in user
user_id = st.session_state.username

# Load data from database with user_id
income_list = get_all_income(user_id)
expense_list = get_all_expenses(user_id)
goals_list = get_all_goals(user_id)

# Calculate totals using DATABASE data
total_income = sum(item['amount'] for item in income_list)
total_expense = sum(item['amount'] for item in expense_list)
total_saved_in_goals = sum(goal['saved_amount'] for goal in goals_list)
available_balance = total_income - total_expense - total_saved_in_goals

# ===========================
# SIDEBAR FILTERS
# ===========================
st.sidebar.header("🔍 Dashboard Filters")

# Date range filter
if expense_list or income_list:
    all_dates = []
    if expense_list:
        all_dates.extend([datetime.strptime(e['date'], '%Y-%m-%d') for e in expense_list])
    if income_list:
        all_dates.extend([datetime.strptime(i['date'], '%Y-%m-%d') for i in income_list])
    
    if all_dates:
        min_date = min(all_dates).date()
        max_date = max(all_dates).date()
        
        date_filter = st.sidebar.radio(
            "Time Period",
            ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days", "Custom Range"]
        )
        
        if date_filter == "Custom Range":
            start_date = st.sidebar.date_input("Start Date", min_date)
            end_date = st.sidebar.date_input("End Date", max_date)
        elif date_filter == "Last 7 Days":
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=7)
        elif date_filter == "Last 30 Days":
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
        elif date_filter == "Last 90 Days":
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=90)
        else:
            start_date = min_date
            end_date = max_date
        
        # Apply filters
        if expense_list:
            expense_list = [e for e in expense_list if start_date <= datetime.strptime(e['date'], '%Y-%m-%d').date() <= end_date]
        if income_list:
            income_list = [i for i in income_list if start_date <= datetime.strptime(i['date'], '%Y-%m-%d').date() <= end_date]
        
        # Recalculate totals after filtering
        total_income = sum(item['amount'] for item in income_list)
        total_expense = sum(item['amount'] for item in expense_list)

# Category filter for expenses
if expense_list:
    expense_categories = list(set([e['category'] for e in expense_list]))
    selected_categories = st.sidebar.multiselect(
        "Filter by Expense Category",
        expense_categories,
        default=expense_categories
    )
    expense_list = [e for e in expense_list if e['category'] in selected_categories]
    total_expense = sum(item['amount'] for item in expense_list)

st.sidebar.markdown("---")
st.sidebar.markdown("💡 **Tip:** Use filters to analyze specific time periods and categories")

# ===========================
# SECTION 1: ENHANCED KPI DASHBOARD
# ===========================
st.markdown("## 💰 Financial Health Overview")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Income", 
        f"₹{total_income:,.0f}",
        delta=None,
        help="Total income received in selected period"
    )

with col2:
    expense_pct = (total_expense / total_income * 100) if total_income > 0 else 0
    st.metric(
        "Total Expenses", 
        f"₹{total_expense:,.0f}",
        delta=f"-{expense_pct:.1f}% of income",
        delta_color="inverse",
        help="Total expenses in selected period"
    )

with col3:
    st.metric(
        "Saved in Goals", 
        f"₹{total_saved_in_goals:,.0f}",
        help="Total amount saved towards goals"
    )

with col4:
    savings_rate = (available_balance / total_income * 100) if total_income > 0 else 0
    st.metric(
        "Available Balance", 
        f"₹{available_balance:,.0f}",
        delta=f"{savings_rate:.1f}% savings",
        delta_color="normal" if available_balance >= 0 else "inverse",
        help="Remaining balance after expenses and goals"
    )

with col5:
    avg_daily_expense = total_expense / max((end_date - start_date).days, 1) if expense_list else 0
    st.metric(
        "Daily Avg Expense", 
        f"₹{avg_daily_expense:,.0f}",
        help="Average daily spending"
    )

st.markdown("---")

# Check if data exists
if not expense_list and not income_list:
    st.info("📝 No data available for visualization. Add some income and expenses first!")
    st.stop()

# ===========================
# SECTION 2: INTERACTIVE EXPENSE BREAKDOWN (PLOTLY DONUT + TREEMAP)
# ===========================
if expense_list:
    st.markdown("## 🍩 Expense Distribution Analysis")
    
    expense_df = pd.DataFrame(expense_list)
    category_totals = expense_df.groupby('category')['amount'].sum().reset_index()
    category_totals = category_totals.sort_values('amount', ascending=False)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Interactive Donut Chart with Plotly
        fig = go.Figure(data=[go.Pie(
            labels=category_totals['category'],
            values=category_totals['amount'],
            hole=0.5,
            textposition='auto',
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>' +
                         'Amount: ₹%{value:,.2f}<br>' +
                         'Percentage: %{percent}<br>' +
                         '<extra></extra>',
            marker=dict(
                colors=px.colors.qualitative.Set3,
                line=dict(color='white', width=3)
            ),
            pull=[0.1 if i == 0 else 0 for i in range(len(category_totals))]
        )])
        
        fig.update_layout(
            title={
                'text': 'Expense Distribution by Category',
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 18, 'color': '#2c3e50', 'family': 'Arial Black'}
            },
            height=450,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05
            ),
            annotations=[dict(
                text=f'Total<br>₹{total_expense:,.0f}',
                x=0.5, y=0.5,
                font_size=16,
                showarrow=False,
                font=dict(color='#34495e', family='Arial', weight='bold')
            )]
        )
        
        st.plotly_chart(fig, use_container_width=True, key="expense_donut")
    
    with col2:
        st.markdown("### 📊 Category Insights")
        for idx, row in category_totals.head(5).iterrows():
            percentage = (row['amount'] / total_expense * 100)
            st.markdown(f"**{row['category']}**")
            st.progress(percentage / 100)
            st.caption(f"₹{row['amount']:,.2f} ({percentage:.1f}%)")
            st.markdown("")
        
        # Top spending category alert
        if len(category_totals) > 0:
            top_category = category_totals.iloc[0]
            top_pct = (top_category['amount'] / total_expense * 100)
            if top_pct > 40:
                st.warning(f"⚠️ **{top_category['category']}** accounts for {top_pct:.1f}% of total expenses!")
    
    # Treemap visualization
    st.markdown("### 🗺️ Hierarchical Expense Treemap")
    fig_treemap = px.treemap(
        category_totals,
        path=['category'],
        values='amount',
        color='amount',
        color_continuous_scale='RdYlGn_r',
        title='Expense Categories - Hierarchical View'
    )
    fig_treemap.update_traces(
        textinfo='label+value+percent parent',
        hovertemplate='<b>%{label}</b><br>Amount: ₹%{value:,.2f}<br>Percentage: %{percentParent}<extra></extra>'
    )
    fig_treemap.update_layout(height=400)
    st.plotly_chart(fig_treemap, use_container_width=True, key="expense_treemap")

st.markdown("---")

# ===========================
# SECTION 3: CASH FLOW WATERFALL & SANKEY DIAGRAM
# ===========================
st.markdown("## 💧 Cash Flow Analysis")

col1, col2 = st.columns(2)

with col1:
    # Waterfall Chart
    st.markdown("### Waterfall: Income to Balance")
    
    waterfall_labels = ['Income', 'Expenses', 'Goals Saved', 'Final Balance']
    waterfall_values = [total_income, -total_expense, -total_saved_in_goals, available_balance]
    waterfall_measure = ['relative', 'relative', 'relative', 'total']
    
    fig_waterfall = go.Figure(go.Waterfall(
        name="Cash Flow",
        orientation="v",
        measure=waterfall_measure,
        x=waterfall_labels,
        textposition="outside",
        text=[f"₹{abs(v):,.0f}" for v in waterfall_values],
        y=waterfall_values,
        connector={"line": {"color": "rgb(63, 63, 63)", "width": 2}},
        increasing={"marker": {"color": "#2ecc71", "line": {"color": "#27ae60", "width": 2}}},
        decreasing={"marker": {"color": "#e74c3c", "line": {"color": "#c0392b", "width": 2}}},
        totals={"marker": {"color": "#3498db", "line": {"color": "#2980b9", "width": 2}}},
        hovertemplate='<b>%{x}</b><br>Amount: ₹%{y:,.2f}<extra></extra>'
    ))
    
    fig_waterfall.update_layout(
        title="Cash Flow Breakdown",
        height=400,
        showlegend=False,
        yaxis_title="Amount (₹)"
    )
    
    st.plotly_chart(fig_waterfall, use_container_width=True, key="waterfall")

with col2:
    # Sankey Diagram
    st.markdown("### Sankey: Money Flow Diagram")
    
    if expense_list:
        # Prepare Sankey data
        sankey_labels = ['Total Income'] + [cat['category'] for cat in category_totals.to_dict('records')]
        if available_balance > 0:
            sankey_labels.append('Savings')
        if total_saved_in_goals > 0:
            sankey_labels.append('Goals')
        
        sankey_source = [0] * len(category_totals)
        sankey_target = list(range(1, len(category_totals) + 1))
        sankey_value = category_totals['amount'].tolist()
        
        if available_balance > 0:
            sankey_source.append(0)
            sankey_target.append(len(sankey_labels) - (2 if total_saved_in_goals > 0 else 1))
            sankey_value.append(available_balance)
        
        if total_saved_in_goals > 0:
            sankey_source.append(0)
            sankey_target.append(len(sankey_labels) - 1)
            sankey_value.append(total_saved_in_goals)
        
        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=sankey_labels,
                color=['#3498db'] + ['#e74c3c'] * len(category_totals) + ['#2ecc71'] * 2
            ),
            link=dict(
                source=sankey_source,
                target=sankey_target,
                value=sankey_value,
                hovertemplate='%{source.label} → %{target.label}<br>₹%{value:,.2f}<extra></extra>'
            )
        )])
        
        fig_sankey.update_layout(
            title="Money Flow Visualization",
            height=400,
            font_size=10
        )
        
        st.plotly_chart(fig_sankey, use_container_width=True, key="sankey")

st.markdown("---")

# ===========================
# SECTION 4: ADVANCED TIME SERIES ANALYSIS
# ===========================
if expense_list:
    st.markdown("## 📈 Time Series & Trend Analysis")
    
    expense_df = pd.DataFrame(expense_list)
    expense_df['date'] = pd.to_datetime(expense_df['date'])
    expense_df = expense_df.sort_values('date')
    
    # Daily, Weekly, Monthly aggregation
    tab1, tab2, tab3 = st.tabs(["📅 Daily Trends", "📊 Weekly Analysis", "📆 Monthly Overview"])
    
    with tab1:
        # Daily spending with moving averages
        daily_spending = expense_df.groupby('date')['amount'].sum().reset_index()
        daily_spending['7_day_ma'] = daily_spending['amount'].rolling(window=7, min_periods=1).mean()
        daily_spending['30_day_ma'] = daily_spending['amount'].rolling(window=30, min_periods=1).mean()
        
        fig_daily = go.Figure()
        
        # Daily bars
        fig_daily.add_trace(go.Bar(
            x=daily_spending['date'],
            y=daily_spending['amount'],
            name='Daily Spending',
            marker_color='rgba(231, 76, 60, 0.6)',
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>₹%{y:,.2f}<extra></extra>'
        ))
        
        # 7-day MA
        fig_daily.add_trace(go.Scatter(
            x=daily_spending['date'],
            y=daily_spending['7_day_ma'],
            mode='lines',
            name='7-Day Average',
            line=dict(color='#3498db', width=3),
            hovertemplate='<b>7-Day Avg</b><br>₹%{y:,.2f}<extra></extra>'
        ))
        
        # 30-day MA
        fig_daily.add_trace(go.Scatter(
            x=daily_spending['date'],
            y=daily_spending['30_day_ma'],
            mode='lines',
            name='30-Day Average',
            line=dict(color='#2ecc71', width=3, dash='dash'),
            hovertemplate='<b>30-Day Avg</b><br>₹%{y:,.2f}<extra></extra>'
        ))
        
        fig_daily.update_layout(
            title='Daily Spending with Moving Averages',
            xaxis_title='Date',
            yaxis_title='Amount (₹)',
            height=500,
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig_daily, use_container_width=True, key="daily_trend")
        
        # Daily insights
        avg_daily = daily_spending['amount'].mean()
        max_day = daily_spending.loc[daily_spending['amount'].idxmax()]
        st.info(f"📊 **Daily Insights:** Average daily spending: ₹{avg_daily:,.2f} | "
                f"Highest spending day: {max_day['date'].strftime('%Y-%m-%d')} (₹{max_day['amount']:,.2f})")
    
    with tab2:
        # Weekly analysis
        expense_df['week'] = expense_df['date'].dt.to_period('W').astype(str)
        weekly_spending = expense_df.groupby('week')['amount'].sum().reset_index()
        
        fig_weekly = px.bar(
            weekly_spending,
            x='week',
            y='amount',
            title='Weekly Spending Pattern',
            labels={'week': 'Week', 'amount': 'Amount (₹)'},
            color='amount',
            color_continuous_scale='Reds',
            text='amount'
        )
        fig_weekly.update_traces(
            texttemplate='₹%{text:,.0f}',
            textposition='outside',
            hovertemplate='<b>Week: %{x}</b><br>Amount: ₹%{y:,.2f}<extra></extra>'
        )
        fig_weekly.update_layout(height=450)
        st.plotly_chart(fig_weekly, use_container_width=True, key="weekly_trend")
    
    with tab3:
        # Monthly analysis
        expense_df['month'] = expense_df['date'].dt.to_period('M').astype(str)
        monthly_spending = expense_df.groupby('month')['amount'].sum().reset_index()
        
        fig_monthly = go.Figure()
        fig_monthly.add_trace(go.Scatter(
            x=monthly_spending['month'],
            y=monthly_spending['amount'],
            mode='lines+markers',
            name='Monthly Spending',
            line=dict(color='#e74c3c', width=4),
            marker=dict(size=12, color='white', line=dict(color='#e74c3c', width=3)),
            fill='tozeroy',
            fillcolor='rgba(231, 76, 60, 0.2)',
            hovertemplate='<b>%{x}</b><br>₹%{y:,.2f}<extra></extra>'
        ))
        
        fig_monthly.update_layout(
            title='Monthly Spending Trend',
            xaxis_title='Month',
            yaxis_title='Amount (₹)',
            height=450
        )
        
        st.plotly_chart(fig_monthly, use_container_width=True, key="monthly_trend")

st.markdown("---")

# ===========================
# SECTION 5: CATEGORY-WISE DEEP DIVE
# ===========================
if expense_list:
    st.markdown("## 🔍 Category-Wise Deep Dive Analysis")
    
    expense_df = pd.DataFrame(expense_list)
    
    # Calculate comprehensive category statistics
    category_stats = expense_df.groupby('category').agg({
        'amount': ['sum', 'mean', 'median', 'std', 'count', 'min', 'max']
    }).reset_index()
    category_stats.columns = ['Category', 'Total', 'Average', 'Median', 'Std Dev', 'Count', 'Min', 'Max']
    category_stats = category_stats.sort_values('Total', ascending=False)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Multi-metric bar chart
        fig_cat_stats = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Total Spending by Category', 'Transaction Count by Category'),
            specs=[[{"type": "bar"}, {"type": "bar"}]]
        )
        
        fig_cat_stats.add_trace(
            go.Bar(
                x=category_stats['Category'],
                y=category_stats['Total'],
                name='Total',
                marker_color='#e74c3c',
                text=[f'₹{v:,.0f}' for v in category_stats['Total']],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Total: ₹%{y:,.2f}<extra></extra>'
            ),
            row=1, col=1
        )
        
        fig_cat_stats.add_trace(
            go.Bar(
                x=category_stats['Category'],
                y=category_stats['Count'],
                name='Count',
                marker_color='#3498db',
                text=category_stats['Count'],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Transactions: %{y}<extra></extra>'
            ),
            row=1, col=2
        )
        
        fig_cat_stats.update_layout(
            height=500,
            showlegend=False,
            title_text="Category Performance Metrics"
        )
        
        st.plotly_chart(fig_cat_stats, use_container_width=True, key="cat_stats")
    
    with col2:
        st.markdown("### 📈 Category Statistics")
        st.dataframe(
            category_stats[['Category', 'Total', 'Average', 'Count']].style.format({
                'Total': '₹{:,.2f}',
                'Average': '₹{:,.2f}',
                'Count': '{:.0f}'
            }).background_gradient(cmap='RdYlGn_r', subset=['Total']),
            height=450
        )
    
    # Box plot for distribution analysis
    st.markdown("### 📦 Expense Distribution by Category (Box Plot)")
    fig_box = px.box(
        expense_df,
        x='category',
        y='amount',
        color='category',
        title='Expense Distribution & Outliers by Category',
        labels={'category': 'Category', 'amount': 'Amount (₹)'},
        points='all',
        hover_data=['date', 'description']
    )
    fig_box.update_layout(height=450, showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True, key="box_plot")

st.markdown("---")

# ===========================
# SECTION 6: CALENDAR HEATMAP & SPENDING PATTERNS
# ===========================
if expense_list:
    st.markdown("## 🗓️ Calendar & Pattern Analysis")
    
    expense_df = pd.DataFrame(expense_list)
    expense_df['date'] = pd.to_datetime(expense_df['date'])
    expense_df['day_of_week'] = expense_df['date'].dt.day_name()
    expense_df['day_of_month'] = expense_df['date'].dt.day
    expense_df['month_name'] = expense_df['date'].dt.strftime('%Y-%m')
    expense_df['hour'] = 12  # Default since time not tracked
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Day of week analysis
        st.markdown("### 📅 Spending by Day of Week")
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_spending = expense_df.groupby('day_of_week')['amount'].agg(['sum', 'mean', 'count']).reindex(day_order)
        dow_spending = dow_spending.reset_index()
        
        fig_dow = go.Figure()
        fig_dow.add_trace(go.Bar(
            x=dow_spending['day_of_week'],
            y=dow_spending['sum'],
            name='Total',
            marker_color=['#e74c3c' if day in ['Saturday', 'Sunday'] else '#3498db' for day in dow_spending['day_of_week']],
            text=[f'₹{v:,.0f}' for v in dow_spending['sum']],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Total: ₹%{y:,.2f}<extra></extra>'
        ))
        
        fig_dow.update_layout(
            xaxis_title='Day of Week',
            yaxis_title='Total Spending (₹)',
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig_dow, use_container_width=True, key="dow_chart")
    
    with col2:
        # Monthly heatmap
        st.markdown("### 🔥 Category × Month Heatmap")
        monthly_category = expense_df.pivot_table(
            values='amount',
            index='category',
            columns='month_name',
            aggfunc='sum',
            fill_value=0
        )
        
        if not monthly_category.empty and len(monthly_category.columns) > 0:
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=monthly_category.values,
                x=monthly_category.columns,
                y=monthly_category.index,
                colorscale='Reds',
                text=monthly_category.values,
                texttemplate='₹%{text:,.0f}',
                textfont={"size": 9},
                hovertemplate='<b>%{y}</b><br>Month: %{x}<br>Amount: ₹%{z:,.2f}<extra></extra>',
                colorbar=dict(title="Amount")
            ))
            
            fig_heatmap.update_layout(
                xaxis_title='Month',
                yaxis_title='Category',
                height=400
            )
            
            st.plotly_chart(fig_heatmap, use_container_width=True, key="heatmap")

st.markdown("---")

# ===========================
# SECTION 7: INCOME ANALYSIS
# ===========================
if income_list:
    st.markdown("## 💵 Income Analysis Dashboard")
    
    income_df = pd.DataFrame(income_list)
    income_df['date'] = pd.to_datetime(income_df['date'])
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Income sources breakdown
        income_by_source = income_df.groupby('source')['amount'].agg(['sum', 'count', 'mean']).reset_index()
        income_by_source.columns = ['Source', 'Total', 'Count', 'Average']
        income_by_source = income_by_source.sort_values('Total', ascending=True)
        
        fig_income = go.Figure()
        fig_income.add_trace(go.Bar(
            y=income_by_source['Source'],
            x=income_by_source['Total'],
            orientation='h',
            marker=dict(
                color=income_by_source['Total'],
                colorscale='Greens',
                showscale=True,
                colorbar=dict(title="Amount (₹)")
            ),
            text=[f'₹{v:,.0f}' for v in income_by_source['Total']],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Total: ₹%{x:,.2f}<br>Transactions: %{customdata[0]}<br>Average: ₹%{customdata[1]:,.2f}<extra></extra>',
            customdata=income_by_source[['Count', 'Average']].values
        ))
        
        fig_income.update_layout(
            title='Income Distribution by Source',
            xaxis_title='Total Amount (₹)',
            height=400
        )
        
        st.plotly_chart(fig_income, use_container_width=True, key="income_sources")
    
    with col2:
        st.markdown("### 💰 Income Insights")
        for _, row in income_by_source.iterrows():
            pct = (row['Total'] / total_income * 100)
            st.markdown(f"**{row['Source']}**")
            st.progress(pct / 100)
            st.caption(f"₹{row['Total']:,.0f} ({pct:.1f}%) | {int(row['Count'])} transactions")
            st.markdown("")
        
        # Income diversity score
        diversity_score = len(income_by_source) * 20
        diversity_score = min(diversity_score, 100)
        st.metric("Income Diversity Score", f"{diversity_score}/100")
        if diversity_score >= 60:
            st.success("✅ Good income diversification!")
        else:
            st.warning("⚠️ Consider diversifying income sources")
    
    # Income vs Expense comparison over time
    st.markdown("### 📊 Income vs Expense Comparison")
    
    income_df['month'] = income_df['date'].dt.to_period('M').astype(str)
    monthly_income = income_df.groupby('month')['amount'].sum().reset_index()
    monthly_income.columns = ['month', 'income']
    
    if expense_list:
        expense_df = pd.DataFrame(expense_list)
        expense_df['date'] = pd.to_datetime(expense_df['date'])
        expense_df['month'] = expense_df['date'].dt.to_period('M').astype(str)
        monthly_expense = expense_df.groupby('month')['amount'].sum().reset_index()
        monthly_expense.columns = ['month', 'expense']
        
        monthly_comparison = pd.merge(monthly_income, monthly_expense, on='month', how='outer').fillna(0)
        monthly_comparison['savings'] = monthly_comparison['income'] - monthly_comparison['expense']
        monthly_comparison['savings_rate'] = (monthly_comparison['savings'] / monthly_comparison['income'] * 100).fillna(0)
        
        fig_comparison = make_subplots(
            rows=1, cols=1,
            specs=[[{"secondary_y": True}]]
        )
        
        fig_comparison.add_trace(
            go.Bar(
                x=monthly_comparison['month'],
                y=monthly_comparison['income'],
                name='Income',
                marker_color='#2ecc71',
                hovertemplate='<b>Income</b><br>₹%{y:,.2f}<extra></extra>'
            ),
            secondary_y=False
        )
        
        fig_comparison.add_trace(
            go.Bar(
                x=monthly_comparison['month'],
                y=monthly_comparison['expense'],
                name='Expenses',
                marker_color='#e74c3c',
                hovertemplate='<b>Expenses</b><br>₹%{y:,.2f}<extra></extra>'
            ),
            secondary_y=False
        )
        
        fig_comparison.add_trace(
            go.Scatter(
                x=monthly_comparison['month'],
                y=monthly_comparison['savings_rate'],
                name='Savings Rate %',
                mode='lines+markers',
                line=dict(color='#3498db', width=3),
                marker=dict(size=10),
                hovertemplate='<b>Savings Rate</b><br>%{y:.1f}%<extra></extra>'
            ),
            secondary_y=True
        )
        
        fig_comparison.update_layout(
            title='Monthly Income, Expenses & Savings Rate',
            height=450,
            hovermode='x unified',
            barmode='group',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        fig_comparison.update_yaxes(title_text="Amount (₹)", secondary_y=False)
        fig_comparison.update_yaxes(title_text="Savings Rate (%)", secondary_y=True)
        
        st.plotly_chart(fig_comparison, use_container_width=True, key="income_expense_compare")

st.markdown("---")

# ===========================
# SECTION 8: GOALS PROGRESS TRACKER
# ===========================
if goals_list:
    st.markdown("## 🎯 Savings Goals Progress Dashboard")
    
    goals_data = []
    for goal in goals_list:
        progress_pct = (goal['saved_amount'] / goal['target_amount'] * 100) if goal['target_amount'] > 0 else 0
        remaining = max(0, goal['target_amount'] - goal['saved_amount'])
        goals_data.append({
            'Goal': goal['name'],
            'Saved': goal['saved_amount'],
            'Remaining': remaining,
            'Target': goal['target_amount'],
            'Progress': progress_pct,
            'Status': 'Completed ✅' if progress_pct >= 100 else 'In Progress 🔄'
        })
    
    goals_df = pd.DataFrame(goals_data)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Stacked horizontal bar for goals
        fig_goals = go.Figure()
        
        fig_goals.add_trace(go.Bar(
            y=goals_df['Goal'],
            x=goals_df['Saved'],
            name='Saved',
            orientation='h',
            marker=dict(color='#2ecc71', line=dict(color='#27ae60', width=2)),
            text=[f'₹{v:,.0f}' for v in goals_df['Saved']],
            textposition='inside',
            textfont=dict(color='white', size=12, family='Arial Black'),
            hovertemplate='<b>Saved</b><br>₹%{x:,.2f}<extra></extra>'
        ))
        
        fig_goals.add_trace(go.Bar(
            y=goals_df['Goal'],
            x=goals_df['Remaining'],
            name='Remaining',
            orientation='h',
            marker=dict(color='#ecf0f1', line=dict(color='#bdc3c7', width=2)),
            text=[f'₹{v:,.0f}' for v in goals_df['Remaining']],
            textposition='inside',
            hovertemplate='<b>Remaining</b><br>₹%{x:,.2f}<extra></extra>'
        ))
        
        fig_goals.update_layout(
            title='Goals Achievement Progress',
            xaxis_title='Amount (₹)',
            height=max(350, len(goals_data) * 70),
            barmode='stack',
            hovermode='y unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig_goals, use_container_width=True, key="goals_progress")
    
    with col2:
        st.markdown("### 🏆 Goal Details")
        for _, goal in goals_df.iterrows():
            with st.container():
                st.markdown(f"**{goal['Goal']}** {goal['Status']}")
                st.progress(min(goal['Progress'] / 100, 1.0))
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Progress", f"{goal['Progress']:.1f}%")
                with col_b:
                    st.metric("Target", f"₹{goal['Target']:,.0f}")
                st.markdown("---")
    
    # Goal completion timeline
    st.markdown("### 📅 Goal Completion Forecast")
    
    if total_income > 0 and available_balance > 0:
        monthly_savings = available_balance  # Simplified assumption
        forecast_data = []
        
        for _, goal in goals_df.iterrows():
            if goal['Remaining'] > 0:
                months_needed = goal['Remaining'] / max(monthly_savings, 1)
                forecast_data.append({
                    'Goal': goal['Goal'],
                    'Months to Complete': round(months_needed, 1),
                    'Remaining': goal['Remaining']
                })
        
        if forecast_data:
            forecast_df = pd.DataFrame(forecast_data)
            
            fig_forecast = px.bar(
                forecast_df,
                x='Goal',
                y='Months to Complete',
                color='Remaining',
                color_continuous_scale='RdYlGn_r',
                title='Estimated Months to Complete Each Goal',
                text='Months to Complete'
            )
            fig_forecast.update_traces(
                texttemplate='%{text:.1f} months',
                textposition='outside'
            )
            fig_forecast.update_layout(height=400)
            st.plotly_chart(fig_forecast, use_container_width=True, key="goal_forecast")

st.markdown("---")

# ===========================
# SECTION 9: FINANCIAL HEALTH SCORE WITH GAUGE
# ===========================
st.markdown("## 💯 Financial Health Score & Recommendations")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    # Calculate comprehensive health score
    score = 0
    score_breakdown = {}
    recommendations = []
    
    # 1. Expense Control (35 points)
    if total_income > 0:
        expense_ratio = total_expense / total_income
        if expense_ratio < 0.5:
            score += 35
            score_breakdown['Expense Control'] = 35
            recommendations.append("✅ Excellent expense control! You're spending less than 50% of income.")
        elif expense_ratio < 0.7:
            score += 25
            score_breakdown['Expense Control'] = 25
            recommendations.append("✅ Good expense management, spending under 70%.")
        elif expense_ratio < 0.85:
            score += 15
            score_breakdown['Expense Control'] = 15
            recommendations.append("⚠️ Moderate spending. Try to reduce expenses below 70%.")
        else:
            score += 5
            score_breakdown['Expense Control'] = 5
            recommendations.append("❌ High spending rate. Review and cut unnecessary expenses.")
    
    # 2. Savings Rate (30 points)
    savings_rate = (available_balance / total_income * 100) if total_income > 0 else 0
    if savings_rate >= 30:
        score += 30
        score_breakdown['Savings Rate'] = 30
        recommendations.append("✅ Outstanding savings rate! You're saving 30%+ of income.")
    elif savings_rate >= 20:
        score += 22
        score_breakdown['Savings Rate'] = 22
        recommendations.append("✅ Good savings rate at 20%+.")
    elif savings_rate >= 10:
        score += 15
        score_breakdown['Savings Rate'] = 15
        recommendations.append("⚠️ Moderate savings. Aim for 20%+ savings rate.")
    elif savings_rate > 0:
        score += 8
        score_breakdown['Savings Rate'] = 8
        recommendations.append("⚠️ Low savings rate. Increase to at least 10%.")
    else:
        score_breakdown['Savings Rate'] = 0
        recommendations.append("❌ No savings. Start saving at least 10% of income.")
    
    # 3. Goal Setting (20 points)
    if total_saved_in_goals > 0:
        score += 20
        score_breakdown['Goal Planning'] = 20
        recommendations.append("✅ Great! You're actively working towards financial goals.")
    elif goals_list:
        score += 10
        score_breakdown['Goal Planning'] = 10
        recommendations.append("⚠️ Goals set but not funded. Start allocating money to goals.")
    else:
        score_breakdown['Goal Planning'] = 0
        recommendations.append("❌ Set financial goals to stay motivated and focused.")
    
    # 4. Income Diversity (15 points)
    if income_list:
        unique_sources = len(set(item['source'] for item in income_list))
        if unique_sources >= 3:
            score += 15
            score_breakdown['Income Diversity'] = 15
            recommendations.append("✅ Excellent income diversification with 3+ sources!")
        elif unique_sources >= 2:
            score += 10
            score_breakdown['Income Diversity'] = 10
            recommendations.append("✅ Good, you have 2 income sources.")
        else:
            score += 5
            score_breakdown['Income Diversity'] = 5
            recommendations.append("⚠️ Consider diversifying with additional income streams.")
    
    # Determine rating and color
    if score >= 85:
        color = '#2ecc71'
        rating = 'Excellent 🌟'
        emoji = '🎉'
    elif score >= 70:
        color = '#3498db'
        rating = 'Very Good 👍'
        emoji = '😊'
    elif score >= 55:
        color = '#f39c12'
        rating = 'Good 👌'
        emoji = '🙂'
    elif score >= 40:
        color = '#e67e22'
        rating = 'Fair ⚠️'
        emoji = '😐'
    else:
        color = '#e74c3c'
        rating = 'Needs Improvement 📈'
        emoji = '😟'
    
    # Gauge Chart
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={
            'text': f"<b>Financial Health Score</b><br><span style='font-size:0.7em;color:gray'>{rating}</span>",
            'font': {'size': 20}
        },
        delta={'reference': 75, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 2, 'tickcolor': "darkblue"},
            'bar': {'color': color, 'thickness': 0.75},
            'bgcolor': "white",
            'borderwidth': 3,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 40], 'color': '#ffcdd2'},
                {'range': [40, 55], 'color': '#fff9c4'},
                {'range': [55, 70], 'color': '#c8e6c9'},
                {'range': [70, 85], 'color': '#a5d6a7'},
                {'range': [85, 100], 'color': '#81c784'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig_gauge.update_layout(
        height=400,
        font={'family': "Arial", 'size': 14}
    )
    
    st.plotly_chart(fig_gauge, use_container_width=True, key="health_gauge")
    
    # Score breakdown
    st.markdown("### 📊 Score Breakdown")
    breakdown_df = pd.DataFrame(list(score_breakdown.items()), columns=['Category', 'Points'])
    
    fig_breakdown = go.Figure(data=[
        go.Bar(
            y=breakdown_df['Category'],
            x=breakdown_df['Points'],
            orientation='h',
            marker=dict(
                color=breakdown_df['Points'],
                colorscale=[[0, '#e74c3c'], [0.5, '#f39c12'], [1, '#2ecc71']],
                showscale=False,
                line=dict(color='black', width=1)
            ),
            text=breakdown_df['Points'],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Points: %{x}<extra></extra>'
        )
    ])
    
    fig_breakdown.update_layout(
        xaxis_title='Points Earned',
        height=300,
        showlegend=False
    )
    
    st.plotly_chart(fig_breakdown, use_container_width=True, key="score_breakdown")

with col2:
    st.markdown("### 🎯 Your Score")
    st.markdown(f"<h1 style='text-align: center; color: {color};'>{score}/100 {emoji}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>{rating}</h3>", unsafe_allow_html=True)
    
    st.markdown("### 📈 Rating Scale")
    st.markdown("""
    - **85-100:** Excellent 🌟
    - **70-84:** Very Good 👍
    - **55-69:** Good 👌
    - **40-54:** Fair ⚠️
    - **0-39:** Needs Work 📈
    """)

with col3:
    st.markdown("### 💡 Recommendations")
    for rec in recommendations:
        if '✅' in rec:
            st.success(rec)
        elif '⚠️' in rec:
            st.warning(rec)
        else:
            st.error(rec)

st.markdown("---")

# ===========================
# SECTION 10: TOP TRANSACTIONS & INSIGHTS
# ===========================
st.markdown("## 🔝 Transaction Highlights & Insights")

col1, col2 = st.columns(2)

with col1:
    if expense_list:
        st.markdown("### 💸 Top 10 Highest Expenses")
        expense_df = pd.DataFrame(expense_list)
        top_expenses = expense_df.nlargest(10, 'amount')
        
        for idx, row in top_expenses.iterrows():
            with st.container():
                col_a, col_b, col_c = st.columns([2, 1, 1])
                with col_a:
                    st.markdown(f"**{row['category']}**")
                    st.caption(row.get('description', 'No description'))
                with col_b:
                    st.metric("Amount", f"₹{row['amount']:,.2f}")
                with col_c:
                    st.caption(row['date'])
                st.markdown("---")

with col2:
    if expense_list:
        st.markdown("### 📊 Spending Insights")
        
        expense_df = pd.DataFrame(expense_list)
        
        # Insight 1: Most frequent category
        most_frequent_cat = expense_df['category'].mode()[0]
        freq_count = len(expense_df[expense_df['category'] == most_frequent_cat])
        st.info(f"🔄 **Most Frequent Category:** {most_frequent_cat} ({freq_count} transactions)")
        
        # Insight 2: Highest single expense
        highest_expense = expense_df.loc[expense_df['amount'].idxmax()]
        st.warning(f"💰 **Largest Single Expense:** ₹{highest_expense['amount']:,.2f} in {highest_expense['category']}")
        
        # Insight 3: Average transaction value
        avg_transaction = expense_df['amount'].mean()
        st.success(f"📊 **Average Transaction:** ₹{avg_transaction:,.2f}")
        
        # Insight 4: Spending velocity
        if len(expense_df) > 1:
            expense_df['date'] = pd.to_datetime(expense_df['date'])
            date_range = (expense_df['date'].max() - expense_df['date'].min()).days
            if date_range > 0:
                transactions_per_day = len(expense_df) / date_range
                st.info(f"⚡ **Transaction Frequency:** {transactions_per_day:.2f} transactions/day")
        
        # Insight 5: Budget alerts
        if expense_list:
            top_category = expense_df.groupby('category')['amount'].sum().idxmax()
            top_category_spend = expense_df.groupby('category')['amount'].sum().max()
            top_category_pct = (top_category_spend / total_expense * 100)
            
            if top_category_pct > 50:
                st.error(f"⚠️ **Alert:** {top_category} consumes {top_category_pct:.1f}% of your budget!")
            elif top_category_pct > 35:
                st.warning(f"⚠️ {top_category} is {top_category_pct:.1f}% of total expenses")

st.markdown("---")

# ===========================
# SECTION 11: COMPARATIVE ANALYSIS
# ===========================
if expense_list and len(expense_list) > 10:
    st.markdown("## 📊 Comparative & Trend Analysis")
    
    expense_df = pd.DataFrame(expense_list)
    expense_df['date'] = pd.to_datetime(expense_df['date'])
    expense_df['month'] = expense_df['date'].dt.to_period('M').astype(str)
    
    # Month-over-month comparison
    monthly_totals = expense_df.groupby('month')['amount'].sum().reset_index()
    if len(monthly_totals) > 1:
        monthly_totals['change'] = monthly_totals['amount'].pct_change() * 100
        monthly_totals['change_abs'] = monthly_totals['amount'].diff()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Month-over-Month Growth")
            fig_mom = go.Figure()
            
            colors = ['red' if x > 0 else 'green' for x in monthly_totals['change'].fillna(0)]
            
            fig_mom.add_trace(go.Bar(
                x=monthly_totals['month'],
                y=monthly_totals['change'].fillna(0),
                marker_color=colors,
                text=[f"{v:.1f}%" for v in monthly_totals['change'].fillna(0)],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Change: %{y:.2f}%<extra></extra>'
            ))
            
            fig_mom.update_layout(
                title='Monthly Spending Change (%)',
                yaxis_title='Change (%)',
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig_mom, use_container_width=True, key="mom_growth")
        
        with col2:
            st.markdown("### 💰 Monthly Spending Trend")
            fig_trend = go.Figure()
            
            fig_trend.add_trace(go.Scatter(
                x=monthly_totals['month'],
                y=monthly_totals['amount'],
                mode='lines+markers',
                name='Monthly Total',
                line=dict(color='#e74c3c', width=3),
                marker=dict(size=10, color='white', line=dict(color='#e74c3c', width=2)),
                fill='tozeroy',
                fillcolor='rgba(231, 76, 60, 0.2)',
                hovertemplate='<b>%{x}</b><br>₹%{y:,.2f}<extra></extra>'
            ))
            
            # Add trend line
            from sklearn.linear_model import LinearRegression
            import warnings
            warnings.filterwarnings('ignore')
            
            X = np.arange(len(monthly_totals)).reshape(-1, 1)
            y = monthly_totals['amount'].values
            model = LinearRegression()
            model.fit(X, y)
            trend_line = model.predict(X)
            
            fig_trend.add_trace(go.Scatter(
                x=monthly_totals['month'],
                y=trend_line,
                mode='lines',
                name='Trend',
                line=dict(color='#3498db', width=2, dash='dash'),
                hovertemplate='<b>Trend</b><br>₹%{y:,.2f}<extra></extra>'
            ))
            
            fig_trend.update_layout(
                title='Monthly Spending with Trend Line',
                yaxis_title='Amount (₹)',
                height=400,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig_trend, use_container_width=True, key="trend_analysis")

st.markdown("---")

# ===========================
# SECTION 12: EXPORT & DOWNLOAD
# ===========================
st.markdown("## 📥 Export Your Financial Data")

col1, col2, col3 = st.columns(3)

with col1:
    if expense_list:
        @st.cache_data
        def convert_expenses_to_csv():
            df = pd.DataFrame(expense_list)
            return df.to_csv(index=False).encode('utf-8')
        
        csv_expenses = convert_expenses_to_csv()
        st.download_button(
            label="📥 Download Expenses (CSV)",
            data=csv_expenses,
            file_name=f"expenses_{user_id}_{datetime.now().date()}.csv",
            mime='text/csv',
            help="Download all expense records"
        )

with col2:
    if income_list:
        @st.cache_data
        def convert_income_to_csv():
            df = pd.DataFrame(income_list)
            return df.to_csv(index=False).encode('utf-8')
        
        csv_income = convert_income_to_csv()
        st.download_button(
            label="📥 Download Income (CSV)",
            data=csv_income,
            file_name=f"income_{user_id}_{datetime.now().date()}.csv",
            mime='text/csv',
            help="Download all income records"
        )

with col3:
    if goals_list:
        @st.cache_data
        def convert_goals_to_csv():
            df = pd.DataFrame(goals_list)
            return df.to_csv(index=False).encode('utf-8')
        
        csv_goals = convert_goals_to_csv()
        st.download_button(
            label="📥 Download Goals (CSV)",
            data=csv_goals,
            file_name=f"goals_{user_id}_{datetime.now().date()}.csv",
            mime='text/csv',
            help="Download all savings goals"
        )

st.markdown("---")

# ===========================
# FOOTER WITH TIPS
# ===========================
st.markdown("""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            padding: 30px; 
            border-radius: 15px; 
            color: white; 
            text-align: center;
            margin-top: 20px;'>
    <h3>💡 Interactive Dashboard Tips</h3>
    <p style='font-size: 16px;'>
        <b>Hover</b> over charts for detailed information | 
        <b>Click & Drag</b> to zoom | 
        <b>Double-click</b> to reset view | 
        <b>Click legend</b> items to show/hide data
    </p>
    <p style='font-size: 14px; margin-top: 15px;'>
        🎯 Use sidebar filters to analyze specific periods | 
        📊 All charts update in real-time | 
        💾 Download your data anytime
    </p>
</div>
""", unsafe_allow_html=True)
