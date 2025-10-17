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
    get_all_income,
    get_all_expenses
)

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
        <div style="background-color: {color}; padding: 15px; border-radius: 10px; 
                    border-left: 5px solid {border}; margin-bottom: 15px;">
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 1])
        
        with col1:
            st.markdown(f"### {icon} {transaction['category']}")
            if transaction.get('description'):
                st.caption(f"📝 {transaction['description']}")
        
        with col2:
            st.markdown("**Amount**")
            st.markdown(f"₹{transaction['amount']:,.0f}")
        
        with col3:
            st.markdown("**Frequency**")
            st.markdown(f"🔁 {transaction['frequency']}")
        
        with col4:
            st.markdown("**Next Date**")
            st.markdown(f"📅 {transaction['next_date']}")
        
        # Days until next occurrence
        if days_until < 0:
            st.error(f"⚠️ Overdue by {abs(days_until)} days!")
        elif days_until == 0:
            st.success("🎯 Due today!")
        elif days_until <= 3:
            st.warning(f"⏰ Due in {days_until} days")
        else:
            st.info(f"📆 Due in {days_until} days")
        
        st.markdown("</div>", unsafe_allow_html=True)

# ===== PROCESS DUE TRANSACTIONS =====
due_count = process_recurring_transactions(user_id)
if due_count > 0:
    st.success(f"✅ Processed {due_count} recurring transaction(s) automatically!")

# ===== INFORMATION BOX - EXPLAIN THE SYSTEM =====
with st.expander("ℹ️ **How Recurring Transactions Work** (IMPORTANT - Please Read!)", expanded=False):
    st.markdown("""
    ### 📊 Understanding Recurring vs Manual Transactions
    
    **🔄 Recurring Transactions (This Page):**
    - Set up AUTOMATIC future transactions (salary, rent, bills)
    - System auto-adds them to Income/Expense on due date
    - Shows SCHEDULED transactions (not yet processed)
    
    **💰 Income & 💳 Expense Pages:**
    - Shows ALL completed transactions (manual + auto-processed)
    - Manual entries = one-time transactions
    - Auto entries = marked with "[Recurring]" tag
    
    ### ✅ How They Connect:
    
    ```
    You add recurring → Stored here → Auto-copies on due date → Shows in Income/Expense
    ```
    
    ### 📝 Example:
    1. **You add** "Salary ₹50,000 Monthly" here
    2. **On 1st of month** → System auto-adds to Income page
    3. **Income page shows** "[Recurring] Salary ₹50,000"
    4. **You manually add** "Bonus ₹10,000" in Income page
    5. **Income page shows both** recurring salary + manual bonus
    6. **This page shows** only the recurring salary (future schedule)
    
    ### 🎯 Key Points:
    - ✅ Recurring page = **Future scheduled** transactions
    - ✅ Income/Expense pages = **All actual** transactions
    - ✅ Manual entries won't show here (they're one-time!)
    - ✅ Look for "[Recurring]" tag in Income/Expense to see auto-processed ones
    """)

# ===== SHOW RECENTLY PROCESSED RECURRING TRANSACTIONS =====
st.markdown("---")
st.subheader("📌 Recently Auto-Processed Transactions")

# Get recent income and expenses
all_income = get_all_income(user_id)
all_expenses = get_all_expenses(user_id)

# Filter for recurring ones (with [Recurring] tag)
recent_recurring_income = [i for i in all_income if i.get('notes', '').startswith('[Recurring]')][:5]
recent_recurring_expenses = [e for e in all_expenses if e.get('description', '').startswith('[Recurring]')][:5]

if recent_recurring_income or recent_recurring_expenses:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 💵 Recent Auto-Processed Income")
        if recent_recurring_income:
            for income in recent_recurring_income:
                st.success(f"✅ {income['source']} - ₹{income['amount']:,.0f} on {income['date']}")
        else:
            st.info("No auto-processed income yet")
    
    with col2:
        st.markdown("##### 💳 Recent Auto-Processed Expenses")
        if recent_recurring_expenses:
            for expense in recent_recurring_expenses:
                st.error(f"✅ {expense['category']} - ₹{expense['amount']:,.0f} on {expense['date']}")
        else:
            st.info("No auto-processed expenses yet")
    
    st.caption("💡 These transactions were automatically added from your recurring schedule")
else:
    st.info("💡 No auto-processed transactions yet. Your scheduled transactions will appear here after processing.")

# ===== SECTION 1: ADD NEW RECURRING TRANSACTION WITH TABS =====
st.markdown("---")
st.subheader("➕ Add New Recurring Transaction")

