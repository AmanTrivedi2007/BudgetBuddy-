import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)

st.title("📊 Spending Visualization")

# Initialize session states
if 'income_list' not in st.session_state:
    st.session_state.income_list = []
if 'expense_list' not in st.session_state:
    st.session_state.expense_list = []
if 'goals_list' not in st.session_state:
    st.session_state.goals_list = []

# Calculate totals
total_income = sum(item['amount'] for item in st.session_state.income_list)
total_expense = sum(item['amount'] for item in st.session_state.expense_list)
total_saved_in_goals = sum(goal['saved_amount'] for goal in st.session_state.goals_list)
available_balance = total_income - total_expense - total_saved_in_goals

# Financial Overview Cards
st.subheader("💰 Financial Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Income", f"₹{total_income:,.2f}")
with col2:
    st.metric("Total Expenses", f"₹{total_expense:,.2f}")
with col3:
    st.metric("In Goals", f"₹{total_saved_in_goals:,.2f}")
with col4:
    st.metric("Available", f"₹{available_balance:,.2f}")

st.markdown("---")

# Check if data exists
if not st.session_state.expense_list and not st.session_state.income_list:
    st.info("📝 No data to visualize yet. Add some income and expenses first!")
    st.stop()

# SECTION 1: Expense by Category (Pie Chart)
if st.session_state.expense_list:
    st.subheader("🍰 Expenses by Category")
    
    # Calculate expenses by category
    expense_df = pd.DataFrame(st.session_state.expense_list)
    category_totals = expense_df.groupby('category')['amount'].sum().reset_index()
    category_totals = category_totals.sort_values('amount', ascending=False)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Pie Chart
        fig, ax = plt.subplots(figsize=(8, 8))
        colors = sns.color_palette("Set3", len(category_totals))
        
        wedges, texts, autotexts = ax.pie(
            category_totals['amount'],
            labels=category_totals['category'],
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            textprops={'fontsize': 10, 'weight': 'bold'}
        )
        
        # Make percentage text more readable
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(11)
        
        ax.set_title('Expense Distribution by Category', fontsize=14, weight='bold', pad=20)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    with col2:
        st.markdown("### Category Breakdown")
        for _, row in category_totals.iterrows():
            percentage = (row['amount'] / total_expense * 100)
            st.write(f"**{row['category']}**")
            st.progress(percentage / 100)
            st.write(f"₹{row['amount']:,.2f} ({percentage:.1f}%)")
            st.write("")

st.markdown("---")

# SECTION 2: Income vs Expenses (Bar Chart)
st.subheader("📊 Income vs Expenses Comparison")

col1, col2 = st.columns([3, 1])

