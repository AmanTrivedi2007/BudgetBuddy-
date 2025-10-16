import streamlit as st
import pandas as pd

st.title("💳 Expense Tracking")

# Initialize expense list
if 'expense_list' not in st.session_state:
    st.session_state.expense_list = []

# Initialize income list if not exists (for safety)
if 'income_list' not in st.session_state:
    st.session_state.income_list = []

# Add expense form
with st.form("expense_form"):
    st.subheader("Add New Expense")
    
    expense_category = st.selectbox("Category", 
        ["Food", "Transport", "Bills", "Entertainment", "Shopping", "Other"])
    expense_amount = st.number_input("Amount (₹)", min_value=0.0, step=50.0)
    expense_date = st.date_input("Date")
    description = st.text_input("Description")
    
    submitted = st.form_submit_button("➕ Add Expense")
    
    if submitted and expense_amount > 0:
        expense_entry = {
            'category': expense_category,
            'amount': expense_amount,
            'date': str(expense_date),
            'description': description
        }
        # Add to session state
        st.session_state.expense_list.append(expense_entry)
        st.success("Expense added!")

# Display expenses
if st.session_state.expense_list:
    df = pd.DataFrame(st.session_state.expense_list)
    st.dataframe(df)
    
    total_expense = sum(item['amount'] for item in st.session_state.expense_list)
    st.metric("Total Expenses", f"₹{total_expense:,.2f}")
else:
    st.info("No expenses added yet!")

# Calculate balance using income from other page
st.markdown("---")
st.subheader("💰 Financial Summary")

col1, col2, col3 = st.columns(3)

with col1:
    # Access income_list from income_monitoring.py
    total_income = sum(item['amount'] for item in st.session_state.income_list)
    st.metric("Total Income", f"₹{total_income:,.2f}")

with col2:
    total_expense = sum(item['amount'] for item in st.session_state.expense_list)
    st.metric("Total Expenses", f"₹{total_expense:,.2f}")

with col3:
    balance = total_income - total_expense
    st.metric("Balance", f"₹{balance:,.2f}", delta=f"{balance:,.2f}")

# Show warning if spending more than income
if total_expense > total_income:
    st.warning("⚠️ You're spending more than your income!")

@st.cache_data
def converter(df):
    return df.to_csv(index=False).encode('utf-8')

# Create DataFrame (empty if no data)
if st.session_state.income_list:
    df = pd.DataFrame(st.session_state.expense_list)
    csv = converter(df)
    button_disabled = False
    button_label = "📥 Download Expense Entries"
    st.success("You can download the Data file")
else:
    df = pd.DataFrame()  # Empty DataFrame
    csv = ""
    button_disabled = True
    button_label = "📥 No Data to Download"
    st.info("You need at least one entry to download the Data")

# Button always shows but disabled when no data
st.download_button(
    label=button_label,
    data=csv if csv else b"",  # Empty bytes if no data
    file_name="Expense_entry_Data.csv",
    mime='text/csv',
    disabled=button_disabled
)