# recurring_transactions.py - Auto-add Salary, Rent, Subscriptions

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

# Import shared categories
from categories import EXPENSE_CATEGORIES, INCOME_CATEGORIES

# Set seaborn style
sns.set_style("whitegrid")

# Title
st.title("🔄 Recurring Transactions")
st.markdown("*Automate your regular income and expenses*")

# Get current user
if 'username' not in st.session_state or not st.session_state.username:
    st.error("⚠️ Please login first!")
    st.stop()

user_id = st.session_state.username

# Import database functions
from database import (
    get_all_recurring_transactions,
    add_recurring_transaction,
    delete_recurring_transaction,
    process_recurring_transactions,
    get_all_income,      # ADDED: Import for database sync
    get_all_expenses     # ADDED: Import for database sync
)

# ===== PROCESS PENDING RECURRING TRANSACTIONS =====
# Auto-process any transactions that are due
processed = process_recurring_transactions(user_id)
if processed > 0:
    st.success(f"✅ {processed} recurring transaction(s) processed automatically!")

# ===== HELPER FUNCTIONS =====
def calculate_monthly_equivalent(amount, frequency):
    """Convert any frequency to monthly amount"""
    if frequency == 'Daily':
        return amount * 30
    elif frequency == 'Weekly':
        return amount * 4.33
    elif frequency == 'Monthly':
        return amount
    elif frequency == '3 Months':
        return amount / 3
    elif frequency == '6 Months':
        return amount / 6
    elif frequency == 'Yearly':
        return amount / 12
    return amount

def display_transaction_card(transaction, trans_type):
    """Display a transaction card with details"""
    next_date = datetime.strptime(transaction['next_date'], '%Y-%m-%d').date()
    days_until = (next_date - datetime.now().date()).days
    
    if trans_type == 'Income':
        color = "#E6F9E6"
        border = "#00AA00"
        icon = "💵"
    else:
        color = "#FFE6E6"
        border = "#FF4444"
        icon = "💳"
    
    with st.container():
        st.markdown(f"""
        <div style='background-color: {color}; 
                    padding: 15px; 
                    border-radius: 10px; 
                    border-left: 5px solid {border};
                    margin-bottom: 10px;'>
            <h4 style='margin: 0;'>{icon} {transaction['category']}</h4>
            <p style='margin: 5px 0;'><b>Amount:</b> ₹{transaction['amount']:,.2f}</p>
            <p style='margin: 5px 0;'><b>Frequency:</b> {transaction['frequency']}</p>
            <p style='margin: 5px 0;'><b>Next Date:</b> {transaction['next_date']}</p>
            <p style='margin: 5px 0; color: {'green' if days_until > 7 else 'orange' if days_until > 0 else 'red'};'>
                <b>{'In ' + str(days_until) + ' days' if days_until > 0 else 'DUE TODAY!' if days_until == 0 else 'OVERDUE by ' + str(abs(days_until)) + ' days'}</b>
            </p>
            {f"<p style='margin: 5px 0;'><i>{transaction['description']}</i></p>" if transaction['description'] else ""}
        </div>
        """, unsafe_allow_html=True)

# ===== FETCH ALL DATA =====
recurring_transactions = get_all_recurring_transactions(user_id)

# CRITICAL FIX: Get income and expenses from DATABASE instead of session state
all_income_data = get_all_income(user_id)      # CHANGED: Fetch from database
all_expenses_data = get_all_expenses(user_id)  # CHANGED: Fetch from database

# Calculate totals from DATABASE
total_income = sum(item['amount'] for item in all_income_data)      # CHANGED: Use database data
total_expenses = sum(item['amount'] for item in all_expenses_data)  # CHANGED: Use database data

# Separate recurring transactions by type
recurring_income = [t for t in recurring_transactions if t['type'] == 'Income']
recurring_expenses = [t for t in recurring_transactions if t['type'] == 'Expense']

# Calculate monthly recurring amounts
monthly_recurring_income = sum(calculate_monthly_equivalent(t['amount'], t['frequency']) for t in recurring_income)
monthly_recurring_expenses = sum(calculate_monthly_equivalent(t['amount'], t['frequency']) for t in recurring_expenses)

# ===== DASHBOARD OVERVIEW =====
st.markdown("## 📊 Financial Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Income",
        f"₹{total_income:,.2f}",
        help="Total income from all sources (includes recurring)"
    )

with col2:
    st.metric(
        "Total Expenses",
        f"₹{total_expenses:,.2f}",
        help="Total expenses (includes recurring)"
    )

with col3:
    net_balance = total_income - total_expenses
    st.metric(
        "Net Balance",
        f"₹{net_balance:,.2f}",
        delta=f"{'Surplus' if net_balance >= 0 else 'Deficit'}",
        delta_color="normal" if net_balance >= 0 else "inverse",
        help="Income minus expenses"
    )