with col1:
    # Create comparison bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    
    categories = ['Income', 'Expenses', 'Saved in Goals', 'Available']
    amounts = [total_income, total_expense, total_saved_in_goals, available_balance]
    colors = ['#2ecc71', '#e74c3c', '#3498db', '#f39c12']
    
    bars = ax.bar(categories, amounts, color=colors, edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'₹{height:,.0f}',
                ha='center', va='bottom', fontsize=11, weight='bold')
    
    ax.set_ylabel('Amount (₹)', fontsize=12, weight='bold')
    ax.set_title('Financial Overview', fontsize=14, weight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col2:
    st.markdown("### Summary")
    savings_rate = (available_balance / total_income * 100) if total_income > 0 else 0
    expense_rate = (total_expense / total_income * 100) if total_income > 0 else 0
    
    st.metric("Expense Rate", f"{expense_rate:.1f}%")
    st.metric("Savings Rate", f"{savings_rate:.1f}%")
    
    if expense_rate > 80:
        st.error("⚠️ High spending!")
    elif expense_rate > 60:
        st.warning("⚠️ Moderate spending")
    else:
        st.success("✅ Good savings!")

st.markdown("---")

# SECTION 3: Income Sources Breakdown
if st.session_state.income_list:
    st.subheader("💵 Income Sources Breakdown")
    
    income_df = pd.DataFrame(st.session_state.income_list)
    income_by_source = income_df.groupby('source')['amount'].sum().reset_index()
    income_by_source = income_by_source.sort_values('amount', ascending=True)
    
    # Horizontal bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.barh(income_by_source['source'], income_by_source['amount'], 
                   color=sns.color_palette("Greens_r", len(income_by_source)),
                   edgecolor='black', linewidth=1.2)
    
    # Add value labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2.,
                f'₹{width:,.0f}',
                ha='left', va='center', fontsize=10, weight='bold', 
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    ax.set_xlabel('Amount (₹)', fontsize=12, weight='bold')
    ax.set_title('Income by Source', fontsize=14, weight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

st.markdown("---")

# SECTION 4: Spending Trends Over Time (Line Chart)
if st.session_state.expense_list:
    st.subheader("📈 Spending Trends Over Time")
    
    expense_df = pd.DataFrame(st.session_state.expense_list)
    expense_df['date'] = pd.to_datetime(expense_df['date'])
    
    # Daily spending
    daily_spending = expense_df.groupby('date')['amount'].sum().reset_index()
    daily_spending = daily_spending.sort_values('date')
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(daily_spending['date'], daily_spending['amount'], 
            marker='o', linewidth=2.5, markersize=8, color='#e74c3c',
            markerfacecolor='white', markeredgewidth=2, markeredgecolor='#e74c3c')
    
    ax.fill_between(daily_spending['date'], daily_spending['amount'], 
                     alpha=0.3, color='#e74c3c')
    
    ax.set_xlabel('Date', fontsize=12, weight='bold')
    ax.set_ylabel('Amount (₹)', fontsize=12, weight='bold')
    ax.set_title('Daily Spending Trend', fontsize=14, weight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

st.markdown("---")

# SECTION 5: Category-wise Spending Details
if st.session_state.expense_list:
    st.subheader("📊 Category-wise Spending Details")
    
    expense_df = pd.DataFrame(st.session_state.expense_list)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 5 expenses
        st.markdown("### 💸 Top 5 Highest Expenses")
        top_expenses = expense_df.nlargest(5, 'amount')
        for idx, row in top_expenses.iterrows():
            with st.container():
                st.write(f"**{row['category']}** - ₹{row['amount']:,.2f}")
                st.caption(f"{row['date']} | {row.get('description', 'No description')}")
                st.write("")
    
    with col2:
        # Average spending by category
        st.markdown("### 📊 Average Spending per Category")
        avg_by_category = expense_df.groupby('category')['amount'].mean().reset_index()
        avg_by_category = avg_by_category.sort_values('amount', ascending=False)
        
        for _, row in avg_by_category.iterrows():
            st.write(f"**{row['category']}**")
            st.write(f"₹{row['amount']:,.2f} avg")
            st.write("")

st.markdown("---")

# SECTION 6: Heatmap of Spending by Category
if st.session_state.expense_list:
    st.subheader("🔥 Category Spending Heatmap")
    
    expense_df = pd.DataFrame(st.session_state.expense_list)
    expense_df['date'] = pd.to_datetime(expense_df['date'])
    expense_df['month'] = expense_df['date'].dt.to_period('M').astype(str)
    
    # Create pivot table
    heatmap_data = expense_df.pivot_table(
        values='amount',
        index='category',
        columns='month',
        aggfunc='sum',
        fill_value=0
    )
    
    if not heatmap_data.empty and len(heatmap_data.columns) > 0:
        fig, ax = plt.subplots(figsize=(12, 6))
        
        sns.heatmap(heatmap_data, annot=True, fmt='.0f', cmap='Reds',
                   cbar_kws={'label': 'Amount (₹)'}, linewidths=0.5,
                   linecolor='gray', ax=ax)
        
        ax.set_title('Monthly Spending by Category', fontsize=14, weight='bold', pad=20)
        ax.set_xlabel('Month', fontsize=12, weight='bold')
        ax.set_ylabel('Category', fontsize=12, weight='bold')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

st.markdown("---")

# SECTION 7: Savings Goals Progress
if st.session_state.goals_list:
    st.subheader("🎯 Savings Goals Progress")
    
    # Prepare data
    goals_data = []
    for goal in st.session_state.goals_list:
        progress = (goal['saved_amount'] / goal['target_amount'] * 100) if goal['target_amount'] > 0 else 0
        goals_data.append({
            'Goal': goal['name'],
            'Saved': goal['saved_amount'],
            'Remaining': goal['target_amount'] - goal['saved_amount'],
            'Target': goal['target_amount']
        })
    
    goals_df = pd.DataFrame(goals_data)
    
    # Stacked horizontal bar chart
    fig, ax = plt.subplots(figsize=(12, len(goals_data) * 1.5))
    
    y_pos = np.arange(len(goals_df))
    
    # Plot saved amount
    bars1 = ax.barh(y_pos, goals_df['Saved'], label='Saved', 
                    color='#2ecc71', edgecolor='black', linewidth=1.2)
    
    # Plot remaining amount
    bars2 = ax.barh(y_pos, goals_df['Remaining'], left=goals_df['Saved'],
                    label='Remaining', color='#ecf0f1', 
                    edgecolor='black', linewidth=1.2)
    
    # Add value labels
    for i, (saved, remaining) in enumerate(zip(goals_df['Saved'], goals_df['Remaining'])):
        # Saved amount label
        if saved > 0:
            ax.text(saved/2, i, f'₹{saved:,.0f}',
                   ha='center', va='center', fontsize=10, weight='bold')
        # Remaining amount label
        if remaining > 0:
            ax.text(saved + remaining/2, i, f'₹{remaining:,.0f}',
                   ha='center', va='center', fontsize=10)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(goals_df['Goal'])
    ax.set_xlabel('Amount (₹)', fontsize=12, weight='bold')
    ax.set_title('Goals Progress', fontsize=14, weight='bold', pad=20)
    ax.legend(loc='upper right')
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

st.markdown("---")

# SECTION 8: Monthly Summary
if st.session_state.expense_list or st.session_state.income_list:
    st.subheader("📅 Monthly Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.income_list:
            income_df = pd.DataFrame(st.session_state.income_list)
            income_df['date'] = pd.to_datetime(income_df['date'])
            income_df['month'] = income_df['date'].dt.to_period('M').astype(str)
            monthly_income = income_df.groupby('month')['amount'].sum().reset_index()
            
            fig, ax = plt.subplots(figsize=(8, 5))
            bars = ax.bar(monthly_income['month'], monthly_income['amount'],
                         color=sns.color_palette("Greens", len(monthly_income)),
                         edgecolor='black', linewidth=1.2)
            
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'₹{height:,.0f}',
                       ha='center', va='bottom', fontsize=9, weight='bold')
            
            ax.set_xlabel('Month', fontsize=11, weight='bold')
            ax.set_ylabel('Amount (₹)', fontsize=11, weight='bold')
            ax.set_title('Monthly Income', fontsize=12, weight='bold', pad=15)
            plt.xticks(rotation=45)
            ax.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
    
    with col2:
        if st.session_state.expense_list:
            expense_df = pd.DataFrame(st.session_state.expense_list)
            expense_df['date'] = pd.to_datetime(expense_df['date'])
            expense_df['month'] = expense_df['date'].dt.to_period('M').astype(str)
            monthly_expense = expense_df.groupby('month')['amount'].sum().reset_index()
            
            fig, ax = plt.subplots(figsize=(8, 5))
            bars = ax.bar(monthly_expense['month'], monthly_expense['amount'],
                         color=sns.color_palette("Reds", len(monthly_expense)),
                         edgecolor='black', linewidth=1.2)
            
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'₹{height:,.0f}',
                       ha='center', va='bottom', fontsize=9, weight='bold')
            
            ax.set_xlabel('Month', fontsize=11, weight='bold')
            ax.set_ylabel('Amount (₹)', fontsize=11, weight='bold')
            ax.set_title('Monthly Expenses', fontsize=12, weight='bold', pad=15)
            plt.xticks(rotation=45)
            ax.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

st.markdown("---")

# SECTION 9: Financial Health Score
st.subheader("💯 Financial Health Score")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    # Calculate health score
    score = 0
    reasons = []
    
    # Income vs Expense ratio (40 points)
    if total_income > 0:
        expense_ratio = total_expense / total_income
        if expense_ratio < 0.5:
            score += 40
            reasons.append("✅ Excellent expense control")
        elif expense_ratio < 0.7:
            score += 30
            reasons.append("✅ Good expense management")
        elif expense_ratio < 0.9:
            score += 20
            reasons.append("⚠️ Moderate spending")
        else:
            score += 10
            reasons.append("❌ High spending rate")
    
    # Savings goals (30 points)
    if total_saved_in_goals > 0:
        score += 30
        reasons.append("✅ Active savings goals")
    else:
        reasons.append("⚠️ No active savings goals")
    
    # Number of income sources (15 points)
    if st.session_state.income_list:
        unique_sources = len(set(item['source'] for item in st.session_state.income_list))
        if unique_sources >= 3:
            score += 15
            reasons.append("✅ Multiple income sources")
        elif unique_sources >= 2:
            score += 10
            reasons.append("✅ Two income sources")
        else:
            score += 5
            reasons.append("⚠️ Single income source")
    
    # Positive balance (15 points)
    if available_balance > 0:
        score += 15
        reasons.append("✅ Positive balance")
    else:
        reasons.append("❌ Negative balance")
    
    # Display score with gauge-like visualization
    fig, ax = plt.subplots(figsize=(8, 4), subplot_kw=dict(aspect="equal"))
    
    # Determine color based on score
    if score >= 80:
        color = '#2ecc71'
        rating = 'Excellent'
    elif score >= 60:
        color = '#3498db'
        rating = 'Good'
    elif score >= 40:
        color = '#f39c12'
        rating = 'Fair'
    else:
        color = '#e74c3c'
        rating = 'Needs Attention'
    
    # Create circular progress
    wedges, texts = ax.pie([score, 100-score], 
                           colors=[color, '#ecf0f1'],
                           startangle=90,
                           counterclock=False)
    
    # Add score text in center
    ax.text(0, 0, f'{score}\n{rating}', 
           ha='center', va='center',
           fontsize=24, weight='bold')
    
    ax.set_title('Financial Health Score', fontsize=14, weight='bold', pad=20)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col2:
    st.markdown("### Score Breakdown")
    for reason in reasons:
        st.write(reason)

with col3:
    st.markdown("### Rating")
    if score >= 80:
        st.success("🌟 Excellent")
        st.write("Great financial habits!")
    elif score >= 60:
        st.info("👍 Good")
        st.write("You're on the right track!")
    elif score >= 40:
        st.warning("⚠️ Fair")
        st.write("Room for improvement")
    else:
        st.error("❌ Needs Attention")
        st.write("Focus on savings!")

st.markdown("---")

# Export data
st.subheader("📥 Export Data")

col1, col2 = st.columns(2)

with col1:
    if st.session_state.expense_list:
        @st.cache_data
        def convert_expenses_to_csv():
            df = pd.DataFrame(st.session_state.expense_list)
            return df.to_csv(index=False).encode('utf-8')
        
        csv_expenses = convert_expenses_to_csv()
        st.download_button(
            label="📥 Download Expense Data",
            data=csv_expenses,
            file_name=f"expenses_{datetime.now().date()}.csv",
            mime='text/csv',
        )

with col2:
    if st.session_state.income_list:
        @st.cache_data
        def convert_income_to_csv():
            df = pd.DataFrame(st.session_state.income_list)
            return df.to_csv(index=False).encode('utf-8')
        
        csv_income = convert_income_to_csv()
        st.download_button(
            label="📥 Download Income Data",
            data=csv_income,
            file_name=f"income_{datetime.now().date()}.csv",
            mime='text/csv',
        )
