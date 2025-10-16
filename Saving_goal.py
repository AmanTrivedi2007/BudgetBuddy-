import streamlit as st
import pandas as pd
from datetime import datetime

st.title("🎯 Saving Goals Tracker")

# Initialize session states
if 'income_list' not in st.session_state:
    st.session_state.income_list = []
if 'expense_list' not in st.session_state:
    st.session_state.expense_list = []
if 'goals_list' not in st.session_state:
    st.session_state.goals_list = []

# Calculate financial summary
total_income = sum(item['amount'] for item in st.session_state.income_list)
total_expense = sum(item['amount'] for item in st.session_state.expense_list)
total_saved_in_goals = sum(goal['saved_amount'] for goal in st.session_state.goals_list)
available_balance = total_income - total_expense - total_saved_in_goals

# Display Financial Overview
st.subheader("💰 Financial Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Income", f"₹{total_income:,.2f}")
with col2:
    st.metric("Total Expenses", f"₹{total_expense:,.2f}")
with col3:
    st.metric("Saved in Goals", f"₹{total_saved_in_goals:,.2f}", delta=f"-{total_saved_in_goals:,.2f}")
with col4:
    st.metric("Available Balance", f"₹{available_balance:,.2f}")

st.markdown("---")

# Create two columns for layout
col_left, col_right = st.columns([1, 1])

# LEFT COLUMN - Create New Goal
with col_left:
    st.subheader("➕ Create New Saving Goal")
    
    with st.form("create_goal_form"):
        goal_name = st.text_input("Goal Name (e.g., New Laptop, Vacation)")
        goal_target = st.number_input("Target Amount (₹)", min_value=0.0, step=1000.0)
        goal_description = st.text_area("Description (optional)")
        
        create_submitted = st.form_submit_button("🎯 Create Goal")
        
        if create_submitted and goal_name and goal_target > 0:
            # Check if goal name already exists
            existing_names = [goal['name'] for goal in st.session_state.goals_list]
            if goal_name in existing_names:
                st.error("❌ Goal with this name already exists!")
            else:
                new_goal = {
                    'name': goal_name,
                    'target_amount': goal_target,
                    'saved_amount': 0.0,
                    'description': goal_description,
                    'created_date': str(datetime.now().date()),
                    'transactions': []  # Store all money additions
                }
                st.session_state.goals_list.append(new_goal)
                st.success(f"✅ Goal '{goal_name}' created successfully!")
                st.rerun()

# RIGHT COLUMN - Add Money to Existing Goal
with col_right:
    st.subheader("💵 Add Money to Goal")
    
    if st.session_state.goals_list:
        with st.form("add_money_form"):
            # Dropdown to select goal
            goal_names = [goal['name'] for goal in st.session_state.goals_list]
            selected_goal_name = st.selectbox("Select Goal", goal_names)
            
            add_amount = st.number_input("Amount to Add (₹)", min_value=0.0, step=100.0)
            add_note = st.text_input("Note (optional)")
            
            add_submitted = st.form_submit_button("💰 Add Money")
            
            if add_submitted and add_amount > 0:
                # Check if enough balance available
                if add_amount > available_balance:
                    st.error(f"❌ Insufficient balance! Available: ₹{available_balance:,.2f}")
                else:
                    # Find the goal and add money
                    for goal in st.session_state.goals_list:
                        if goal['name'] == selected_goal_name:
                            goal['saved_amount'] += add_amount
                            
                            # Record transaction
                            transaction = {
                                'amount': add_amount,
                                'date': str(datetime.now().date()),
                                'note': add_note
                            }
                            goal['transactions'].append(transaction)
                            
                            st.success(f"✅ Added ₹{add_amount:,.2f} to '{selected_goal_name}'!")
                            st.rerun()
    else:
        st.info("📝 Create a goal first to add money!")

st.markdown("---")

# Display All Saving Goals
st.subheader("📊 Your Saving Goals")

