# recurring_transactions.py - TRUE RECURRING AUTOMATION SYSTEM

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

# Import shared categories
from categories import EXPENSE_CATEGORIES, INCOME_CATEGORIES

# Import database functions
from database import (
    add_recurring_transaction,
    get_all_recurring_transactions,
    delete_recurring_transaction,
    process_recurring_transactions,
    add_income_to_db,
    add_expense_to_db,
    get_all_income,
    get_all_expenses,
    get_all_goals  # ← ONLY CHANGE 1: Added this line
)

# Set seaborn style
sns.set_style("whitegrid")

# Check user login
if 'username' not in st.session_state or not st.session_state.username:
    st.error("⚠️ Please login first!")
    st.stop()

user_id = st.session_state.username

# ===== AUTO-PROCESS RECURRING TRANSACTIONS ON PAGE LOAD =====
try:
    processed_count = process_recurring_transactions(user_id)
    if processed_count > 0:
        st.success(f"✅ Automatically processed {processed_count} due recurring transaction(s)!")
        st.balloons()
except Exception as e:
    st.error(f"⚠️ Error processing recurring transactions: {str(e)}")

# Page header
st.title("🔄 Recurring Transactions - Auto Payment System")
st.markdown("*Set up automatic recurring income and expenses that process automatically!*")

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

# ===== GET DATA =====
all_income = get_all_income(user_id)
all_expenses = get_all_expenses(user_id)
all_goals = get_all_goals(user_id)  # ← ONLY CHANGE 2: Added this line
recurring_transactions = get_all_recurring_transactions(user_id)

# Separate recurring transactions
recurring_income_list = [t for t in recurring_transactions if t['type'] == 'Income']
recurring_expense_list = [t for t in recurring_transactions if t['type'] == 'Expense']

# Calculate totals
total_income = sum([i['amount'] for i in all_income])
total_expenses = sum([e['amount'] for e in all_expenses])
total_saved_in_goals = sum([goal['saved_amount'] for goal in all_goals])  # ← ONLY CHANGE 3a: Added this line
net_balance = total_income - total_expenses - total_saved_in_goals  # ← ONLY CHANGE 3b: Modified this line

# Calculate recurring monthly
recurring_monthly_income = sum([calculate_monthly_equivalent(t['amount'], t['frequency']) for t in recurring_income_list])
recurring_monthly_expenses = sum([calculate_monthly_equivalent(t['amount'], t['frequency']) for t in recurring_expense_list])

