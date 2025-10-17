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

def get_combined_recurring_totals(user_id):
    """Get COMBINED totals from recurring_transactions + income/expense tables"""
    # Get scheduled recurring transactions
    recurring_trans = get_all_recurring_transactions(user_id)
    recurring_income_list = [t for t in recurring_trans if t['type'] == 'Income']
    recurring_expense_list = [t for t in recurring_trans if t['type'] == 'Expense']
    
    # Calculate monthly equivalents for scheduled transactions
    scheduled_monthly_income = sum([calculate_monthly_equivalent(t['amount'], t['frequency']) for t in recurring_income_list])
    scheduled_monthly_expenses = sum([calculate_monthly_equivalent(t['amount'], t['frequency']) for t in recurring_expense_list])
    
    # Get ALL actual transactions from income/expense tables
    all_income = get_all_income(user_id)
    all_expenses = get_all_expenses(user_id)
    
    # Calculate total actual income/expenses (including recurring AND manual)
    total_actual_income = sum([i['amount'] for i in all_income])
    total_actual_expenses = sum([e['amount'] for e in all_expenses])
    
    return {
        'scheduled_monthly_income': scheduled_monthly_income,
        'scheduled_monthly_expenses': scheduled_monthly_expenses,
        'total_actual_income': total_actual_income,
        'total_actual_expenses': total_actual_expenses,
        'recurring_income_list': recurring_income_list,
        'recurring_expense_list': recurring_expense_list
    }

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

# ===== GET COMBINED DATA =====
combined_data = get_combined_recurring_totals(user_id)

# ===== SHOW COMBINED OVERVIEW WITH ALL DATA =====
st.markdown("---")
st.subheader("💰 Complete Financial Overview")
st.caption("Shows ALL income and expenses (recurring + manual)")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="💵 Total Income",
        value=f"₹{combined_data['total_actual_income']:,.0f}",
        help="All income (recurring + manual)"
    )
    st.caption(f"📆 Scheduled Monthly: ₹{combined_data['scheduled_monthly_income']:,.0f}")

with col2:
    st.metric(
        label="💳 Total Expenses",
        value=f"₹{combined_data['total_actual_expenses']:,.0f}",
        delta=f"-₹{combined_data['total_actual_expenses']:,.0f}",
        delta_color="inverse",
        help="All expenses (recurring + manual)"
    )
    st.caption(f"📆 Scheduled Monthly: ₹{combined_data['scheduled_monthly_expenses']:,.0f}")

with col3:
    net_total = combined_data['total_actual_income'] - combined_data['total_actual_expenses']
    st.metric(
        label="💰 Net Balance",
        value=f"₹{net_total:,.0f}",
        delta=f"₹{net_total:,.0f}" if net_total >= 0 else f"-₹{abs(net_total):,.0f}",
        delta_color="normal" if net_total >= 0 else "inverse",
        help="Total income minus total expenses"
    )
    net_monthly = combined_data['scheduled_monthly_income'] - combined_data['scheduled_monthly_expenses']
    st.caption(f"📆 Net Monthly Recurring: ₹{net_monthly:,.0f}")

# Show status message
if net_total > 0:
    st.success(f"✅ Your overall balance is positive at ₹{net_total:,.0f}!")
elif net_total < 0:
    st.error(f"⚠️ Your expenses exceed income by ₹{abs(net_total):,.0f}!")
else:
    st.info("ℹ️ Your income and expenses are balanced.")

# ===== SHOW BREAKDOWN =====
with st.expander("📊 Detailed Breakdown", expanded=False):
    breakdown_col1, breakdown_col2 = st.columns(2)
    
    with breakdown_col1:
        st.markdown("##### 💵 Income Breakdown")
        # Get recurring income count
        all_income = get_all_income(user_id)
        recurring_income_count = len([i for i in all_income if i.get('notes', '').startswith('[Recurring]')])
        manual_income_count = len(all_income) - recurring_income_count
        
        st.info(f"🔄 Recurring: {recurring_income_count} transactions")
        st.info(f"✍️ Manual: {manual_income_count} transactions")
        st.success(f"📊 Total: {len(all_income)} transactions")
    
    with breakdown_col2:
        st.markdown("##### 💳 Expense Breakdown")
        # Get recurring expense count
        all_expenses = get_all_expenses(user_id)
        recurring_expense_count = len([e for e in all_expenses if e.get('description', '').startswith('[Recurring]')])
        manual_expense_count = len(all_expenses) - recurring_expense_count
        
        st.info(f"🔄 Recurring: {recurring_expense_count} transactions")
        st.info(f"✍️ Manual: {manual_expense_count} transactions")
        st.error(f"📊 Total: {len(all_expenses)} transactions")

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

# ===== SECTION 2: SCHEDULED RECURRING TRANSACTIONS =====
st.markdown("---")
st.subheader("📅 Scheduled Recurring Transactions")
st.caption("💡 Future automatic transactions that will be added to Income/Expense")

# Get all recurring transactions
recurring_income_list = combined_data['recurring_income_list']
recurring_expense_list = combined_data['recurring_expense_list']

if recurring_income_list or recurring_expense_list:
    # ===== TABS FOR SCHEDULED TRANSACTIONS =====
    tab1, tab2 = st.tabs([f"💵 Income Schedule ({len(recurring_income_list)})", 
                           f"💳 Expense Schedule ({len(recurring_expense_list)})"])
    
    with tab1:
        if recurring_income_list:
            st.markdown("### Scheduled Recurring Income")
            
            for transaction in recurring_income_list:
                display_transaction_card(transaction, 'Income')
                
                # Delete button
                if st.button(f"🗑️ Delete", key=f"del_inc_{transaction['id']}", type="secondary"):
                    if delete_recurring_transaction(transaction['id']):
                        st.success(f"✅ Deleted recurring income: {transaction['category']}")
                        st.rerun()
                    else:
                        st.error("❌ Error deleting transaction")
        else:
            st.info("💡 No recurring income scheduled yet.")
    
    with tab2:
        if recurring_expense_list:
            st.markdown("### Scheduled Recurring Expenses")
            
            for transaction in recurring_expense_list:
                display_transaction_card(transaction, 'Expense')
                
                # Delete button
                if st.button(f"🗑️ Delete", key=f"del_exp_{transaction['id']}", type="secondary"):
                    if delete_recurring_transaction(transaction['id']):
                        st.success(f"✅ Deleted recurring expense: {transaction['category']}")
                        st.rerun()
                    else:
                        st.error("❌ Error deleting transaction")
        else:
            st.info("💡 No recurring expenses scheduled yet.")

else:
    st.info("💡 **No recurring transactions scheduled yet!** Set up automatic tracking for regular income and expenses.")

# Footer
st.markdown("---")
st.caption("🔄 Recurring Transactions | BudgetBuddy")
st.caption("💡 Set it once, track it automatically!")
