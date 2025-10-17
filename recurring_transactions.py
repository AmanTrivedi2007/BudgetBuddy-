# recurring_transactions.py - Auto-add Salary, Rent, Subscriptions
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

# Set seaborn style
sns.set_style("whitegrid")


# ===== HELPER FUNCTIONS (MUST BE AT TOP!) =====

def calculate_monthly_equivalent(amount, frequency):
    """Convert any frequency to monthly amount"""
    if frequency == 'daily':
        return amount * 30
    elif frequency == 'weekly':
        return amount * 4.33
    elif frequency == 'monthly':
        return amount
    elif frequency == 'yearly':
        return amount / 12
    return amount


def display_transaction_card(transaction, trans_type):
    """Display a transaction card with details"""
    next_date = datetime.strptime(transaction['next_date'], '%Y-%m-%d').date()
    days_until = (next_date - datetime.now().date()).days
    
    if trans_type == 'income':
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
                    border-left: 5px solid {border}; margin-bottom: 10px;">
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
        
        with col1:
            st.markdown(f"### {icon} {transaction['category']}")
            if transaction['description']:
                st.caption(transaction['description'])
        
        with col2:
            st.markdown(f"**₹{transaction['amount']:,.0f}**")
        
        with col3:
            st.markdown(f"*{transaction['frequency'].capitalize()}*")
        
        with col4:
            if days_until <= 0:
                st.success(f"📅 Processing today!")
            elif days_until <= 3:
                st.warning(f"📅 In {days_until} days")
            else:
                st.info(f"📅 Next: {transaction['next_date']}")
        
        st.markdown("</div>", unsafe_allow_html=True)


def display_recurring_table(recurring_list):
    """Display recurring transactions in a table"""
    df_data = []
    for r in recurring_list:
        df_data.append({
            'Type': '💵 Income' if r['type'] == 'income' else '💳 Expense',
            'Category': r['category'],
            'Amount': f"₹{r['amount']:,.0f}",
            'Frequency': r['frequency'].capitalize(),
            'Next Date': r['next_date'],
            'Description': r['description'] if r['description'] else '-'
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True, hide_index=True)


# ===== MAIN PAGE CODE =====

# Title
st.title("🔁 Recurring Transactions")
st.markdown("*Auto-add salary, rent, subscriptions, and bills*")

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
    get_recurring_transaction_by_id
)

# Process any pending recurring transactions when page loads
process_recurring_transactions(user_id)

# === SECTION 1: OVERVIEW ===
st.markdown("---")
st.subheader("📊 Recurring Transactions Overview")

recurring_list = get_all_recurring_transactions(user_id)

