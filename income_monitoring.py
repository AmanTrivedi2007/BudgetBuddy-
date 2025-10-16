# income_monitoring.py
import streamlit as st
import pandas as pd
from datetime import datetime
from database import add_income_to_db, get_all_income, delete_income_from_db

st.title("💵 Income Monitoring")

# Add income form
st.subheader("➕ Add New Income")

with st.form("income_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        income_source = st.selectbox("Income Source", 
            ["Salary", "Freelance", "Business", "Investment", "Other"])
        income_amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
    
    with col2:
        income_date = st.date_input("Date", value=datetime.now())
        income_notes = st.text_input("Notes (optional)")
    
    submitted = st.form_submit_button("💾 Add Income")
    
    if submitted and income_amount > 0:
        # Save to database
        add_income_to_db(income_source, income_amount, income_date, income_notes)
        st.success(f"✅ Added ₹{income_amount:,.2f} from {income_source}!")
        st.rerun()

st.markdown("---")

# Display income history
st.subheader("📊 Income History")

# Load data from database
income_list = get_all_income()

if income_list:
    # Convert to DataFrame
    df = pd.DataFrame(income_list)
    
    # Display total
    total_income = df['amount'].sum()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.dataframe(df[['source', 'amount', 'date', 'notes']], use_container_width=True)
    
    with col2:
        st.metric("💰 Total Income", f"₹{total_income:,.2f}")
        st.metric("📝 Total Entries", len(income_list))
    
    # Download button
    st.markdown("---")
    
    @st.cache_data
    def convert_to_csv(dataframe):
        return dataframe.to_csv(index=False).encode('utf-8')
    
    csv = convert_to_csv(df)
    st.download_button(
        label="📥 Download Income Data",
        data=csv,
        file_name=f"income_{datetime.now().date()}.csv",
        mime='text/csv',
    )
    
    # Delete option
    with st.expander("🗑️ Delete Income Entry"):
        delete_id = st.selectbox("Select entry to delete", 
            options=[f"{item['id']} - {item['source']} - ₹{item['amount']}" for item in income_list])
        
        if st.button("Delete Selected Entry"):
            selected_id = int(delete_id.split(' - ')[0])
            delete_income_from_db(selected_id)
            st.success("Entry deleted!")
            st.rerun()
else:
    st.info("📝 No income records yet. Add your first income above!")
