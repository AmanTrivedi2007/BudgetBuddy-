# recurring_transactions.py - Enterprise-Grade Recurring Transactions System
# Like Mint, YNAB, PocketGuard - Production Ready

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

# Import shared categories
from categories import EXPENSE_CATEGORIES, INCOME_CATEGORIES

# Set seaborn style
sns.set_style("whitegrid")

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

# ===== AUTO-PROCESS RECURRING TRANSACTIONS =====
# This runs EVERY TIME the page loads (like top apps do)
try:
    due_count = process_recurring_transactions(user_id)
    if due_count > 0:
        st.success(f"✅ Automatically processed {due_count} recurring transaction(s)!")
except Exception as e:
    st.error(f"⚠️ Error processing recurring transactions: {e}")

# ===== PAGE HEADER =====
st.title("🔄 Recurring Transactions")
st.markdown("*Automate your regular income and expenses - Like autopilot for your money!*")

# ===== HELPER FUNCTIONS =====

def calculate_monthly_equivalent(amount, frequency):
    """Convert any frequency to monthly amount"""
    conversions = {
        'Daily': amount * 30,
        'Weekly': amount * 4.33,
        'Monthly': amount,
        '3 Months': amount / 3,
        '6 Months': amount / 6,
        'Yearly': amount / 12
    }
    return conversions.get(frequency, amount)

def calculate_all_periods(amount, frequency):
    """Calculate daily, weekly, monthly, yearly amounts"""
    monthly = calculate_monthly_equivalent(amount, frequency)
    return {
        'daily': monthly / 30,
        'weekly': monthly / 4.33,
        'monthly': monthly,
        'yearly': monthly * 12
    }

def get_days_until(next_date_str):
    """Calculate days until next occurrence"""
    try:
        next_date = datetime.strptime(next_date_str, '%Y-%m-%d').date()
        today = datetime.now().date()
        return (next_date - today).days
    except:
        return 999

def display_transaction_card(transaction, trans_type):
    """Display beautiful transaction card (like Mint app)"""
    days_until = get_days_until(transaction['next_date'])
    
    # Color scheme
    if trans_type == 'Income':
        color = "#E8F5E9"
        border = "#4CAF50"
        icon = "💰"
    else:
        color = "#FFEBEE"
        border = "#F44336"
        icon = "💸"
    
    # Status badge color
    if days_until < 0:
        status_color = "#F44336"
        status_text = f"⚠️ OVERDUE ({abs(days_until)} days)"
    elif days_until == 0:
        status_color = "#FF9800"
        status_text = "🎯 DUE TODAY"
    elif days_until <= 3:
        status_color = "#FFC107"
        status_text = f"⏰ Due in {days_until} days"
    else:
        status_color = "#4CAF50"
        status_text = f"📅 Due in {days_until} days"
    
    # Card HTML
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {color} 0%, white 100%);
        padding: 20px;
        border-radius: 15px;
        border-left: 6px solid {border};
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="flex: 1;">
                <h3 style="margin: 0; color: #333;">{icon} {transaction['category']}</h3>
                <p style="margin: 5px 0; color: #666; font-size: 14px;">
                    {transaction.get('description', 'No description')}
                </p>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 28px; font-weight: bold; color: {border};">
                    ₹{transaction['amount']:,.0f}
                </div>
                <div style="font-size: 14px; color: #666;">
                    {transaction['frequency']}
                </div>
            </div>
        </div>
        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #ddd;">
            <span style="
                background-color: {status_color};
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 13px;
                font-weight: bold;
            ">{status_text}</span>
            <span style="margin-left: 15px; color: #666; font-size: 13px;">
                Next: {transaction['next_date']}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ===== SECTION 1: QUICK STATS DASHBOARD =====
st.markdown("---")
st.subheader("📊 Recurring Transactions Dashboard")

# Get all data
recurring_trans = get_all_recurring_transactions(user_id)
all_income = get_all_income(user_id)
all_expenses = get_all_expenses(user_id)

# Filter recurring transactions
recurring_income_list = [t for t in recurring_trans if t['type'] == 'Income']
recurring_expense_list = [t for t in recurring_trans if t['type'] == 'Expense']

# Calculate monthly totals
total_monthly_income = sum([calculate_monthly_equivalent(t['amount'], t['frequency']) for t in recurring_income_list])
total_monthly_expenses = sum([calculate_monthly_equivalent(t['amount'], t['frequency']) for t in recurring_expense_list])
net_monthly = total_monthly_income - total_monthly_expenses

