import streamlit as st
import pandas as pd

st.title("💵 Income Monitoring")

# Initialize session state
if 'income_list' not in st.session_state:
    st.session_state.income_list = []

# Add income section
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("➕ Add New Income")
    
    with st.form("add_income"):
        income_source = st.selectbox(
            "Income Source",
            ["Salary", "Freelance", "Business", "Investment", "Other"]
        )
        income_amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
        income_date = st.date_input("Date")
        notes = st.text_input("Notes (optional)")
        
        submitted = st.form_submit_button("💾 Add Income")
        
        if submitted and income_amount > 0:
            income_entry = {
                'source': income_source,
                'amount': income_amount,
                'date': str(income_date),
                'notes': notes
            }
            st.session_state.income_list.append(income_entry)
            st.success("Income added successfully!")
            st.rerun()  # Refresh the page

with col2:
    if st.session_state.income_list:
        total = sum(item['amount'] for item in st.session_state.income_list)
        st.metric("Total Income", f"₹{total:,.2f}")
        st.metric("Total Entries", len(st.session_state.income_list))

# Display income history
st.subheader("📊 Income History")

if st.session_state.income_list:
    # Convert list to DataFrame for better display
    df = pd.DataFrame(st.session_state.income_list)
    st.dataframe(df, use_container_width=True)
    
    # Option to clear all data
    if st.button("🗑️ Clear All Income Data"):
        st.session_state.income_list = []
        st.rerun()
else:
    st.info("No income records yet. Add your first income above!")


@st.cache_data
def converter(df):
    return df.to_csv(index=False).encode('utf-8')

# Create DataFrame (empty if no data)
if st.session_state.income_list:
    df = pd.DataFrame(st.session_state.income_list)
    csv = converter(df)
    button_disabled = False
    button_label = "📥 Download Income Entries"
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
    file_name="Income_entry_Data.csv",
    mime='text/csv',
    disabled=button_disabled
)