if recurring_list:
    # Separate by type
    income_recurring = [r for r in recurring_list if r['type'] == 'income']
    expense_recurring = [r for r in recurring_list if r['type'] == 'expense']
    
    total_monthly_income = sum([calculate_monthly_equivalent(r['amount'], r['frequency']) for r in income_recurring])
    total_monthly_expense = sum([calculate_monthly_equivalent(r['amount'], r['frequency']) for r in expense_recurring])
    net_monthly = total_monthly_income - total_monthly_expense
    
    # Display summary cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💵 Monthly Income",
            value=f"₹{total_monthly_income:,.0f}",
            delta=f"+₹{total_monthly_income:,.0f}",
            help="Estimated monthly recurring income"
        )
    
    with col2:
        st.metric(
            label="💳 Monthly Expenses",
            value=f"₹{total_monthly_expense:,.0f}",
            delta=f"-₹{total_monthly_expense:,.0f}",
            delta_color="inverse",
            help="Estimated monthly recurring expenses"
        )
    
    with col3:
        st.metric(
            label="💰 Net Monthly",
            value=f"₹{net_monthly:,.0f}",
            delta=f"₹{net_monthly:,.0f}" if net_monthly >= 0 else f"-₹{abs(net_monthly):,.0f}",
            delta_color="normal" if net_monthly >= 0 else "inverse",
            help="Income - Expenses (monthly)"
        )
    
    with col4:
        total_transactions = len(recurring_list)
        st.metric(
            label="🔁 Active",
            value=total_transactions,
            help="Total active recurring transactions"
        )
    
    # === SECTION 2: UPCOMING TRANSACTIONS ===
    st.markdown("---")
    st.subheader("📅 Upcoming Transactions")
    
    # Sort by next_date
    upcoming = sorted(recurring_list, key=lambda x: x['next_date'])
    
    # Show next 7 days
    today = datetime.now().date()
    next_week = today + timedelta(days=7)
    
    upcoming_this_week = [
        r for r in upcoming 
        if today <= datetime.strptime(r['next_date'], '%Y-%m-%d').date() <= next_week
    ]
    
    if upcoming_this_week:
        st.info(f"📌 **{len(upcoming_this_week)} transactions** coming up in the next 7 days")
        
        for transaction in upcoming_this_week:
            next_date = datetime.strptime(transaction['next_date'], '%Y-%m-%d').date()
            days_until = (next_date - today).days
            
            # Determine styling
            if transaction['type'] == 'income':
                icon = "💵"
                color = "#E6F9E6"
                border_color = "#00AA00"
            else:
                icon = "💳"
                color = "#FFE6E6"
                border_color = "#FF4444"
            
            with st.container():
                st.markdown(f"""
                <div style="background-color: {color}; padding: 15px; border-radius: 10px; 
                            border-left: 5px solid {border_color}; margin-bottom: 10px;">
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 1, 2])
                
                with col1:
                    st.markdown(f"### {icon}")
                
                with col2:
                    st.markdown(f"**{transaction['category']}**")
                    if transaction['description']:
                        st.caption(transaction['description'])
                
                with col3:
                    st.markdown(f"**₹{transaction['amount']:,.0f}**")
                
                with col4:
                    st.markdown(f"*{transaction['frequency'].capitalize()}*")
                
                with col5:
                    if days_until == 0:
                        st.success("📅 **TODAY**")
                    elif days_until == 1:
                        st.info("📅 **Tomorrow**")
                    elif days_until <= 3:
                        st.warning(f"📅 **In {days_until} days**")
                    else:
                        st.write(f"📅 {transaction['next_date']}")
                
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("✨ No transactions scheduled for the next 7 days")
    
    # === SECTION 3: ALL RECURRING TRANSACTIONS (TABS) ===
    st.markdown("---")
    st.subheader("📋 All Recurring Transactions")
    
    tab1, tab2, tab3 = st.tabs(["💵 Income", "💳 Expenses", "📊 All"])
    
    with tab1:
        if income_recurring:
            st.markdown(f"**{len(income_recurring)} Recurring Income Sources**")
            
            for transaction in income_recurring:
                display_transaction_card(transaction, "income")
        else:
            st.info("💡 No recurring income set up yet. Add your salary or regular income below!")
    
    with tab2:
        if expense_recurring:
            st.markdown(f"**{len(expense_recurring)} Recurring Expenses**")
            
            for transaction in expense_recurring:
                display_transaction_card(transaction, "expense")
        else:
            st.info("💡 No recurring expenses set up yet. Add rent, subscriptions, or bills below!")
    
    with tab3:
        st.markdown(f"**{len(recurring_list)} Total Recurring Transactions**")
        
        # Create detailed table
        display_recurring_table(recurring_list)
    
    # === SECTION 4: VISUALIZATIONS ===
    st.markdown("---")
    st.subheader("📈 Recurring Transactions Analytics")
    
    viz_col1, viz_col2 = st.columns(2)
    
    with viz_col1:
        # Pie chart: Income vs Expense
        st.markdown("##### Income vs Expense Distribution")
        fig1, ax1 = plt.subplots(figsize=(6, 6))
        
        sizes = [total_monthly_income, total_monthly_expense]
        labels = ['Income', 'Expenses']
        colors = ['#90EE90', '#FFB6C1']
        explode = (0.05, 0.05)
        
        ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                startangle=90, textprops={'fontweight': 'bold'})
        ax1.axis('equal')
        st.pyplot(fig1)
        plt.close()
    
    with viz_col2:
        # Bar chart: Category-wise breakdown
        st.markdown("##### Category-wise Monthly Amount")
        fig2, ax2 = plt.subplots(figsize=(6, 6))
        
        # Group by category
        category_data = {}
        for r in recurring_list:
            category = r['category']
            monthly_amount = calculate_monthly_equivalent(r['amount'], r['frequency'])
            if category in category_data:
                category_data[category] += monthly_amount
            else:
                category_data[category] = monthly_amount
        
        if category_data:
            categories = list(category_data.keys())
            amounts = list(category_data.values())
            
            colors_list = ['#90EE90' if any(r['category'] == cat and r['type'] == 'income' for r in recurring_list) 
                     else '#FFB6C1' for cat in categories]
            
            bars = ax2.barh(categories, amounts, color=colors_list, edgecolor='black', alpha=0.7)
            ax2.set_xlabel('Monthly Amount (₹)', fontweight='bold')
            ax2.set_title('Category-wise Recurring Amounts', fontweight='bold')
            ax2.grid(axis='x', alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig2)
            plt.close()

else:
    st.info("💡 **No recurring transactions set up yet!** Create your first one below.")
    
    st.markdown("""
    ### 🎯 Why Use Recurring Transactions?
    
    - ✅ **Never forget regular income** (salary, freelance payments)
    - ✅ **Auto-track monthly expenses** (rent, subscriptions, bills)
    - ✅ **Save time** - Add once, auto-repeats forever
    - ✅ **Better budgeting** - Know your fixed monthly costs
    - ✅ **Stay organized** - See all upcoming transactions at a glance
    
    **Examples:**
    - 💵 **Income:** Monthly salary, freelance projects, rental income
    - 💳 **Expenses:** Rent, Netflix, Spotify, insurance premiums, loan EMIs
    """)

# === SECTION 5: ADD NEW RECURRING TRANSACTION ===
st.markdown("---")
st.subheader("➕ Add Recurring Transaction")

with st.form("add_recurring_form", clear_on_submit=True):
    st.markdown("##### Transaction Details")
    
    transaction_type = st.radio(
        "Type*", 
        ["Income", "Expense"], 
        horizontal=True,
        help="Choose whether this is recurring income or expense"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if transaction_type == "Income":
            category = st.selectbox(
                "Category*", 
                ["Salary", "Freelance", "Business", "Investment Returns", "Rental Income", "Other"],
                help="Select the type of recurring income"
            )
        else:
            category = st.selectbox(
                "Category*", 
                ["Rent", "Subscription", "Bills & Utilities", "Loan/EMI", "Insurance", 
                 "Internet/Phone", "Gym Membership", "Other"],
                help="Select the type of recurring expense"
            )
    
    with col2:
        amount = st.number_input(
            "Amount (₹)*", 
            min_value=0.0, 
            value=1000.0, 
            step=100.0,
            help="Enter the transaction amount"
        )
    
    col3, col4 = st.columns(2)
    
    with col3:
        frequency = st.selectbox(
            "Frequency*", 
            ["Daily", "Weekly", "Monthly", "Yearly"],
            index=2,
            help="How often this transaction repeats"
        )
    
    with col4:
        start_date = st.date_input(
            "Start Date*", 
            value=datetime.now(),
            help="When should this recurring transaction start?"
        )
    
    description = st.text_area(
        "Description (optional)", 
        placeholder="e.g., Monthly salary from XYZ Company, Netflix Premium subscription",
        help="Add notes about this transaction"
    )
    
    # Show estimated monthly impact
    st.markdown("##### Estimated Monthly Impact")
    monthly_impact = amount
    if frequency == "Daily":
        monthly_impact = amount * 30
    elif frequency == "Weekly":
        monthly_impact = amount * 4.33
    elif frequency == "Yearly":
        monthly_impact = amount / 12
    
    if transaction_type == "Income":
        st.success(f"💵 This will add approximately **₹{monthly_impact:,.0f}/month** to your income")
    else:
        st.error(f"💳 This will add approximately **₹{monthly_impact:,.0f}/month** to your expenses")
    
    submit_recurring = st.form_submit_button("💾 Save Recurring Transaction", use_container_width=True, type="primary")
    
    if submit_recurring:
        if amount <= 0:
            st.error("❌ Amount must be greater than 0")
        else:
            trans_type = transaction_type.lower()
            if add_recurring_transaction(user_id, trans_type, category, amount, 
                                        frequency.lower(), str(start_date), description):
                st.success(f"✅ Recurring {transaction_type} added: **{category}** - ₹{amount:,.0f} ({frequency})")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Error adding recurring transaction")

# === SECTION 6: MANAGE RECURRING TRANSACTIONS ===
if recurring_list:
    st.markdown("---")
    st.subheader("🗂️ Manage Recurring Transactions")
    
    # Delete recurring transaction
    st.markdown("##### Delete Recurring Transaction")
    
    delete_col1, delete_col2 = st.columns([3, 1])
    
    with delete_col1:
        delete_options = [
            f"{r['type'].capitalize()} - {r['category']} - ₹{r['amount']:,.0f} ({r['frequency']})" 
            for r in recurring_list
        ]
        delete_index = st.selectbox(
            "Select transaction to delete", 
            range(len(delete_options)), 
            format_func=lambda x: delete_options[x],
            help="Choose which recurring transaction to remove"
        )
    
    with delete_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Delete", type="secondary", use_container_width=True):
            selected_transaction = recurring_list[delete_index]
            if delete_recurring_transaction(selected_transaction['id']):
                st.success("✅ Recurring transaction deleted!")
                st.rerun()
            else:
                st.error("❌ Error deleting transaction")

# === SECTION 7: INFORMATION ===
st.markdown("---")
with st.expander("💡 How Recurring Transactions Work", expanded=False):
    st.markdown("""
    ### Automatic Transaction Processing
    
    **Frequency Options:**
    - **Daily**: Transaction added every day
    - **Weekly**: Transaction added every 7 days
    - **Monthly**: Transaction added on the same date each month
    - **Yearly**: Transaction added once per year on the same date
    
    **How It Works:**
    1. You set up a recurring transaction (e.g., Monthly salary on 1st)
    2. System automatically adds it to your income/expenses when date arrives
    3. Next date is automatically calculated
    4. Process repeats forever until you delete it
    
    **Examples:**
    - 💵 **Salary (Monthly)**: ₹50,000 on 1st of every month
    - 💳 **Rent (Monthly)**: ₹15,000 on 5th of every month
    - 💳 **Netflix (Monthly)**: ₹649 on 15th of every month
    - 💳 **Insurance (Yearly)**: ₹25,000 on birthday
    
    **Benefits:**
    - ✅ Never forget to log regular transactions
    - ✅ Accurate budget tracking
    - ✅ Saves time (set once, works forever)
    - ✅ See upcoming expenses in advance
    - ✅ Better financial planning
    
    **Tips:**
    - Review recurring transactions monthly
    - Update amounts if they change (e.g., salary increase)
    - Delete old subscriptions you cancelled
    - Use descriptions to remember details
    """)

# Footer
st.markdown("---")
st.caption("🔁 Recurring Transactions | BudgetBuddy | Auto-processed daily")
st.caption("💡 Transactions are automatically added to your income/expenses when the date arrives")