# CREATE TWO TABS - ONE FOR INCOME, ONE FOR EXPENSE
income_tab, expense_tab = st.tabs(["💵 Add Recurring Income", "💳 Add Recurring Expense"])

# ===== INCOME TAB =====
with income_tab:
    with st.form("add_recurring_income_form", clear_on_submit=True):
        st.markdown("##### Recurring Income Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            income_category = st.selectbox(
                "Income Category*", 
                INCOME_CATEGORIES,
                help="Select the type of recurring income"
            )
        
        with col2:
            income_amount = st.number_input(
                "Amount (₹)*", 
                min_value=0.0, 
                value=5000.0, 
                step=100.0,
                help="Amount for each occurrence",
                key="income_amount"
            )
        
        col3, col4 = st.columns(2)
        
        with col3:
            income_frequency = st.selectbox(
                "Frequency*",
                ["Daily", "Weekly", "Monthly", "3 Months", "6 Months", "Yearly"],
                index=2,
                help="How often this income occurs",
                key="income_frequency"
            )
        
        with col4:
            income_start_date = st.date_input(
                "Start Date*",
                value=datetime.now().date(),
                help="When should this recurring income start?",
                key="income_start_date"
            )
        
        income_description = st.text_area(
            "Description (Optional)",
            placeholder="e.g., Monthly salary from ABC Company",
            help="Add any additional notes",
            key="income_description"
        )
        
        submit_income = st.form_submit_button("💾 Add Recurring Income", use_container_width=True, type="primary")
        
        if submit_income:
            if income_amount <= 0:
                st.error("❌ Amount must be greater than 0")
            else:
                success = add_recurring_transaction(
                    user_id=user_id,
                    trans_type="Income",
                    category=income_category,
                    amount=income_amount,
                    frequency=income_frequency,
                    start_date=income_start_date,
                    description=income_description
                )
                
                if success:
                    monthly_impact = calculate_monthly_equivalent(income_amount, income_frequency)
                    daily_impact = monthly_impact / 30
                    weekly_impact = monthly_impact / 4.33
                    yearly_impact = monthly_impact * 12
                    
                    st.success(f"✅ Recurring income added: **{income_category}** - ₹{income_amount:,.0f} ({income_frequency})")
                    st.info(f"🔔 This will automatically appear in your Income page starting {income_start_date}")
                    
                    # Show impact breakdown
                    st.markdown("##### 💰 Financial Impact Breakdown")
                    impact_col1, impact_col2, impact_col3, impact_col4 = st.columns(4)
                    
                    with impact_col1:
                        st.metric("📅 Daily", f"₹{daily_impact:,.0f}")
                    
                    with impact_col2:
                        st.metric("🗓️ Weekly", f"₹{weekly_impact:,.0f}")
                    
                    with impact_col3:
                        st.metric("📆 Monthly", f"₹{monthly_impact:,.0f}")
                    
                    with impact_col4:
                        st.metric("📅 Yearly", f"₹{yearly_impact:,.0f}")
                    
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Error adding recurring income")

# ===== EXPENSE TAB =====
with expense_tab:
    with st.form("add_recurring_expense_form", clear_on_submit=True):
        st.markdown("##### Recurring Expense Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            expense_category = st.selectbox(
                "Expense Category*", 
                EXPENSE_CATEGORIES,
                help="Select the type of recurring expense"
            )
        
        with col2:
            expense_amount = st.number_input(
                "Amount (₹)*", 
                min_value=0.0, 
                value=5000.0, 
                step=100.0,
                help="Amount for each occurrence",
                key="expense_amount"
            )
        
        col3, col4 = st.columns(2)
        
        with col3:
            expense_frequency = st.selectbox(
                "Frequency*",
                ["Daily", "Weekly", "Monthly", "3 Months", "6 Months", "Yearly"],
                index=2,
                help="How often this expense occurs",
                key="expense_frequency"
            )
        
        with col4:
            expense_start_date = st.date_input(
                "Start Date*",
                value=datetime.now().date(),
                help="When should this recurring expense start?",
                key="expense_start_date"
            )
        
        expense_description = st.text_area(
            "Description (Optional)",
            placeholder="e.g., Monthly rent payment",
            help="Add any additional notes",
            key="expense_description"
        )
        
        submit_expense = st.form_submit_button("💾 Add Recurring Expense", use_container_width=True, type="primary")
        
        if submit_expense:
            if expense_amount <= 0:
                st.error("❌ Amount must be greater than 0")
            else:
                success = add_recurring_transaction(
                    user_id=user_id,
                    trans_type="Expense",
                    category=expense_category,
                    amount=expense_amount,
                    frequency=expense_frequency,
                    start_date=expense_start_date,
                    description=expense_description
                )
                
                if success:
                    monthly_impact = calculate_monthly_equivalent(expense_amount, expense_frequency)
                    daily_impact = monthly_impact / 30
                    weekly_impact = monthly_impact / 4.33
                    yearly_impact = monthly_impact * 12
                    
                    st.success(f"✅ Recurring expense added: **{expense_category}** - ₹{expense_amount:,.0f} ({expense_frequency})")
                    st.info(f"🔔 This will automatically appear in your Expense page starting {expense_start_date}")
                    
                    # Show impact breakdown
                    st.markdown("##### 💸 Financial Impact Breakdown")
                    impact_col1, impact_col2, impact_col3, impact_col4 = st.columns(4)
                    
                    with impact_col1:
                        st.metric("📅 Daily", f"₹{daily_impact:,.0f}")
                    
                    with impact_col2:
                        st.metric("🗓️ Weekly", f"₹{weekly_impact:,.0f}")
                    
                    with impact_col3:
                        st.metric("📆 Monthly", f"₹{monthly_impact:,.0f}")
                    
                    with impact_col4:
                        st.metric("📅 Yearly", f"₹{yearly_impact:,.0f}")
                    
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Error adding recurring expense")

