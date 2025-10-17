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

# Import database functions - FIXED FUNCTION NAMES
from database import (
    get_all_recurring_transactions,
    add_recurring_transaction,
    delete_recurring_transaction,
    process_recurring_transactions  # ← FIXED: Removed "due_" prefix
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
# Auto-process any transactions that are due - FIXED FUNCTION CALL
due_count = process_recurring_transactions(user_id)  # ← FIXED
if due_count > 0:
    st.success(f"✅ Processed {due_count} recurring transaction(s) automatically!")

# ... REST OF THE CODE REMAINS EXACTLY THE SAME ...
# (I'll include the full code below for completeness)

# ===== SECTION 1: ADD NEW RECURRING TRANSACTION (NOW AT TOP!) =====
st.markdown("---")
st.subheader("➕ Add New Recurring Transaction")

with st.form("add_recurring_form", clear_on_submit=True):
    st.markdown("##### Transaction Details")
    
    # Type selection
    transaction_type = st.radio(
        "Type*", 
        ["Income", "Expense"], 
        horizontal=True,
        help="Choose whether this is recurring income or expense"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Dynamic category selection based on type
        if transaction_type == "Income":
            category = st.selectbox(
                "Category*", 
                INCOME_CATEGORIES,
                help="Select the type of recurring income"
            )
        else:
            category = st.selectbox(
                "Category*", 
                EXPENSE_CATEGORIES,
                help="Select the type of recurring expense"
            )
    
    with col2:
        amount = st.number_input(
            "Amount (₹)*", 
            min_value=0.0, 
            value=5000.0, 
            step=100.0,
            help="Amount for each occurrence"
        )
    
    col3, col4 = st.columns(2)
    
    with col3:
        frequency = st.selectbox(
            "Frequency*",
            ["Daily", "Weekly", "Monthly", "Yearly"],
            index=2,
            help="How often this transaction occurs"
        )
    
    with col4:
        start_date = st.date_input(
            "Start Date*",
            value=datetime.now().date(),
            help="When should this recurring transaction start?"
        )
    
    description = st.text_area(
        "Description (Optional)",
        placeholder="e.g., Monthly salary from ABC Company",
        help="Add any additional notes about this recurring transaction"
    )
    
    # Show monthly equivalent
    if amount > 0:
        monthly_equiv = calculate_monthly_equivalent(amount, frequency)
        st.info(f"💰 **Monthly Impact:** ₹{monthly_equiv:,.0f} ({frequency.lower()})")
    
    submit_recurring = st.form_submit_button("💾 Add Recurring Transaction", use_container_width=True, type="primary")
    
    if submit_recurring:
        if amount <= 0:
            st.error("❌ Amount must be greater than 0")
        else:
            # Add to database
            success = add_recurring_transaction(
                user_id=user_id,
                trans_type=transaction_type,
                category=category,
                amount=amount,
                frequency=frequency,
                start_date=start_date,
                description=description
            )
            
            if success:
                monthly_impact = calculate_monthly_equivalent(amount, frequency)
                st.success(f"✅ Recurring {transaction_type.lower()} added: **{category}** - ₹{amount:,.0f} ({frequency})")
                st.info(f"💰 Monthly impact: ₹{monthly_impact:,.0f}")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Error adding recurring transaction")

# ===== SECTION 2: RECURRING TRANSACTIONS OVERVIEW (NOW BELOW FORM!) =====
st.markdown("---")
st.subheader("📊 Your Recurring Transactions")

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
            st.markdown("### Recurring Income")
            
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
            st.markdown("### Recurring Expenses")
            
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

# ===== TIPS SECTION =====
st.markdown("---")
with st.expander("💡 How Recurring Transactions Work", expanded=False):
    st.markdown("""
    ### Automatic Processing
    
    **How it works:**
    1. Set up your recurring income and expenses once
    2. System automatically adds them on the due date
    3. You get notified when transactions are processed
    4. All budgets and reports update automatically
    
    **Frequency Options:**
    - **Daily**: Every day (e.g., daily allowance)
    - **Weekly**: Every 7 days (e.g., weekly grocery shopping)
    - **Monthly**: Once per month (e.g., salary, rent)
    - **Yearly**: Once per year (e.g., insurance renewal)
    
    **Tips:**
    - Set up all regular transactions for better budgeting
    - Check upcoming transactions in the overview
    - Update amounts if they change
    - Delete completed or cancelled transactions
    """)

# Footer
st.markdown("---")
st.caption("🔄 Recurring Transactions | BudgetBuddy")
st.caption("💡 Set it once, track it automatically!")
