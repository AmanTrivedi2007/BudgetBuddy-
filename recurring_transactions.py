# recurring_transactions.py - PRODUCTION READY - Connected to Income & Expense Tables

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

# Import shared categories
from categories import EXPENSE_CATEGORIES, INCOME_CATEGORIES

# Import database functions - SAME AS income_monitoring.py and expense.py
from database import (
    add_income_to_db,
    add_expense_to_db,
    get_all_income,
    get_all_expenses,
    delete_income_from_db,
    delete_expense_from_db
)

# Set seaborn style
sns.set_style("whitegrid")

# Check user login
if 'username' not in st.session_state or not st.session_state.username:
    st.error("⚠️ Please login first!")
    st.stop()

user_id = st.session_state.username

# Page header
st.title("🔄 Recurring Transactions Dashboard")
st.markdown("*Manage all your recurring income and expenses - Connected directly to your Income & Expense data*")

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
    """Calculate all time period equivalents"""
    monthly = calculate_monthly_equivalent(amount, frequency)
    return {
        'daily': monthly / 30,
        'weekly': monthly / 4.33,
        'monthly': monthly,
        'yearly': monthly * 12
    }

# ===== GET ALL DATA FROM INCOME & EXPENSE TABLES =====
all_income = get_all_income(user_id)
all_expenses = get_all_expenses(user_id)

# Calculate totals
total_income = sum([i['amount'] for i in all_income])
total_expenses = sum([e['amount'] for e in all_expenses])
net_balance = total_income - total_expenses