# ===== SECTION 2: RECURRING TRANSACTIONS OVERVIEW =====
st.markdown("---")
st.subheader("📊 Your Scheduled Recurring Transactions")
st.caption("💡 These are FUTURE transactions that will be auto-added to Income/Expense pages")

# Get all recurring transactions
recurring_transactions = get_all_recurring_transactions(user_id)

if recurring_transactions:
    # Separate into income and expenses
    recurring_income = [t for t in recurring_transactions if t['type'] == 'Income']
    recurring_expenses = [t for t in recurring_transactions if t['type'] == 'Expense']
    
    # Calculate totals
    total_monthly_income = sum([calculate_monthly_equivalent(t['amount'], t['frequency']) for t in recurring_income])
    total_monthly_expenses = sum([calculate_monthly_equivalent(t['amount'], t['frequency']) for t in recurring_expenses])
    net_monthly = total_monthly_income - total_monthly_expenses
    
    # Display summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="💵 Monthly Income",
            value=f"₹{total_monthly_income:,.0f}",
            help="Total recurring income per month"
        )
    
    with col2:
        st.metric(
            label="💳 Monthly Expenses",
            value=f"₹{total_monthly_expenses:,.0f}",
            delta=f"-₹{total_monthly_expenses:,.0f}",
            delta_color="inverse",
            help="Total recurring expenses per month"
        )
    
    with col3:
        st.metric(
            label="💰 Net Monthly",
            value=f"₹{net_monthly:,.0f}",
            delta=f"₹{net_monthly:,.0f}" if net_monthly >= 0 else f"-₹{abs(net_monthly):,.0f}",
            delta_color="normal" if net_monthly >= 0 else "inverse",
            help="Income minus expenses per month"
        )
    
    # Show status message
    if net_monthly > 0:
        st.success(f"✅ You have a positive cash flow of ₹{net_monthly:,.0f} per month from recurring transactions!")
    elif net_monthly < 0:
        st.error(f"⚠️ Your recurring expenses exceed income by ₹{abs(net_monthly):,.0f} per month!")
    else:
        st.info("ℹ️ Your recurring income and expenses are balanced.")
    
    # ===== TABS FOR INCOME AND EXPENSES =====
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs([f"💵 Income ({len(recurring_income)})", 
                                  f"💳 Expenses ({len(recurring_expenses)})", 
                                  "📊 Analytics"])
    
    with tab1:
        if recurring_income:
            st.markdown("### Scheduled Recurring Income")
            st.caption("🔔 These will be automatically added to your Income page on the due date")
            
            for transaction in recurring_income:
                display_transaction_card(transaction, 'Income')
                
                # Delete button
                if st.button(f"🗑️ Delete", key=f"del_inc_{transaction['id']}", type="secondary"):
                    if delete_recurring_transaction(transaction['id']):
                        st.success(f"✅ Deleted recurring income: {transaction['category']}")
                        st.rerun()
                    else:
                        st.error("❌ Error deleting transaction")
        else:
            st.info("💡 No recurring income set up yet. Add your salary, freelance income, or other regular income above!")
    
    with tab2:
        if recurring_expenses:
            st.markdown("### Scheduled Recurring Expenses")
            st.caption("🔔 These will be automatically added to your Expense page on the due date")
            
            for transaction in recurring_expenses:
                display_transaction_card(transaction, 'Expense')
                
                # Delete button
                if st.button(f"🗑️ Delete", key=f"del_exp_{transaction['id']}", type="secondary"):
                    if delete_recurring_transaction(transaction['id']):
                        st.success(f"✅ Deleted recurring expense: {transaction['category']}")
                        st.rerun()
                    else:
                        st.error("❌ Error deleting transaction")
        else:
            st.info("💡 No recurring expenses set up yet. Add your rent, subscriptions, EMIs, or other regular expenses above!")
    
    with tab3:
        st.markdown("### 📊 Recurring Transactions Analytics")
        
        # Create visualizations
        if len(recurring_transactions) > 0:
            viz_col1, viz_col2 = st.columns(2)
            
            with viz_col1:
                # Pie chart: Income categories
                if recurring_income:
                    st.markdown("##### Recurring Income Breakdown")
                    fig1, ax1 = plt.subplots(figsize=(6, 6))
                    
                    income_categories = [t['category'] for t in recurring_income]
                    income_amounts = [calculate_monthly_equivalent(t['amount'], t['frequency']) for t in recurring_income]
                    
                    ax1.pie(income_amounts, labels=income_categories, autopct='%1.1f%%', startangle=90)
                    ax1.axis('equal')
                    st.pyplot(fig1)
                    plt.close()
                else:
                    st.info("No recurring income to display")
            
            with viz_col2:
                # Pie chart: Expense categories
                if recurring_expenses:
                    st.markdown("##### Recurring Expenses Breakdown")
                    fig2, ax2 = plt.subplots(figsize=(6, 6))
                    
                    expense_categories = [t['category'] for t in recurring_expenses]
                    expense_amounts = [calculate_monthly_equivalent(t['amount'], t['frequency']) for t in recurring_expenses]
                    
                    ax2.pie(expense_amounts, labels=expense_categories, autopct='%1.1f%%', startangle=90)
                    ax2.axis('equal')
                    st.pyplot(fig2)
                    plt.close()
                else:
                    st.info("No recurring expenses to display")
            
            # Bar chart: Income vs Expenses comparison
            st.markdown("---")
            st.markdown("##### Monthly Recurring Cash Flow")
            
            fig3, ax3 = plt.subplots(figsize=(10, 6))
            
            categories = ['Income', 'Expenses', 'Net']
            amounts = [total_monthly_income, total_monthly_expenses, net_monthly]
            colors = ['#00AA00', '#FF4444', '#0088FF' if net_monthly >= 0 else '#FF4444']
            
            bars = ax3.bar(categories, amounts, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
            
            # Add value labels on bars
            for bar, amount in zip(bars, amounts):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'₹{amount:,.0f}', ha='center', va='bottom', fontweight='bold', fontsize=11)
            
            ax3.set_ylabel('Amount (₹)', fontweight='bold', fontsize=11)
            ax3.set_title('Monthly Recurring Transactions Summary', fontweight='bold', fontsize=13)
            ax3.grid(axis='y', alpha=0.3, linestyle='--')
            plt.tight_layout()
            st.pyplot(fig3)
            plt.close()
            
            # Detailed table
            st.markdown("---")
            st.markdown("##### Detailed Breakdown")
            
            # Create DataFrame
            df_data = []
            for t in recurring_transactions:
                monthly_equiv = calculate_monthly_equivalent(t['amount'], t['frequency'])
                df_data.append({
                    'Type': '💵 Income' if t['type'] == 'Income' else '💳 Expense',
                    'Category': t['category'],
                    'Amount': f"₹{t['amount']:,.0f}",
                    'Frequency': t['frequency'],
                    'Monthly Impact': f"₹{monthly_equiv:,.0f}",
                    'Next Date': t['next_date']
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

else:
    st.info("💡 **No recurring transactions yet!** Set up automatic tracking for regular income and expenses.")
    
    st.markdown("### 🎯 Why Use Recurring Transactions?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Common Recurring Income:**
        - 💼 Monthly Salary
        - 💰 Freelance Contracts
        - 🏠 Rental Income
        - 💹 Investment Returns
        - 🎁 Regular Allowances
        """)
    
    with col2:
        st.markdown("""
        **Common Recurring Expenses:**
        - 🏠 Rent/Mortgage
        - 📞 Phone & Internet Bills
        - 📺 Subscriptions (Netflix, Spotify)
        - 💰 Loan EMIs
        - 🏦 Insurance Premiums
        - 🏋️ Gym Membership
        """)

# Footer
st.markdown("---")
st.caption("🔄 Recurring Transactions | BudgetBuddy")
st.caption("💡 Set it once, track it automatically!")
