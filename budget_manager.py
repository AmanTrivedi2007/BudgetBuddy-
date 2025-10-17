# budget_manager.py - Budget Management with Error Handling

import streamlit as st
import pandas as pd
from datetime import datetime

# Title
st.title("💰 Budget Manager")
st.markdown("*Set limits, track spending, and get real-time alerts*")

# Get current user
if 'username' not in st.session_state or not st.session_state.username:
    st.error("⚠️ Please login first!")
    st.stop()

user_id = st.session_state.username
current_month = datetime.now().strftime('%Y-%m')

# Try to import database functions
try:
    from database import (
        get_all_budgets,
        add_budget_to_db,
        update_budget,
        delete_budget,
        get_category_spending,
        get_all_expenses
    )
except ImportError as e:
    st.error(f"❌ Database functions not available: {e}")
    st.error("⚠️ Please make sure database.py has all budget functions!")
    st.info("""
    **Missing Functions in database.py:**
    - get_all_budgets(user_id)
    - add_budget_to_db(...)
    - update_budget(...)
    - delete_budget(...)
    - get_category_spending(user_id, category, month)
    - get_all_expenses(user_id)
    
    **Solution:** Update your database.py file with the complete version.
    """)
    st.stop()

# Try to import matplotlib
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    sns.set_style("whitegrid")
    PLOTTING_AVAILABLE = True
except ImportError:
    st.warning("⚠️ Matplotlib/Seaborn not installed. Charts will be disabled.")
    PLOTTING_AVAILABLE = False

# Helper function to determine alert level
def get_alert_level(percentage):
    """Return alert level based on percentage spent"""
    if percentage >= 100:
        return "exceeded"
    elif percentage >= 90:
        return "critical"
    elif percentage >= 75:
        return "warning"
    elif percentage >= 50:
        return "caution"
    else:
        return "safe"

def get_alert_color(level):
    """Return color based on alert level"""
    colors = {
        "safe": "#28a745",
        "caution": "#ffc107",
        "warning": "#fd7e14",
        "critical": "#dc3545",
        "exceeded": "#6c757d"
    }
    return colors.get(level, "#6c757d")

def get_alert_emoji(level):
    """Return emoji based on alert level"""
    emojis = {
        "safe": "✅",
        "caution": "⚠️",
        "warning": "🟠",
        "critical": "🔴",
        "exceeded": "🚫"
    }
    return emojis.get(level, "ℹ️")

# === SECTION 1: OVERVIEW ===
st.markdown("---")
st.subheader("📊 Budget Overview")

budgets = get_all_budgets(user_id)