# ===== SECTION 1: DASHBOARD OVERVIEW =====
st.markdown("---")
st.subheader("📊 Financial Overview")
st.caption("💡 This data is synced with your Income and Expense pages")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #E8F5E9 0%, white 100%); padding: 20px; border-radius: 10px; border-left: 4px solid #4CAF50; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="font-size: 14px; color: #666; font-weight: 500;">Total Income</div>
        <div style="font-size: 32px; font-weight: bold; color: #4CAF50; margin: 10px 0;">₹{total_income:,.0f}</div>
        <div style="font-size: 12px; color: #666;">{len(all_income)} transactions</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #FFEBEE 0%, white 100%); padding: 20px; border-radius: 10px; border-left: 4px solid #F44336; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="font-size: 14px; color: #666; font-weight: 500;">Total Expenses</div>
        <div style="font-size: 32px; font-weight: bold; color: #F44336; margin: 10px 0;">₹{total_expenses:,.0f}</div>
        <div style="font-size: 12px; color: #666;">{len(all_expenses)} transactions</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    net_color = "#4CAF50" if net_balance >= 0 else "#F44336"
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #E3F2FD 0%, white 100%); padding: 20px; border-radius: 10px; border-left: 4px solid {net_color}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="font-size: 14px; color: #666; font-weight: 500;">Net Balance</div>
        <div style="font-size: 32px; font-weight: bold; color: {net_color}; margin: 10px 0;">₹{net_balance:,.0f}</div>
        <div style="font-size: 12px; color: #666;">{'Surplus' if net_balance >= 0 else 'Deficit'}</div>
    </div>
    """, unsafe_allow_html=True)

# Status message
if net_balance > 0:
    st.success(f"✅ Excellent! You have a surplus of ₹{net_balance:,.0f}!")
elif net_balance < 0:
    st.error(f"⚠️ Warning: You have a deficit of ₹{abs(net_balance):,.0f}!")
else:
    st.info("💡 Your income and expenses are balanced.")

# ===== SECTION 2: ADD RECURRING TRANSACTIONS =====
st.markdown("---")
st.subheader("➕ Add Recurring Transaction")
st.caption("💡 Transactions added here are saved directly to Income/Expense tables")

# Two tabs for income/expense
income_tab, expense_tab = st.tabs(["💰 Add Recurring Income", "💸 Add Recurring Expense"])

# INCOME TAB
with income_tab:
    st.markdown("##### Set Up Recurring Income")
    st.info("💡 This will be added to your **Income Monitoring** page")
    
    with st.form("add_recurring_income_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            income_source = st.selectbox(
                "Income Source*",
                ["Salary", "Freelance", "Business", "Investment", "Bonus", "Gift", "Other"],
                help="Select the type of recurring income"
            )
            
            income_amount = st.number_input(
                "Amount (₹)*",
                min_value=0.0,
                value=50000.0,
                step=500.0,
                help="Amount you receive",
                key="income_amount"
            )
        
        with col2:
            income_frequency = st.selectbox(
                "Frequency*",
                ["Daily", "Weekly", "Monthly", "3 Months", "6 Months", "Yearly"],
                index=2,
                help="How often you receive this income",
                key="income_frequency"
            )
            
            income_date = st.date_input(
                "Date*",
                value=datetime.now().date(),
                help="Transaction date",
                key="income_date"
            )
        
        income_notes = st.text_area(
            "Notes (Optional)",
            placeholder="e.g., Monthly salary from XYZ Company",
            help="Add any additional details",
            key="income_notes"
        )
        
        submit_income = st.form_submit_button("💾 Add Recurring Income", use_container_width=True, type="primary")
        
        if submit_income:
            if income_amount <= 0:
                st.error("❌ Amount must be greater than 0")
            else:
                # Add note about recurring frequency
                notes_with_frequency = f"[Recurring-{income_frequency}] {income_notes}"
                
                # Save DIRECTLY to income table (same as income_monitoring.py)
                add_income_to_db(user_id, income_source, income_amount, income_date, notes_with_frequency)
                
                periods = calculate_all_periods(income_amount, income_frequency)
                
                st.success(f"✅ Recurring income added: **{income_source}** - ₹{income_amount:,.0f} ({income_frequency})")
                st.info("🔔 This transaction is now visible in your **Income Monitoring** page!")
                
                # Show financial impact
                st.markdown("##### 💰 Financial Impact")
                impact_col1, impact_col2, impact_col3, impact_col4 = st.columns(4)
                
                with impact_col1:
                    st.metric("📅 Daily", f"₹{periods['daily']:,.0f}")
                with impact_col2:
                    st.metric("🗓️ Weekly", f"₹{periods['weekly']:,.0f}")
                with impact_col3:
                    st.metric("📆 Monthly", f"₹{periods['monthly']:,.0f}")
                with impact_col4:
                    st.metric("📅 Yearly", f"₹{periods['yearly']:,.0f}")
                
                st.balloons()
                st.rerun()

# EXPENSE TAB
with expense_tab:
    st.markdown("##### Set Up Recurring Expense")
    st.info("💡 This will be added to your **Expense Tracking** page")
    
    with st.form("add_recurring_expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            expense_category = st.selectbox(
                "Expense Category*",
                EXPENSE_CATEGORIES,
                help="Select the type of recurring expense"
            )
            
            expense_amount = st.number_input(
                "Amount (₹)*",
                min_value=0.0,
                value=5000.0,
                step=500.0,
                help="Amount you pay",
                key="expense_amount"
            )
        
        with col2:
            expense_frequency = st.selectbox(
                "Frequency*",
                ["Daily", "Weekly", "Monthly", "3 Months", "6 Months", "Yearly"],
                index=2,
                help="How often you pay this expense",
                key="expense_frequency"
            )
            
            expense_date = st.date_input(
                "Date*",
                value=datetime.now().date(),
                help="Transaction date",
                key="expense_date"
            )
        
        expense_description = st.text_area(
            "Description (Optional)",
            placeholder="e.g., Monthly rent payment",
            help="Add any additional details",
            key="expense_description"
        )
        
        submit_expense = st.form_submit_button("💾 Add Recurring Expense", use_container_width=True, type="primary")
        
        if submit_expense:
            if expense_amount <= 0:
                st.error("❌ Amount must be greater than 0")
            else:
                # Add note about recurring frequency
                description_with_frequency = f"[Recurring-{expense_frequency}] {expense_description}"
                
                # Save DIRECTLY to expenses table (same as expense.py)
                add_expense_to_db(user_id, expense_category, expense_amount, expense_date, description_with_frequency)
                
                periods = calculate_all_periods(expense_amount, expense_frequency)
                
                st.success(f"✅ Recurring expense added: **{expense_category}** - ₹{expense_amount:,.0f} ({expense_frequency})")
                st.info("🔔 This transaction is now visible in your **Expense Tracking** page!")
                
                # Show financial impact
                st.markdown("##### 💸 Financial Impact")
                impact_col1, impact_col2, impact_col3, impact_col4 = st.columns(4)
                
                with impact_col1:
                    st.metric("📅 Daily", f"₹{periods['daily']:,.0f}")
                with impact_col2:
                    st.metric("🗓️ Weekly", f"₹{periods['weekly']:,.0f}")
                with impact_col3:
                    st.metric("📆 Monthly", f"₹{periods['monthly']:,.0f}")
                with impact_col4:
                    st.metric("📅 Yearly", f"₹{periods['yearly']:,.0f}")
                
                st.balloons()
                st.rerun()

# ===== SECTION 3: VIEW ALL TRANSACTIONS =====
st.markdown("---")
st.subheader("📋 All Transactions")
st.caption("💡 Showing data from Income and Expense tables")

# Filter recurring transactions
recurring_income = [i for i in all_income if '[Recurring' in str(i.get('notes', ''))]
recurring_expenses = [e for e in all_expenses if '[Recurring' in str(e.get('description', ''))]

tab1, tab2, tab3 = st.tabs([
    f"💰 Income ({len(all_income)})", 
    f"💸 Expenses ({len(all_expenses)})",
    f"🔄 Recurring Only ({len(recurring_income)} income, {len(recurring_expenses)} expenses)"
])

with tab1:
    st.markdown("##### All Income Transactions")
    if all_income:
        df_income = pd.DataFrame(all_income)
        df_income = df_income[['date', 'source', 'amount', 'notes']].sort_values('date', ascending=False)
        df_income.columns = ['Date', 'Source', 'Amount (₹)', 'Notes']
        df_income['Amount (₹)'] = df_income['Amount (₹)'].apply(lambda x: f"₹{x:,.0f}")
        st.dataframe(df_income, use_container_width=True, hide_index=True)
    else:
        st.info("💡 No income transactions yet. Add some using the form above or in the Income Monitoring page!")

with tab2:
    st.markdown("##### All Expense Transactions")
    if all_expenses:
        df_expenses = pd.DataFrame(all_expenses)
        df_expenses = df_expenses[['date', 'category', 'amount', 'description']].sort_values('date', ascending=False)
        df_expenses.columns = ['Date', 'Category', 'Amount (₹)', 'Description']
        df_expenses['Amount (₹)'] = df_expenses['Amount (₹)'].apply(lambda x: f"₹{x:,.0f}")
        st.dataframe(df_expenses, use_container_width=True, hide_index=True)
    else:
        st.info("💡 No expense transactions yet. Add some using the form above or in the Expense Tracking page!")

with tab3:
    st.markdown("##### Recurring Transactions Only")
    
    if recurring_income or recurring_expenses:
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("**💰 Recurring Income**")
            if recurring_income:
                for inc in recurring_income:
                    st.success(f"✅ {inc['source']} - ₹{inc['amount']:,.0f} ({inc['date']})")
            else:
                st.info("No recurring income yet")
        
        with col_b:
            st.markdown("**💸 Recurring Expenses**")
            if recurring_expenses:
                for exp in recurring_expenses:
                    st.error(f"✅ {exp['category']} - ₹{exp['amount']:,.0f} ({exp['date']})")
            else:
                st.info("No recurring expenses yet")
    else:
        st.info("💡 No recurring transactions yet. Add your first recurring income or expense above!")
        
        # Show examples
        st.markdown("### 💡 Common Recurring Transactions")
        
        col_examples1, col_examples2 = st.columns(2)
        
        with col_examples1:
            st.markdown("**Recurring Income:**")
            st.write("- 💼 Monthly Salary")
            st.write("- 💻 Regular Freelance Contracts")
            st.write("- 🏠 Rental Income")
            st.write("- 💹 Investment Dividends")
        
        with col_examples2:
            st.markdown("**Recurring Expenses:**")
            st.write("- 🏠 Rent/Mortgage")
            st.write("- 📱 Phone & Internet Bills")
            st.write("- 📺 Streaming Subscriptions")
            st.write("- 💰 Loan EMIs")
            st.write("- 🏋️ Gym Membership")

# Footer
st.markdown("---")
st.markdown("### ✅ How This Works")
st.info("""
**Perfect Integration:**
- 💰 Income added here → Shows in **Income Monitoring** page
- 💸 Expenses added here → Shows in **Expense Tracking** page
- 🔄 All data is synchronized across pages
- 📊 No separate database - everything uses the same Income & Expense tables
- ✨ Add transactions anywhere - they appear everywhere!
""")

st.caption("🔄 Recurring Transactions Dashboard | BudgetBuddy Pro")
st.caption("💡 Seamlessly connected with Income & Expense tracking")
