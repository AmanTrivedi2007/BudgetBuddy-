# income_monitoring.py
import streamlit as st
import pandas as pd
from datetime import datetime
from database import add_income_to_db, get_all_income, delete_income_from_db

st.title("💵 Income Monitoring")

# Get current logged-in user
user_id = st.session_state.username

# Add income form
st.subheader("➕ Add New Income")

with st.form("income_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        income_source = st.selectbox("Income Source", 
            ["Salary", "Freelance", "Business", "Investment", "Bonus", "Gift", "Other"])
        income_amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0, help="Enter the income amount")
    
    with col2:
        income_date = st.date_input("Date", value=datetime.now(), help="Select income date")
        income_notes = st.text_input("Notes (optional)", placeholder="e.g., Monthly salary, Project payment")
    
    submitted = st.form_submit_button("💾 Add Income", use_container_width=True)
    
    if submitted and income_amount > 0:
        # Save to database WITH user_id
        add_income_to_db(user_id, income_source, income_amount, income_date, income_notes)
        st.success(f"✅ Added ₹{income_amount:,.2f} from {income_source}!")
        st.balloons()
        st.rerun()
    elif submitted and income_amount == 0:
        st.error("❌ Please enter a valid amount greater than 0")

st.markdown("---")

# Display income history
st.subheader("📊 Income History")

# Load user's income data only
income_list = get_all_income(user_id)

if income_list:
    # Convert to DataFrame
    df = pd.DataFrame(income_list)
    
    # Display total income
    total_income = df['amount'].sum()
    
    # Two column layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Sort by date (most recent first)
        df_display = df.sort_values('date', ascending=False)
        st.dataframe(df_display[['source', 'amount', 'date', 'notes']], use_container_width=True)
    
    with col2:
        st.metric("💰 Total Income", f"₹{total_income:,.2f}")
        st.metric("📝 Total Entries", len(income_list))
        
        # Average income
        avg_income = total_income / len(income_list) if len(income_list) > 0 else 0
        st.metric("📊 Average", f"₹{avg_income:,.2f}")
    
    # Income by source breakdown
    with st.expander("📈 View Income Breakdown by Source"):
        source_summary = df.groupby('source')['amount'].agg(['sum', 'count', 'mean']).reset_index()
        source_summary.columns = ['Source', 'Total (₹)', 'Count', 'Average (₹)']
        source_summary['% of Total'] = (source_summary['Total (₹)'] / total_income * 100).round(1)
        source_summary = source_summary.sort_values('Total (₹)', ascending=False)
        st.dataframe(source_summary, use_container_width=True)
    
    # Download button
    st.markdown("---")
    
    @st.cache_data
    def convert_to_csv(dataframe):
        return dataframe.to_csv(index=False).encode('utf-8')
    
    csv = convert_to_csv(df)
    
    col_download, col_empty = st.columns([1, 3])
    with col_download:
        st.download_button(
            label="📥 Download Income Data",
            data=csv,
            file_name=f"income_{user_id}_{datetime.now().date()}.csv",
            mime='text/csv',
            use_container_width=True
        )
    
    # Delete option
    with st.expander("🗑️ Delete Income Entry"):
        st.warning("⚠️ Deleting income will reduce your total income and available balance.")
        
        # Sort by date for deletion (most recent first)
        income_list_sorted = sorted(income_list, key=lambda x: x['date'], reverse=True)
        
        delete_id = st.selectbox("Select entry to delete", 
            options=[f"{item['id']} - {item['date']} - {item['source']} - ₹{item['amount']:,.2f}" for item in income_list_sorted])
        
        if st.button("🗑️ Confirm Delete", type="primary"):
            selected_id = int(delete_id.split(' - ')[0])
            
            # Get amount before deleting for confirmation message
            deleted_income = next((item for item in income_list if item['id'] == selected_id), None)
            deleted_amount = deleted_income['amount'] if deleted_income else 0
            deleted_source = deleted_income['source'] if deleted_income else ""
            
            # Delete from database WITH user_id
            delete_income_from_db(user_id, selected_id)
            st.success(f"✅ Deleted ₹{deleted_amount:,.2f} from {deleted_source}")
            st.rerun()

else:
    st.info("📝 No income records yet. Add your first income above!")
    
    # Show helpful examples when no income
    st.markdown("### 💡 Income Sources Examples")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Regular Income:**")
        st.write("- 💼 Monthly Salary")
        st.write("- 💻 Freelance Projects")
        st.write("- 🏪 Business Revenue")
    
    with col2:
        st.markdown("**Additional Income:**")
        st.write("- 📈 Investment Returns")
        st.write("- 🎁 Bonuses & Gifts")
        st.write("- 💰 Side Hustles")
    
    st.markdown("---")
    st.markdown("### 📌 Quick Tips")
    st.write("1. **Track all income sources** - Even small amounts add up")
    st.write("2. **Add notes** - Help remember details later")
    st.write("3. **Update regularly** - Keep your finances current")
    st.write("4. **Review monthly** - Understand your income patterns")