with col4:
    net_recurring = monthly_recurring_income - monthly_recurring_expenses
    st.metric(
        "Monthly Recurring Net",
        f"₹{net_recurring:,.2f}",
        help="Net monthly recurring income minus expenses"
    )

st.markdown("---")

# ===== MONTHLY SUMMARY =====
st.markdown("## 📅 Monthly Recurring Summary")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 💰 Recurring Income")
    st.metric("Monthly Equivalent", f"₹{monthly_recurring_income:,.2f}")
    st.caption(f"{len(recurring_income)} active recurring income(s)")
    
    if recurring_income:
        for trans in recurring_income:
            monthly_equiv = calculate_monthly_equivalent(trans['amount'], trans['frequency'])
            st.markdown(f"- **{trans['category']}**: ₹{trans['amount']:,.2f} ({trans['frequency']}) = ₹{monthly_equiv:,.2f}/month")

with col2:
    st.markdown("### 💳 Recurring Expenses")
    st.metric("Monthly Equivalent", f"₹{monthly_recurring_expenses:,.2f}")
    st.caption(f"{len(recurring_expenses)} active recurring expense(s)")
    
    if recurring_expenses:
        for trans in recurring_expenses:
            monthly_equiv = calculate_monthly_equivalent(trans['amount'], trans['frequency'])
            st.markdown(f"- **{trans['category']}**: ₹{trans['amount']:,.2f} ({trans['frequency']}) = ₹{monthly_equiv:,.2f}/month")

st.markdown("---")

# ===== ADD NEW RECURRING TRANSACTION =====
st.markdown("## ➕ Add New Recurring Transaction")

with st.form("add_recurring_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        trans_type = st.selectbox(
            "Type",
            ["Income", "Expense"],
            help="Choose whether this is recurring income or expense"
        )
        
        if trans_type == "Income":
            category = st.selectbox("Income Source", INCOME_CATEGORIES)
        else:
            category = st.selectbox("Expense Category", EXPENSE_CATEGORIES)
        
        amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            step=1.0,
            help="Enter the recurring amount"
        )
    
    with col2:
        frequency = st.selectbox(
            "Frequency",
            ["Daily", "Weekly", "Monthly", "3 Months", "6 Months", "Yearly"],
            index=2,
            help="How often does this transaction occur?"
        )
        
        start_date = st.date_input(
            "Start Date",
            value=datetime.now().date(),
            help="When should this recurring transaction start?"
        )
        
        description = st.text_input(
            "Description (Optional)",
            placeholder="e.g., Monthly salary, Netflix subscription, etc."
        )
    
    # Show monthly equivalent
    if amount > 0:
        monthly_equiv = calculate_monthly_equivalent(amount, frequency)
        st.info(f"💡 This equals approximately **₹{monthly_equiv:,.2f} per month**")
    
    submit = st.form_submit_button("➕ Add Recurring Transaction", use_container_width=True)
    
    if submit:
        if amount <= 0:
            st.error("❌ Amount must be greater than 0")
        elif not category:
            st.error("❌ Please select a category")
        else:
            success = add_recurring_transaction(
                user_id=user_id,
                trans_type=trans_type,
                category=category,
                amount=amount,
                frequency=frequency,
                start_date=str(start_date),
                description=description
            )
            
            if success:
                st.success(f"✅ Recurring {trans_type.lower()} added successfully!")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Failed to add recurring transaction. Please try again.")

st.markdown("---")

# ===== UPCOMING TRANSACTIONS =====
st.markdown("## 🔔 Upcoming Transactions (Next 7 Days)")

today = datetime.now().date()
upcoming_deadline = today + timedelta(days=7)

upcoming = [t for t in recurring_transactions if datetime.strptime(t['next_date'], '%Y-%m-%d').date() <= upcoming_deadline]

if upcoming:
    st.info(f"📌 You have **{len(upcoming)}** transaction(s) coming up in the next 7 days")
    
    for trans in sorted(upcoming, key=lambda x: x['next_date']):
        display_transaction_card(trans, trans['type'])
else:
    st.success("✅ No transactions due in the next 7 days")

st.markdown("---")

# ===== ALL RECURRING TRANSACTIONS =====
st.markdown("## 📋 All Recurring Transactions")

tab1, tab2, tab3 = st.tabs(["💵 Recurring Income", "💳 Recurring Expenses", "📊 All Transactions"])

with tab1:
    if recurring_income:
        st.success(f"**{len(recurring_income)}** active recurring income(s)")
        for trans in recurring_income:
            col1, col2 = st.columns([4, 1])
            with col1:
                display_transaction_card(trans, 'Income')
            with col2:
                st.write("")  # Spacing
                st.write("")  # Spacing
                if st.button(f"🗑️ Delete", key=f"delete_income_{trans['id']}", use_container_width=True):
                    if delete_recurring_transaction(trans['id']):
                        st.success("✅ Deleted!")
                        st.rerun()
                    else:
                        st.error("❌ Delete failed")
    else:
        st.info("💡 No recurring income set up yet. Add your salary or regular income above!")