if budgets:
    # Calculate totals
    total_budget = sum([b['limit_amount'] for b in budgets])
    
    # Get all expenses for current month
    all_expenses = get_all_expenses(user_id)
    current_month_expenses = [
        e for e in all_expenses 
        if e['date'].startswith(current_month)
    ]
    total_spent = sum([e['amount'] for e in current_month_expenses])
    remaining = total_budget - total_spent
    
    # Display summary cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Total Budget",
            value=f"₹{total_budget:,.0f}",
            help="Total budget across all categories"
        )
    
    with col2:
        st.metric(
            label="💳 Total Spent",
            value=f"₹{total_spent:,.0f}",
            delta=f"-₹{total_spent:,.0f}",
            delta_color="inverse",
            help="Total spent this month"
        )
    
    with col3:
        st.metric(
            label="💵 Remaining",
            value=f"₹{remaining:,.0f}",
            delta=f"₹{remaining:,.0f}" if remaining >= 0 else f"-₹{abs(remaining):,.0f}",
            delta_color="normal" if remaining >= 0 else "inverse",
            help="Budget remaining this month"
        )
    
    with col4:
        overall_percentage = (total_spent / total_budget * 100) if total_budget > 0 else 0
        st.metric(
            label="📊 Usage",
            value=f"{overall_percentage:.1f}%",
            help="Percentage of budget used"
        )
    
    # === SECTION 2: BUDGET STATUS BY CATEGORY ===
    st.markdown("---")
    st.subheader("📋 Budget Status by Category")
    
    # Create budget status cards
    for budget in budgets:
        category = budget['category']
        limit = budget['limit_amount']
        spent = get_category_spending(user_id, category, current_month)
        remaining_amount = limit - spent
        percentage = (spent / limit * 100) if limit > 0 else 0
        
        # Determine alert level
        alert_level = get_alert_level(percentage)
        alert_color = get_alert_color(alert_level)
        alert_emoji = get_alert_emoji(alert_level)
        
        # Display category card
        with st.container():
            st.markdown(f"""
            <div style="background-color: {alert_color}22; padding: 15px; border-radius: 10px; 
                        border-left: 5px solid {alert_color}; margin-bottom: 15px;">
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.markdown(f"### {alert_emoji} {category}")
                if budget['notes']:
                    st.caption(budget['notes'])
            
            with col2:
                st.markdown(f"**Spent:** ₹{spent:,.0f}")
                st.markdown(f"**Limit:** ₹{limit:,.0f}")
            
            with col3:
                if remaining_amount >= 0:
                    st.success(f"₹{remaining_amount:,.0f} left")
                else:
                    st.error(f"₹{abs(remaining_amount):,.0f} over")
            
            with col4:
                st.markdown(f"**{percentage:.1f}%** used")
                st.progress(min(percentage / 100, 1.0))
            
            # Alert messages
            if alert_level == "exceeded":
                st.error(f"🚫 Budget exceeded by ₹{abs(remaining_amount):,.0f}!")
            elif alert_level == "critical" and budget['alert_90']:
                st.error(f"🔴 90% of budget used! Only ₹{remaining_amount:,.0f} left")
            elif alert_level == "warning" and budget['alert_75']:
                st.warning(f"🟠 75% of budget used! ₹{remaining_amount:,.0f} remaining")
            elif alert_level == "caution" and budget['alert_50']:
                st.info(f"⚠️ 50% of budget used. ₹{remaining_amount:,.0f} left")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # === SECTION 3: VISUALIZATIONS ===
    if PLOTTING_AVAILABLE and len(budgets) > 0:
        st.markdown("---")
        st.subheader("📈 Budget Analytics")
        
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            # Pie chart: Budget vs Spent
            st.markdown("##### Budget Distribution")
            fig1, ax1 = plt.subplots(figsize=(6, 6))
            
            categories = [b['category'] for b in budgets]
            limits = [b['limit_amount'] for b in budgets]
            
            ax1.pie(limits, labels=categories, autopct='%1.1f%%', startangle=90)
            ax1.axis('equal')
            st.pyplot(fig1)
            plt.close()
        
        with viz_col2:
            # Bar chart: Spent vs Limit
            st.markdown("##### Spending vs Budget Limits")
            fig2, ax2 = plt.subplots(figsize=(6, 6))
            
            categories = [b['category'] for b in budgets]
            limits = [b['limit_amount'] for b in budgets]
            spent_amounts = [get_category_spending(user_id, b['category'], current_month) for b in budgets]
            
            x = range(len(categories))
            width = 0.35
            
            ax2.barh([i - width/2 for i in x], limits, width, label='Budget', color='#90EE90', alpha=0.7)
            ax2.barh([i + width/2 for i in x], spent_amounts, width, label='Spent', color='#FFB6C1', alpha=0.7)
            
            ax2.set_yticks(x)
            ax2.set_yticklabels(categories)
            ax2.set_xlabel('Amount (₹)')
            ax2.legend()
            ax2.grid(axis='x', alpha=0.3)
            
            st.pyplot(fig2)
            plt.close()

else:
    st.info("💡 **No budgets set yet!** Create your first budget below to start tracking spending.")
    
    st.markdown("""
    ### 🎯 Why Set Budgets?
    
    - ✅ **Control spending** - Set limits for each category
    - ✅ **Get alerts** - Know when you're close to your limit
    - ✅ **Avoid overspending** - Stay within your financial goals
    - ✅ **Track progress** - See exactly where your money goes
    - ✅ **Better planning** - Make informed financial decisions
    
    **Popular Categories:**
    - 🍔 Food & Dining
    - 🚗 Transportation
    - 🏠 Rent & Utilities
    - 🎬 Entertainment
    - 🛒 Shopping
    - 💊 Healthcare
    """)

# === SECTION 4: ADD NEW BUDGET ===
st.markdown("---")
st.subheader("➕ Create New Budget")

with st.form("add_budget_form", clear_on_submit=True):
    st.markdown("##### Budget Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        category = st.text_input(
            "Category*",
            placeholder="e.g., Food, Transport, Entertainment",
            help="Enter category name (e.g., Food, Transport)"
        )
    
    with col2:
        limit_amount = st.number_input(
            "Budget Limit (₹)*",
            min_value=0.0,
            value=5000.0,
            step=500.0,
            help="Maximum amount you want to spend in this category per month"
        )
    
    st.markdown("##### Alert Settings")
    st.caption("Get notified when you reach these thresholds:")
    
    col3, col4, col5 = st.columns(3)
    
    with col3:
        alert_50 = st.checkbox("⚠️ 50% Alert", value=True, help="Alert when 50% of budget is used")
    
    with col4:
        alert_75 = st.checkbox("🟠 75% Alert", value=True, help="Alert when 75% of budget is used")
    
    with col5:
        alert_90 = st.checkbox("🔴 90% Alert", value=True, help="Alert when 90% of budget is used")
    
    notes = st.text_area(
        "Notes (optional)",
        placeholder="e.g., Monthly food budget including dining out",
        help="Add any additional notes about this budget"
    )
    
    submit_budget = st.form_submit_button("💾 Create Budget", use_container_width=True, type="primary")
    
    if submit_budget:
        if not category or category.strip() == "":
            st.error("❌ Please enter a category name")
        elif limit_amount <= 0:
            st.error("❌ Budget limit must be greater than 0")
        else:
            category_clean = category.strip()
            if add_budget_to_db(user_id, category_clean, limit_amount, alert_50, alert_75, alert_90, notes):
                st.success(f"✅ Budget created for **{category_clean}**: ₹{limit_amount:,.0f}/month")
                st.balloons()
                st.rerun()
            else:
                st.error(f"❌ Budget for '{category_clean}' already exists! Update it below instead.")

# === SECTION 5: MANAGE EXISTING BUDGETS ===
if budgets:
    st.markdown("---")
    st.subheader("🗂️ Manage Budgets")
    
    # Update budget
    with st.expander("✏️ Update Budget", expanded=False):
        update_col1, update_col2 = st.columns([2, 1])
        
        with update_col1:
            categories = [b['category'] for b in budgets]
            selected_category = st.selectbox(
                "Select category to update",
                categories,
                help="Choose which budget to modify"
            )
        
        if selected_category:
            selected_budget = next((b for b in budgets if b['category'] == selected_category), None)
            
            if selected_budget:
                with st.form("update_budget_form"):
                    new_limit = st.number_input(
                        "New Budget Limit (₹)",
                        min_value=0.0,
                        value=float(selected_budget['limit_amount']),
                        step=500.0
                    )
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        new_alert_50 = st.checkbox("⚠️ 50%", value=bool(selected_budget['alert_50']))
                    with col2:
                        new_alert_75 = st.checkbox("🟠 75%", value=bool(selected_budget['alert_75']))
                    with col3:
                        new_alert_90 = st.checkbox("🔴 90%", value=bool(selected_budget['alert_90']))
                    
                    new_notes = st.text_area("Notes", value=selected_budget['notes'] or "")
                    
                    submit_update = st.form_submit_button("💾 Update Budget", use_container_width=True, type="primary")
                    
                    if submit_update:
                        if update_budget(user_id, selected_category, new_limit, new_alert_50, new_alert_75, new_alert_90, new_notes):
                            st.success(f"✅ Budget updated: **{selected_category}** - ₹{new_limit:,.0f}")
                            st.rerun()
                        else:
                            st.error("❌ Error updating budget")
    
    # Delete budget
    with st.expander("🗑️ Delete Budget", expanded=False):
        delete_col1, delete_col2 = st.columns([2, 1])
        
        with delete_col1:
            delete_category = st.selectbox(
                "Select category to delete",
                [b['category'] for b in budgets],
                key="delete_select",
                help="Choose which budget to remove"
            )
        
        with delete_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ Delete", type="secondary", use_container_width=True):
                if delete_budget(user_id, delete_category):
                    st.success(f"✅ Budget deleted: **{delete_category}**")
                    st.rerun()
                else:
                    st.error("❌ Error deleting budget")

# === SECTION 6: INFORMATION ===
st.markdown("---")
with st.expander("💡 How Budget Alerts Work", expanded=False):
    st.markdown("""
    ### Budget Alert System
    
    **Alert Levels:**
    - **50% Alert** ⚠️: Notifies when you've spent half your budget
    - **75% Alert** 🟠: Warning when you're at three-quarters
    - **90% Alert** 🔴: Critical alert when nearing limit
    - **100% Exceeded** 🚫: Budget limit has been surpassed
    
    **How It Works:**
    1. Set a monthly budget for each spending category
    2. Choose which alert levels you want to receive
    3. Track spending in real-time
    4. Get visual indicators (colors, emojis) based on usage
    5. Budgets reset automatically at the start of each month
    
    **Tips:**
    - Set realistic budgets based on past spending
    - Review and adjust budgets monthly
    - Enable all alerts to stay informed
    - Use notes to remember why you set specific limits
    - Track multiple categories for complete coverage
    """)

# Footer
st.markdown("---")
st.caption("💰 Budget Manager | BudgetBuddy | Track spending & stay within limits")
st.caption(f"📅 Current Month: {current_month} | Budgets reset monthly")