# ===== DASHBOARD OVERVIEW =====
st.markdown("---")
st.subheader("📊 Financial Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #E8F5E9 0%, white 100%); padding: 20px; border-radius: 10px; border-left: 4px solid #4CAF50; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="font-size: 14px; color: #666; font-weight: 500;">Total Income</div>
        <div style="font-size: 28px; font-weight: bold; color: #4CAF50; margin: 10px 0;">₹{total_income:,.0f}</div>
        <div style="font-size: 12px; color: #666;">{len(all_income)} transactions</div>
        <div style="font-size: 11px; color: #4CAF50; margin-top: 8px;">🔄 ₹{recurring_monthly_income:,.0f}/mo recurring</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #FFEBEE 0%, white 100%); padding: 20px; border-radius: 10px; border-left: 4px solid #F44336; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="font-size: 14px; color: #666; font-weight: 500;">Total Expenses</div>
        <div style="font-size: 28px; font-weight: bold; color: #F44336; margin: 10px 0;">₹{total_expenses:,.0f}</div>
        <div style="font-size: 12px; color: #666;">{len(all_expenses)} transactions</div>
        <div style="font-size: 11px; color: #F44336; margin-top: 8px;">🔄 ₹{recurring_monthly_expenses:,.0f}/mo recurring</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    net_balance_color = "#4CAF50" if net_balance >= 0 else "#F44336"
    net_monthly = recurring_monthly_income - recurring_monthly_expenses
    net_monthly_color = "#4CAF50" if net_monthly >= 0 else "#F44336"
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #E3F2FD 0%, white 100%); padding: 20px; border-radius: 10px; border-left: 4px solid {net_balance_color}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="font-size: 14px; color: #666; font-weight: 500;">Available Balance</div>
        <div style="font-size: 28px; font-weight: bold; color: {net_balance_color}; margin: 10px 0;">₹{net_balance:,.0f}</div>
        <div style="font-size: 12px; color: #666;">After savings</div>
        <div style="font-size: 11px; color: {net_monthly_color}; margin-top: 8px;">🔄 ₹{net_monthly:,.0f}/mo recurring</div>
    </div>
    """, unsafe_allow_html=True)

# ... REST OF YOUR CODE STAYS EXACTLY THE SAME ...


if net_balance > 0:
    st.success(f"✅ Great! You have a surplus of ₹{net_balance:,.0f}!")
elif net_balance < 0:
    st.error(f"⚠️ Warning: Deficit of ₹{abs(net_balance):,.0f}!")
else:
    st.info("💡 Balanced budget.")

# ===== ADD RECURRING TRANSACTIONS =====
st.markdown("---")
st.subheader("➕ Set Up Auto-Recurring Transaction")
st.info("💡 **How it works:** Set up once, and transactions will be automatically created every interval!")

income_tab, expense_tab = st.tabs(["💰 Auto Recurring Income", "💸 Auto Recurring Expense"])

# INCOME TAB
with income_tab:
    st.markdown("##### Set Up Automatic Recurring Income")
    
    with st.form("add_auto_recurring_income", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            income_source = st.selectbox(
                "Income Source*",
                ["Salary", "Freelance", "Business", "Investment", "Bonus", "Gift", "Other"],
                key="rec_income_source"
            )
            
            income_amount = st.number_input(
                "Amount (₹)*",
                min_value=0.0,
                value=50000.0,
                step=500.0,
                key="rec_income_amount"
            )
        
        with col2:
            income_frequency = st.selectbox(
                "Frequency*",
                ["Daily", "Weekly", "Monthly", "3 Months", "6 Months", "Yearly"],
                index=2,
                help="Transactions will be auto-created at this interval",
                key="rec_income_frequency"
            )
            
            income_start_date = st.date_input(
                "Start Date*",
                value=datetime.now().date(),
                help="First transaction date",
                key="rec_income_start_date"
            )
        
        income_notes = st.text_area(
            "Notes (Optional)",
            placeholder="e.g., Monthly salary from XYZ Company",
            key="rec_income_notes"
        )
        
        submit_rec_income = st.form_submit_button("💾 Set Up Auto-Recurring Income", use_container_width=True, type="primary")
        
        if submit_rec_income:
            if income_amount <= 0:
                st.error("❌ Amount must be greater than 0")
            else:
                # Add to recurring_transactions table (NOT income table directly!)
                success = add_recurring_transaction(
                    user_id=user_id,
                    trans_type="Income",
                    category=income_source,
                    amount=income_amount,
                    frequency=income_frequency,
                    start_date=income_start_date,
                    description=income_notes
                )
                
                if success:
                    periods = calculate_all_periods(income_amount, income_frequency)
                    
                    st.success(f"✅ Auto-recurring income set up: **{income_source}** - ₹{income_amount:,.0f} ({income_frequency})")
                    st.info(f"🔔 **Automatic Processing:** This will be automatically added to your Income page every {income_frequency}!")
                    
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
                else:
                    st.error("❌ Error setting up recurring income")

# EXPENSE TAB
with expense_tab:
    st.markdown("##### Set Up Automatic Recurring Expense")
    
    with st.form("add_auto_recurring_expense", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            expense_category = st.selectbox(
                "Expense Category*",
                EXPENSE_CATEGORIES,
                key="rec_expense_category"
            )
            
            expense_amount = st.number_input(
                "Amount (₹)*",
                min_value=0.0,
                value=5000.0,
                step=500.0,
                key="rec_expense_amount"
            )
        
        with col2:
            expense_frequency = st.selectbox(
                "Frequency*",
                ["Daily", "Weekly", "Monthly", "3 Months", "6 Months", "Yearly"],
                index=2,
                help="Transactions will be auto-created at this interval",
                key="rec_expense_frequency"
            )
            
            expense_start_date = st.date_input(
                "Start Date*",
                value=datetime.now().date(),
                help="First transaction date",
                key="rec_expense_start_date"
            )
        
        expense_description = st.text_area(
            "Description (Optional)",
            placeholder="e.g., Monthly rent payment",
            key="rec_expense_description"
        )
        
        submit_rec_expense = st.form_submit_button("💾 Set Up Auto-Recurring Expense", use_container_width=True, type="primary")
        
        if submit_rec_expense:
            if expense_amount <= 0:
                st.error("❌ Amount must be greater than 0")
            else:
                # Add to recurring_transactions table (NOT expenses table directly!)
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
                    
                    st.success(f"✅ Auto-recurring expense set up: **{expense_category}** - ₹{expense_amount:,.0f} ({expense_frequency})")
                    st.info(f"🔔 **Automatic Processing:** This will be automatically added to your Expense page every {expense_frequency}!")
                    
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
                else:
                    st.error("❌ Error setting up recurring expense")

# ===== SCHEDULED RECURRING TRANSACTIONS =====
st.markdown("---")
st.subheader("📅 Scheduled Auto-Recurring Transactions")
st.caption("💡 These are set up for automatic processing - they will auto-create transactions when due!")

if recurring_income_list or recurring_expense_list:
    tab1, tab2 = st.tabs([f"💰 Auto Income ({len(recurring_income_list)})", f"💸 Auto Expenses ({len(recurring_expense_list)})"])
    
    with tab1:
        if recurring_income_list:
            st.markdown("##### Scheduled Auto-Recurring Income")
            for rec in recurring_income_list:
                next_date = datetime.strptime(rec['next_date'], '%Y-%m-%d').date()
                days_until = (next_date - datetime.now().date()).days
                
                col_a, col_b, col_c = st.columns([3, 2, 1])
                
                with col_a:
                    st.success(f"💰 **{rec['category']}** - ₹{rec['amount']:,.0f}")
                    st.caption(f"📝 {rec.get('description', 'No description')}")
                
                with col_b:
                    st.info(f"🔁 Every {rec['frequency']}")
                    if days_until <= 0:
                        st.error(f"⚠️ Due today! (will auto-process)")
                    elif days_until <= 3:
                        st.warning(f"⏰ Due in {days_until} days")
                    else:
                        st.caption(f"📅 Next: {rec['next_date']}")
                
                with col_c:
                    if st.button("🗑️ Delete", key=f"del_rec_inc_{rec['id']}", type="secondary"):
                        if delete_recurring_transaction(rec['id']):
                            st.success("✅ Deleted")
                            st.rerun()
                
                st.markdown("---")
        else:
            st.info("💡 No auto-recurring income set up yet.")
    
    with tab2:
        if recurring_expense_list:
            st.markdown("##### Scheduled Auto-Recurring Expenses")
            for rec in recurring_expense_list:
                next_date = datetime.strptime(rec['next_date'], '%Y-%m-%d').date()
                days_until = (next_date - datetime.now().date()).days
                
                col_a, col_b, col_c = st.columns([3, 2, 1])
                
                with col_a:
                    st.error(f"💸 **{rec['category']}** - ₹{rec['amount']:,.0f}")
                    st.caption(f"📝 {rec.get('description', 'No description')}")
                
                with col_b:
                    st.info(f"🔁 Every {rec['frequency']}")
                    if days_until <= 0:
                        st.error(f"⚠️ Due today! (will auto-process)")
                    elif days_until <= 3:
                        st.warning(f"⏰ Due in {days_until} days")
                    else:
                        st.caption(f"📅 Next: {rec['next_date']}")
                
                with col_c:
                    if st.button("🗑️ Delete", key=f"del_rec_exp_{rec['id']}", type="secondary"):
                        if delete_recurring_transaction(rec['id']):
                            st.success("✅ Deleted")
                            st.rerun()
                
                st.markdown("---")
        else:
            st.info("💡 No auto-recurring expenses set up yet.")
else:
    st.info("💡 No auto-recurring transactions set up yet. Add your first one above!")

# Footer
st.markdown("---")
st.markdown("### ✅ How Auto-Recurring Works")
st.success("""
**Perfect Automation:**
1. 🔄 **Set up once** - Add your recurring income/expense with frequency
2. ⏰ **Auto-processing** - System checks daily and creates transactions automatically
3. 💰 **Shows in Income/Expense pages** - Auto-created transactions appear automatically
4. 📅 **Updates next date** - System automatically calculates next occurrence
5. ♾️ **Repeats forever** - Until you delete the recurring schedule

**No manual work needed - just set it and forget it!**
""")

st.caption("🔄 Recurring Transactions - Auto Payment System | BudgetBuddy Pro")
st.caption("💡 Powered by intelligent automation engine")