with tab2:
    if recurring_expenses:
        st.warning(f"**{len(recurring_expenses)}** active recurring expense(s)")
        for trans in recurring_expenses:
            col1, col2 = st.columns([4, 1])
            with col1:
                display_transaction_card(trans, 'Expense')
            with col2:
                st.write("")  # Spacing
                st.write("")  # Spacing
                if st.button(f"🗑️ Delete", key=f"delete_expense_{trans['id']}", use_container_width=True):
                    if delete_recurring_transaction(trans['id']):
                        st.success("✅ Deleted!")
                        st.rerun()
                    else:
                        st.error("❌ Delete failed")
    else:
        st.info("💡 No recurring expenses set up yet. Add your rent, subscriptions, or bills above!")

with tab3:
    if recurring_transactions:
        # Create DataFrame for better display
        df_data = []
        for trans in recurring_transactions:
            monthly_equiv = calculate_monthly_equivalent(trans['amount'], trans['frequency'])
            next_date = datetime.strptime(trans['next_date'], '%Y-%m-%d').date()
            days_until = (next_date - today).days
            
            df_data.append({
                'Type': trans['type'],
                'Category': trans['category'],
                'Amount': f"₹{trans['amount']:,.2f}",
                'Frequency': trans['frequency'],
                'Monthly Equiv.': f"₹{monthly_equiv:,.2f}",
                'Next Date': trans['next_date'],
                'Days Until': days_until,
                'Description': trans['description'] or '-'
            })
        
        df = pd.DataFrame(df_data)
        
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
        
        # Download button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"recurring_transactions_{user_id}_{datetime.now().date()}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("💡 No recurring transactions set up yet")

st.markdown("---")

# ===== VISUALIZATION =====
if recurring_transactions:
    st.markdown("## 📊 Recurring Transactions Visualization")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly recurring by category
        st.markdown("### Monthly Recurring by Category")
        
        monthly_by_category = {}
        for trans in recurring_transactions:
            monthly_amount = calculate_monthly_equivalent(trans['amount'], trans['frequency'])
            category = trans['category']
            if category in monthly_by_category:
                monthly_by_category[category] += monthly_amount
            else:
                monthly_by_category[category] = monthly_amount
        
        fig, ax = plt.subplots(figsize=(10, 6))
        categories = list(monthly_by_category.keys())
        amounts = list(monthly_by_category.values())
        colors = sns.color_palette("husl", len(categories))
        
        ax.barh(categories, amounts, color=colors)
        ax.set_xlabel('Monthly Amount (₹)')
        ax.set_title('Monthly Recurring Amount by Category')
        ax.grid(axis='x', alpha=0.3)
        
        for i, v in enumerate(amounts):
            ax.text(v, i, f' ₹{v:,.0f}', va='center')
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    with col2:
        # Income vs Expense pie chart
        st.markdown("### Monthly Recurring: Income vs Expenses")
        
        fig, ax = plt.subplots(figsize=(8, 8))
        
        sizes = [monthly_recurring_income, monthly_recurring_expenses]
        labels = [f'Income\n₹{monthly_recurring_income:,.0f}', f'Expenses\n₹{monthly_recurring_expenses:,.0f}']
        colors = ['#00AA00', '#FF4444']
        explode = (0.1, 0)
        
        ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
               shadow=True, startangle=90, textprops={'fontsize': 12, 'weight': 'bold'})
        ax.axis('equal')
        ax.set_title('Monthly Recurring Income vs Expenses', fontsize=14, weight='bold')
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

st.markdown("---")

# ===== TIPS & INFO =====
with st.expander("💡 Tips for Managing Recurring Transactions"):
    st.markdown("""
    ### Best Practices:
    
    **Setting Up:**
    - ✅ Add your monthly salary as recurring income
    - ✅ Add rent, subscriptions (Netflix, Spotify), and bills
    - ✅ Set realistic start dates
    
    **Monitoring:**
    - 📊 Check "Upcoming Transactions" regularly
    - 🔔 Transactions process automatically on due date
    - 📈 Review the visualizations to see spending patterns
    
    **Managing:**
    - ✏️ Delete or pause subscriptions you no longer need
    - 💰 Use monthly equivalents to understand annual impact
    - 🎯 Plan your budget around recurring expenses
    
    **Examples:**
    - **Income**: Salary (Monthly), Freelance retainer (Monthly)
    - **Expenses**: Rent (Monthly), Netflix (Monthly), Gym (Yearly)
    
    **Automation:**
    - Transactions are automatically added to your income/expense records on the due date
    - Check your main income/expense pages to see processed transactions
    - The "Next Date" updates automatically after processing
    """)

# Footer
st.caption("💡 Recurring transactions are processed automatically. Check your Income/Expense pages to see them reflected in your totals.")