if st.session_state.goals_list:
    for idx, goal in enumerate(st.session_state.goals_list):
        # Calculate progress percentage
        progress = (goal['saved_amount'] / goal['target_amount']) * 100 if goal['target_amount'] > 0 else 0
        remaining = goal['target_amount'] - goal['saved_amount']
        
        # Create expandable card for each goal
        with st.expander(f"🎯 {goal['name']} - {progress:.1f}% Complete", expanded=True):
            # Progress bar
            st.progress(min(progress / 100, 1.0))
            
            # Goal details in columns
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Target", f"₹{goal['target_amount']:,.2f}")
            with col2:
                st.metric("Saved", f"₹{goal['saved_amount']:,.2f}")
            with col3:
                st.metric("Remaining", f"₹{remaining:,.2f}")
            
            # Description
            if goal['description']:
                st.write(f"**Description:** {goal['description']}")
            
            st.write(f"**Created on:** {goal['created_date']}")
            
            # Show transaction history
            if goal['transactions']:
                st.markdown("**💵 Transaction History:**")
                trans_df = pd.DataFrame(goal['transactions'])
                st.dataframe(trans_df, use_container_width=True)
            
            # Action buttons
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                # Withdraw money button
                if st.button(f"💸 Withdraw", key=f"withdraw_{idx}"):
                    st.session_state[f'withdraw_mode_{idx}'] = True
            
            with col_btn2:
                # Mark as completed
                if progress >= 100:
                    if st.button(f"✅ Mark Complete", key=f"complete_{idx}"):
                        st.success(f"🎉 Congratulations! You achieved '{goal['name']}'!")
            
            with col_btn3:
                # Delete goal
                if st.button(f"🗑️ Delete Goal", key=f"delete_{idx}"):
                    st.session_state.goals_list.pop(idx)
                    st.rerun()
            
            # Withdraw money form (appears when withdraw button clicked)
            if st.session_state.get(f'withdraw_mode_{idx}', False):
                with st.form(f"withdraw_form_{idx}"):
                    st.write("**Withdraw Money from Goal**")
                    withdraw_amount = st.number_input(
                        "Amount to Withdraw (₹)", 
                        min_value=0.0, 
                        max_value=goal['saved_amount'],
                        step=100.0,
                        key=f"withdraw_input_{idx}"
                    )
                    withdraw_note = st.text_input("Reason for withdrawal", key=f"withdraw_note_{idx}")
                    
                    col_w1, col_w2 = st.columns(2)
                    with col_w1:
                        if st.form_submit_button("Confirm Withdraw"):
                            if withdraw_amount > 0:
                                goal['saved_amount'] -= withdraw_amount
                                
                                # Record withdrawal
                                transaction = {
                                    'amount': -withdraw_amount,
                                    'date': str(datetime.now().date()),
                                    'note': f"Withdrawal: {withdraw_note}"
                                }
                                goal['transactions'].append(transaction)
                                
                                st.success(f"✅ Withdrew ₹{withdraw_amount:,.2f}")
                                st.session_state[f'withdraw_mode_{idx}'] = False
                                st.rerun()
                    
                    with col_w2:
                        if st.form_submit_button("Cancel"):
                            st.session_state[f'withdraw_mode_{idx}'] = False
                            st.rerun()

else:
    st.info("📝 No saving goals yet. Create your first goal above!")
    
    # Show example
    st.markdown("### 💡 Example Goals:")
    st.write("- 🏠 Emergency Fund - ₹50,000")
    st.write("- 💻 New Laptop - ₹60,000")
    st.write("- ✈️ Vacation Trip - ₹40,000")
    st.write("- 📚 Course Fee - ₹25,000")

# Summary statistics at bottom
if st.session_state.goals_list:
    st.markdown("---")
    st.subheader("📈 Goals Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    completed_goals = sum(1 for g in st.session_state.goals_list if g['saved_amount'] >= g['target_amount'])
    total_goals = len(st.session_state.goals_list)
    total_target = sum(g['target_amount'] for g in st.session_state.goals_list)
    overall_progress = (total_saved_in_goals / total_target * 100) if total_target > 0 else 0
    
    with col1:
        st.metric("Total Goals", total_goals)
    with col2:
        st.metric("Completed Goals", completed_goals)
    with col3:
        st.metric("Total Target", f"₹{total_target:,.2f}")
    with col4:
        st.metric("Overall Progress", f"{overall_progress:.1f}%")

# Download goals data
if st.session_state.goals_list:
    st.markdown("---")
    
    @st.cache_data
    def convert_goals_to_csv(goals_list):
        # Flatten the goals data for CSV
        export_data = []
        for goal in goals_list:
            export_data.append({
                'Goal Name': goal['name'],
                'Target Amount': goal['target_amount'],
                'Saved Amount': goal['saved_amount'],
                'Remaining': goal['target_amount'] - goal['saved_amount'],
                'Progress (%)': (goal['saved_amount'] / goal['target_amount'] * 100) if goal['target_amount'] > 0 else 0,
                'Created Date': goal['created_date'],
                'Description': goal['description']
            })
        df = pd.DataFrame(export_data)
        return df.to_csv(index=False).encode('utf-8')
    
    csv = convert_goals_to_csv(st.session_state.goals_list)
    st.download_button(
        label="📥 Download Goals Report",
        data=csv,
        file_name=f"saving_goals_{datetime.now().date()}.csv",
        mime='text/csv',
    )
