# expense.py
import streamlit as st
import pandas as pd
from datetime import datetime
from database import add_expense_to_db, get_all_expenses, get_all_income, get_all_goals, delete_expense_from_db

st.title("💳 Expense Tracking")

# Get current user
user_id = st.session_state.username

# Load current financial status to show at top
income_list = get_all_income(user_id)
expense_list = get_all_expenses(user_id)
goals_list = get_all_goals(user_id)

total_income = sum(item['amount'] for item in income_list)
total_expense = sum(item['amount'] for item in expense_list)
total_saved_in_goals = sum(goal['saved_amount'] for goal in goals_list)
available_balance = total_income - total_expense - total_saved_in_goals

# Show balance alert at top if insufficient
if available_balance <= 0:
    st.error(f"⚠️ **No available balance!** Current balance: ₹{available_balance:,.2f}")
    st.warning("💡 Add income first before adding expenses.")

# Add expense form
st.subheader("➕ Add New Expense")

with st.form("expense_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        expense_category = st.selectbox("Category", 
            ["Food", "Transport", "Bills", "Entertainment", "Shopping", "Healthcare", "Education", "Other"])
        expense_amount = st.number_input("Amount (₹)", min_value=0.0, step=50.0)
    
    with col2:
        expense_date = st.date_input("Date", value=datetime.now())
        expense_description = st.text_input("Description (optional)")
    
    submitted = st.form_submit_button("💾 Add Expense")
    
    if submitted and expense_amount > 0:
        # Reload to get latest balance
        income_list_check = get_all_income(user_id)
        expense_list_check = get_all_expenses(user_id)
        goals_list_check = get_all_goals(user_id)
        
        total_income_check = sum(item['amount'] for item in income_list_check)
        total_expense_check = sum(item['amount'] for item in expense_list_check)
        total_saved_in_goals_check = sum(goal['saved_amount'] for goal in goals_list_check)
        available_balance_check = total_income_check - total_expense_check - total_saved_in_goals_check
        
        # Validate: Check if enough balance available
        if expense_amount > available_balance_check:
            st.error(f"❌ Insufficient balance!")
            st.warning(f"💡 You're trying to spend ₹{expense_amount:,.2f} but only have ₹{available_balance_check:,.2f} available.")
            
            # Show breakdown
            with st.expander("💰 See Balance Breakdown"):
                st.write(f"**Total Income:** ₹{total_income_check:,.2f}")
                st.write(f"**Already Spent:** ₹{total_expense_check:,.2f}")
                st.write(f"**Saved in Goals:** ₹{total_saved_in_goals_check:,.2f}")
                st.write(f"**Available:** ₹{available_balance_check:,.2f}")
                st.divider()
                st.info("💡 **Solutions:**\n- Add more income\n- Reduce expense amount\n- Withdraw money from goals")
        else:
            # Save to database with user_id
            add_expense_to_db(user_id, expense_category, expense_amount, expense_date, expense_description)
            st.success(f"✅ Added expense of ₹{expense_amount:,.2f}!")
            st.balloons()
            st.rerun()

st.markdown("---")

# Display financial summary
st.subheader("💰 Financial Summary")

# Reload data for display
income_list = get_all_income(user_id)
expense_list = get_all_expenses(user_id)
goals_list = get_all_goals(user_id)

# Calculate totals
total_income = sum(item['amount'] for item in income_list)
total_expense = sum(item['amount'] for item in expense_list)
total_saved_in_goals = sum(goal['saved_amount'] for goal in goals_list)
balance = total_income - total_expense - total_saved_in_goals

# Display metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Income", f"₹{total_income:,.2f}")
with col2:
    st.metric("Total Expenses", f"₹{total_expense:,.2f}")
with col3:
    st.metric("Saved in Goals", f"₹{total_saved_in_goals:,.2f}")
with col4:
    # Show balance with color indicator
    if balance < 0:
        st.metric("Available Balance", f"₹{balance:,.2f}", delta=f"₹{balance:,.2f}", delta_color="inverse")
    elif balance == 0:
        st.metric("Available Balance", f"₹{balance:,.2f}", delta="₹0.00")
    else:
        st.metric("Available Balance", f"₹{balance:,.2f}", delta=f"₹{balance:,.2f}")

# Warning messages based on balance
if balance < 0:
    st.error(f"🚨 **Critical Alert:** You've overspent by ₹{abs(balance):,.2f}!")
    st.warning("💡 **Immediate Action Required:**")
    st.write("- Add more income to cover the deficit")
    st.write("- Delete unnecessary expenses")
    st.write("- Withdraw money from savings goals")