# Count processed transactions
processed_income_count = len([i for i in all_income if '[Recurring]' in str(i.get('notes', ''))])
processed_expense_count = len([e for e in all_expenses if '[Recurring]' in str(e.get('description', ''))])

# Display metrics in beautiful cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #E8F5E9 0%, white 100%); padding: 20px; border-radius: 10px; border-left: 4px solid #4CAF50;">
        <div style="font-size: 14px; color: #666;">Monthly Income</div>
        <div style="font-size: 28px; font-weight: bold; color: #4CAF50;">₹{total_monthly_income:,.0f}</div>
        <div style="font-size: 12px; color: #666; margin-top: 5px;">{len(recurring_income_list)} scheduled</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #FFEBEE 0%, white 100%); padding: 20px; border-radius: 10px; border-left: 4px solid #F44336;">
        <div style="font-size: 14px; color: #666;">Monthly Expenses</div>
        <div style="font-size: 28px; font-weight: bold; color: #F44336;">₹{total_monthly_expenses:,.0f}</div>
        <div style="font-size: 12px; color: #666; margin-top: 5px;">{len(recurring_expense_list)} scheduled</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    net_color = "#4CAF50" if net_monthly >= 0 else "#F44336"
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #E3F2FD 0%, white 100%); padding: 20px; border-radius: 10px; border-left: 4px solid {net_color};">
        <div style="font-size: 14px; color: #666;">Net Monthly</div>
        <div style="font-size: 28px; font-weight: bold; color: {net_color};">₹{net_monthly:,.0f}</div>
        <div style="font-size: 12px; color: #666; margin-top: 5px;">{'Surplus' if net_monthly >= 0 else 'Deficit'}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #FFF3E0 0%, white 100%); padding: 20px; border-radius: 10px; border-left: 4px solid #FF9800;">
        <div style="font-size: 14px; color: #666;">Processed</div>
        <div style="font-size: 28px; font-weight: bold; color: #FF9800;">{processed_income_count + processed_expense_count}</div>
        <div style="font-size: 12px; color: #666; margin-top: 5px;">Total auto-added</div>
    </div>
    """, unsafe_allow_html=True)

# Status message
if net_monthly > 0:
    st.success(f"✅ Excellent! You save ₹{net_monthly:,.0f} monthly from recurring income after expenses.")
elif net_monthly < 0:
    st.error(f"⚠️ Warning: Recurring expenses exceed income by ₹{abs(net_monthly):,.0f}/month!")
else:
    st.info("💡 Your recurring income and expenses are balanced.")

# ===== SECTION 2: ADD NEW RECURRING TRANSACTION =====
st.markdown("---")
st.subheader("➕ Set Up Recurring Transaction")

# Two tabs for income/expense
income_tab, expense_tab = st.tabs(["💰 Recurring Income", "💸 Recurring Expense"])

# INCOME TAB
with income_tab:
    with st.form("add_recurring_income_form", clear_on_submit=True):
        st.markdown("##### Automate Regular Income")
        
        col1, col2 = st.columns(2)
        
        with col1:
            income_category = st.selectbox(
                "Income Category*",
                INCOME_CATEGORIES,
                help="What type of income is this?"
            )
        
        with col2:
            income_amount = st.number_input(
                "Amount (₹)*",
                min_value=0.0,
                value=50000.0,
                step=500.0,
                help="How much do you receive?",
                key="income_amount"
            )
        
        col3, col4 = st.columns(2)
        
        with col3:
            income_frequency = st.selectbox(
                "Frequency*",
                ["Daily", "Weekly", "Monthly", "3 Months", "6 Months", "Yearly"],
                index=2,
                help="How often do you receive this?",
                key="income_frequency"
            )
        
        with col4:
            income_start_date = st.date_input(
                "Start Date*",
                value=datetime.now().date(),
                help="When does this start?",
                key="income_start_date"
            )
        
        income_description = st.text_area(
            "Description (Optional)",
            placeholder="e.g., Monthly salary from XYZ Company",
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
                    periods = calculate_all_periods(income_amount, income_frequency)
                    
                    st.success(f"✅ Recurring income added: **{income_category}** - ₹{income_amount:,.0f} ({income_frequency})")
                    st.info(f"🔔 This will automatically appear in Income page starting {income_start_date}")
                    
                    # Show impact
                    st.markdown("##### 💰 Financial Impact")
                    impact_col1, impact_col2, impact_col3, impact_col4 = st.columns(4)
                    
                    with impact_col1:
                        st.metric("Daily", f"₹{periods['daily']:,.0f}")
                    with impact_col2:
                        st.metric("Weekly", f"₹{periods['weekly']:,.0f}")
                    with impact_col3:
                        st.metric("Monthly", f"₹{periods['monthly']:,.0f}")
                    with impact_col4:
                        st.metric("Yearly", f"₹{periods['yearly']:,.0f}")
                    
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Error adding recurring income")

# EXPENSE TAB
with expense_tab:
    with st.form("add_recurring_expense_form", clear_on_submit=True):
        st.markdown("##### Automate Regular Expenses")
        
        col1, col2 = st.columns(2)
        
        with col1:
            expense_category = st.selectbox(
                "Expense Category*",
                EXPENSE_CATEGORIES,
                help="What type of expense is this?"
            )
        
        with col2:
            expense_amount = st.number_input(
                "Amount (₹)*",
                min_value=0.0,
                value=5000.0,
                step=500.0,
                help="How much do you pay?",
                key="expense_amount"
            )
        
        col3, col4 = st.columns(2)
        
        with col3:
            expense_frequency = st.selectbox(
                "Frequency*",
                ["Daily", "Weekly", "Monthly", "3 Months", "6 Months", "Yearly"],
                index=2,
                help="How often do you pay this?",
                key="expense_frequency"
            )
        
        with col4:
            expense_start_date = st.date_input(
                "Start Date*",
                value=datetime.now().date(),
                help="When does this start?",
                key="expense_start_date"
            )
        
        expense_description = st.text_area(
            "Description (Optional)",
            placeholder="e.g., Monthly rent for apartment",
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
                    periods = calculate_all_periods(expense_amount, expense_frequency)
                    
                    st.success(f"✅ Recurring expense added: **{expense_category}** - ₹{expense_amount:,.0f} ({expense_frequency})")
                    st.info(f"🔔 This will automatically appear in Expense page starting {expense_start_date}")
                    
                    # Show impact
                    st.markdown("##### 💸 Financial Impact")
                    impact_col1, impact_col2, impact_col3, impact_col4 = st.columns(4)
                    
                    with impact_col1:
                        st.metric("Daily", f"₹{periods['daily']:,.0f}")
                    with impact_col2:
                        st.metric("Weekly", f"₹{periods['weekly']:,.0f}")
                    with impact_col3:
                        st.metric("Monthly", f"₹{periods['monthly']:,.0f}")
                    with impact_col4:
                        st.metric("Yearly", f"₹{periods['yearly']:,.0f}")
                    
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Error adding recurring expense")

# ===== SECTION 3: SCHEDULED TRANSACTIONS =====
st.markdown("---")
st.subheader("📅 Scheduled Recurring Transactions")

if recurring_income_list or recurring_expense_list:
    tab1, tab2 = st.tabs([f"💰 Income ({len(recurring_income_list)})", f"💸 Expenses ({len(recurring_expense_list)})"])
    
    with tab1:
        if recurring_income_list:
            st.markdown("##### Your Scheduled Recurring Income")
            for trans in recurring_income_list:
                display_transaction_card(trans, 'Income')
                if st.button(f"🗑️ Delete", key=f"del_inc_{trans['id']}", type="secondary"):
                    if delete_recurring_transaction(trans['id']):
                        st.success(f"✅ Deleted: {trans['category']}")
                        st.rerun()
        else:
            st.info("💡 No recurring income scheduled yet.")
    
    with tab2:
        if recurring_expense_list:
            st.markdown("##### Your Scheduled Recurring Expenses")
            for trans in recurring_expense_list:
                display_transaction_card(trans, 'Expense')
                if st.button(f"🗑️ Delete", key=f"del_exp_{trans['id']}", type="secondary"):
                    if delete_recurring_transaction(trans['id']):
                        st.success(f"✅ Deleted: {trans['category']}")
                        st.rerun()
        else:
            st.info("💡 No recurring expenses scheduled yet.")
else:
    st.info("💡 No recurring transactions set up yet. Add your first one above!")

# Footer
st.markdown("---")
st.caption("🔄 Recurring Transactions | BudgetBuddy Pro")
st.caption("💡 Powered by intelligent automation")
