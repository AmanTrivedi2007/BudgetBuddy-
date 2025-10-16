# expense.py
import streamlit as st
import pandas as pd
from datetime import datetime
from database import add_expense_to_db, get_all_expenses, get_all_income, get_all_goals, delete_expense_from_db

st.title("💳 Expense Tracking")

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
        # Save to database
        add_expense_to_db(expense_category, expense_amount, expense_date, expense_description)
        st.success(f"✅ Added expense of ₹{expense_amount:,.2f}!")
        st.rerun()

st.markdown("---")

# Display financial summary
st.subheader("💰 Financial Summary")

# Load ALL data including goals
income_list = get_all_income()
expense_list = get_all_expenses()
goals_list = get_all_goals()  # ← ADDED THIS LINE

# Calculate totals INCLUDING goals
total_income = sum(item['amount'] for item in income_list)
total_expense = sum(item['amount'] for item in expense_list)
total_saved_in_goals = sum(goal['saved_amount'] for goal in goals_list)  # ← ADDED THIS LINE
balance = total_income - total_expense - total_saved_in_goals  # ← FIXED THIS LINE

# Display metrics with goals included
col1, col2, col3, col4 = st.columns(4)  # ← CHANGED TO 4 COLUMNS

with col1:
    st.metric("Total Income", f"₹{total_income:,.2f}")
with col2:
    st.metric("Total Expenses", f"₹{total_expense:,.2f}")
with col3:
    st.metric("Saved in Goals", f"₹{total_saved_in_goals:,.2f}")  # ← ADDED THIS
with col4:
    st.metric("Available Balance", f"₹{balance:,.2f}", delta=f"{balance:,.2f}")

# Warning messages
if total_expense > total_income:
    st.warning("⚠️ You're spending more than your income!")
elif balance < 0:
    st.error("❌ Your expenses + savings exceed your income!")
elif balance == 0:
    st.info("ℹ️ You've allocated all your income!")

st.markdown("---")

# Display expense history
st.subheader("📊 Expense History")

if expense_list:
    df = pd.DataFrame(expense_list)
    
    st.dataframe(df[['category', 'amount', 'date', 'description']], use_container_width=True)
    
    # Download button
    @st.cache_data
    def convert_to_csv(dataframe):
        return dataframe.to_csv(index=False).encode('utf-8')
    
    csv = convert_to_csv(df)
    st.download_button(
        label="📥 Download Expense Data",
        data=csv,
        file_name=f"expenses_{datetime.now().date()}.csv",
        mime='text/csv',
    )
    
    # Delete option
    with st.expander("🗑️ Delete Expense Entry"):
        delete_id = st.selectbox("Select entry to delete", 
            options=[f"{item['id']} - {item['category']} - ₹{item['amount']}" for item in expense_list])
        
        if st.button("Delete Selected Entry"):
            selected_id = int(delete_id.split(' - ')[0])
            delete_expense_from_db(selected_id)
            st.success("Entry deleted!")
            st.rerun()
else:
    st.info("📝 No expense records yet. Add your first expense above!")