elif balance == 0:
    st.success("✅ Perfect! You've allocated 100% of your income.")
    st.info("💡 Consider adding any new income before spending more.")
elif balance > 0 and balance < 1000:
    st.warning(f"⚠️ Low balance warning: Only ₹{balance:,.2f} remaining")
else:
    st.success(f"✅ Great! You have ₹{balance:,.2f} available to spend or save.")

# Spending percentage indicator
if total_income > 0:
    expense_percentage = (total_expense / total_income) * 100
    goals_percentage = (total_saved_in_goals / total_income) * 100
    available_percentage = (balance / total_income) * 100 if balance > 0 else 0
    
    st.markdown("#### 📊 Income Allocation")
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Spent", f"{expense_percentage:.1f}%")
    with col_b:
        st.metric("Saved", f"{goals_percentage:.1f}%")
    with col_c:
        st.metric("Available", f"{available_percentage:.1f}%")

st.markdown("---")

# Display expense history
st.subheader("📊 Expense History")

if expense_list:
    df = pd.DataFrame(expense_list)
    
    # Display options
    col_view1, col_view2 = st.columns(2)
    with col_view1:
        sort_by = st.selectbox("Sort by", ["Most Recent", "Highest Amount", "Category"])
    with col_view2:
        filter_category = st.selectbox("Filter Category", ["All"] + ["Food", "Transport", "Bills", "Entertainment", "Shopping", "Healthcare", "Education", "Other"])
    
    # Apply filters
    display_df = df.copy()
    if filter_category != "All":
        display_df = display_df[display_df['category'] == filter_category]
    
    # Apply sorting
    if sort_by == "Most Recent":
        display_df = display_df.sort_values('date', ascending=False)
    elif sort_by == "Highest Amount":
        display_df = display_df.sort_values('amount', ascending=False)
    elif sort_by == "Category":
        display_df = display_df.sort_values('category')
    
    # Show filtered data
    st.dataframe(display_df[['category', 'amount', 'date', 'description']], use_container_width=True)
    
    # Category-wise summary
    with st.expander("📊 View Category Summary"):
        category_summary = df.groupby('category')['amount'].agg(['sum', 'count', 'mean']).reset_index()
        category_summary.columns = ['Category', 'Total (₹)', 'Count', 'Avg (₹)']
        category_summary['% of Total'] = (category_summary['Total (₹)'] / category_summary['Total (₹)'].sum() * 100).round(1)
        category_summary = category_summary.sort_values('Total (₹)', ascending=False)
        st.dataframe(category_summary, use_container_width=True)
    
    # Download button
    st.markdown("---")
    
    @st.cache_data
    def convert_to_csv(dataframe):
        return dataframe.to_csv(index=False).encode('utf-8')
    
    csv = convert_to_csv(df)
    st.download_button(
        label="📥 Download Expense Data",
        data=csv,
        file_name=f"expenses_{user_id}_{datetime.now().date()}.csv",
        mime='text/csv',
    )
    
    # Delete option
    with st.expander("🗑️ Delete Expense Entry"):
        st.warning("⚠️ Deleting an expense will add money back to your available balance.")
        
        # Show expenses in reverse chronological order for deletion
        expense_list_sorted = sorted(expense_list, key=lambda x: x['date'], reverse=True)
        delete_id = st.selectbox("Select entry to delete", 
            options=[f"{item['id']} - {item['date']} - {item['category']} - ₹{item['amount']:,.2f}" for item in expense_list_sorted])
        
        if st.button("🗑️ Confirm Delete", type="primary"):
            selected_id = int(delete_id.split(' - ')[0])
            
            # Get amount before deleting to show in success message
            deleted_expense = next((item for item in expense_list if item['id'] == selected_id), None)
            deleted_amount = deleted_expense['amount'] if deleted_expense else 0
            
            delete_expense_from_db(user_id, selected_id)
            st.success(f"✅ Deleted! ₹{deleted_amount:,.2f} added back to your balance.")
            st.rerun()

else:
    st.info("📝 No expense records yet. Add your first expense above!")
    
    # Show helpful tips when no expenses
    st.markdown("### 💡 Quick Tips")
    st.write("1. 📝 Track every expense, no matter how small")
    st.write("2. 🏷️ Categorize expenses for better insights")
    st.write("3. 📅 Review your spending weekly")
    st.write("4. 🎯 Set spending limits for each category")
    st.write("5. 💰 Always check available balance before spending")
