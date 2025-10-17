# budget_manager.py - Complete Budget Management with Advanced Features

import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# Set matplotlib/seaborn style
try:
    sns.set_style("whitegrid")
    sns.set_palette("husl")
    PLOTTING_AVAILABLE = True
except:
    PLOTTING_AVAILABLE = False

# Title
st.title("💰 Budget Manager")
st.markdown("*Set limits, track spending, and get real-time alerts*")

# Get current user
if 'username' not in st.session_state or not st.session_state.username:
    st.error("⚠️ Please login first!")
    st.stop()

user_id = st.session_state.username
current_month = datetime.now().strftime('%Y-%m')
current_year = datetime.now().year

# Import database functions
from database import (
    get_all_budgets,
    add_budget_to_db,
    update_budget,
    delete_budget,
    get_category_spending,
    get_all_expenses
)

# ===== HELPER FUNCTIONS =====

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

def get_alert_message(level, remaining, percentage, budget_alerts):
    """Generate alert message based on level"""
    if level == "exceeded":
        return f"🚫 **BUDGET EXCEEDED!** You've overspent by ₹{abs(remaining):,.0f}"
    elif level == "critical" and budget_alerts.get('alert_90', True):
        return f"🔴 **CRITICAL ALERT!** 90% of budget used. Only ₹{remaining:,.0f} remaining"
    elif level == "warning" and budget_alerts.get('alert_75', True):
        return f"🟠 **WARNING!** 75% of budget spent. ₹{remaining:,.0f} left"
    elif level == "caution" and budget_alerts.get('alert_50', True):
        return f"⚠️ **CAUTION!** You've used {percentage:.0f}% of your budget"
    return ""

# ===== SECTION 1: BUDGET OVERVIEW =====
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
    remaining_total = total_budget - total_spent
    overall_percentage = (total_spent / total_budget * 100) if total_budget > 0 else 0
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Total Budget",
            value=f"₹{total_budget:,.0f}",
            help="Combined budget across all categories for this month"
        )
    
    with col2:
        st.metric(
            label="💳 Total Spent",
            value=f"₹{total_spent:,.0f}",
            delta=f"-₹{total_spent:,.0f}",
            delta_color="inverse",
            help="Total expenses recorded this month"
        )
    
    with col3:
        st.metric(
            label="💵 Remaining",
            value=f"₹{remaining_total:,.0f}",
            delta=f"₹{remaining_total:,.0f}" if remaining_total >= 0 else f"-₹{abs(remaining_total):,.0f}",
            delta_color="normal" if remaining_total >= 0 else "inverse",
            help="Budget remaining for this month"
        )
    
    with col4:
        st.metric(
            label="📊 Usage",
            value=f"{overall_percentage:.1f}%",
            help="Percentage of total budget used"
        )
    
    # Overall status indicator
    overall_level = get_alert_level(overall_percentage)
    overall_emoji = get_alert_emoji(overall_level)
    
    if overall_level in ["critical", "exceeded"]:
        st.error(f"{overall_emoji} Overall budget is at {overall_percentage:.0f}%!")
    elif overall_level == "warning":
        st.warning(f"{overall_emoji} You've used {overall_percentage:.0f}% of your total budget")
    elif overall_level == "caution":
        st.info(f"{overall_emoji} Budget usage is at {overall_percentage:.0f}%")
    else:
        st.success(f"{overall_emoji} You're doing great! {100-overall_percentage:.0f}% of budget remaining")
    
    # ===== SECTION 2: CATEGORY-WISE BUDGET STATUS =====
    st.markdown("---")
    st.subheader("📋 Budget Status by Category")
    
    # Sort budgets by percentage used (highest first)
    budget_data = []
    for budget in budgets:
        category = budget['category']
        limit = budget['limit_amount']
        spent = get_category_spending(user_id, category, current_month)
        remaining_amount = limit - spent
        percentage = (spent / limit * 100) if limit > 0 else 0
        
        budget_data.append({
            'budget': budget,
            'spent': spent,
            'remaining': remaining_amount,
            'percentage': percentage,
            'level': get_alert_level(percentage)
        })
    
    # Sort by percentage (highest first)
    budget_data.sort(key=lambda x: x['percentage'], reverse=True)
    
    # Display category cards
    for data in budget_data:
        budget = data['budget']
        spent = data['spent']
        remaining_amount = data['remaining']
        percentage = data['percentage']
        level = data['level']
        
        category = budget['category']
        limit = budget['limit_amount']
        
        alert_color = get_alert_color(level)
        alert_emoji = get_alert_emoji(level)
        
        # Create card
        with st.container():
            st.markdown(f"""
            <div style="background-color: {alert_color}22; padding: 20px; border-radius: 12px; 
                        border-left: 6px solid {alert_color}; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            """, unsafe_allow_html=True)
            
            # Category header
            col1, col2, col3, col4, col5 = st.columns([3, 1.5, 1.5, 1, 1])
            
            with col1:
                st.markdown(f"### {alert_emoji} {category}")
                if budget.get('notes'):
                    st.caption(f"📝 {budget['notes']}")
            
            with col2:
                st.markdown("**💳 Spent**")
                st.markdown(f"₹{spent:,.0f}")
            
            with col3:
                st.markdown("**💰 Budget**")
                st.markdown(f"₹{limit:,.0f}")
            
            with col4:
                st.markdown("**📊 Usage**")
                st.markdown(f"{percentage:.1f}%")
            
            with col5:
                if remaining_amount >= 0:
                    st.markdown("**✅ Left**")
                    st.markdown(f"₹{remaining_amount:,.0f}")
                else:
                    st.markdown("**🚫 Over**")
                    st.markdown(f"₹{abs(remaining_amount):,.0f}")
            
            # Progress bar
            st.progress(min(percentage / 100, 1.0))
            
            # Alert message
            alert_msg = get_alert_message(level, remaining_amount, percentage, budget)
            if alert_msg:
                if level == "exceeded":
                    st.error(alert_msg)
                elif level == "critical":
                    st.error(alert_msg)
                elif level == "warning":
                    st.warning(alert_msg)
                elif level == "caution":
                    st.info(alert_msg)
            
            # Show recent transactions for this category
            category_expenses = [e for e in current_month_expenses if e['category'] == category]
            if category_expenses:
                with st.expander(f"📜 View Recent Transactions ({len(category_expenses)})", expanded=False):
                    for expense in category_expenses[:5]:  # Show last 5
                        st.markdown(f"""
                        - **₹{expense['amount']:,.0f}** • {expense['date']} • {expense.get('description', 'No description')}
                        """)
                    if len(category_expenses) > 5:
                        st.caption(f"...and {len(category_expenses) - 5} more transactions")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # ===== SECTION 3: VISUALIZATIONS =====
    if PLOTTING_AVAILABLE and len(budgets) > 0:
        st.markdown("---")
        st.subheader("📈 Budget Analytics & Insights")
        
        # Create tabs for different visualizations
        viz_tab1, viz_tab2, viz_tab3 = st.tabs(["📊 Budget vs Spending", "🥧 Category Distribution", "📉 Trend Analysis"])
        
        with viz_tab1:
            st.markdown("##### Budget Limits vs Actual Spending")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Horizontal bar chart comparing budget vs spent
                fig1, ax1 = plt.subplots(figsize=(10, 6))
                
                categories = [b['category'] for b in budgets]
                limits = [b['limit_amount'] for b in budgets]
                spent_amounts = [get_category_spending(user_id, b['category'], current_month) for b in budgets]
                
                y_pos = range(len(categories))
                width = 0.35
                
                bars1 = ax1.barh([i - width/2 for i in y_pos], limits, width, 
                                label='Budget Limit', color='#90EE90', alpha=0.8, edgecolor='black')
                bars2 = ax1.barh([i + width/2 for i in y_pos], spent_amounts, width, 
                                label='Spent', color='#FFB6C1', alpha=0.8, edgecolor='black')
                
                ax1.set_yticks(y_pos)
                ax1.set_yticklabels(categories, fontweight='bold')
                ax1.set_xlabel('Amount (₹)', fontweight='bold', fontsize=11)
                ax1.set_title('Budget vs Spending Comparison', fontweight='bold', fontsize=13)
                ax1.legend(loc='lower right')
                ax1.grid(axis='x', alpha=0.3, linestyle='--')
                plt.tight_layout()
                st.pyplot(fig1)
                plt.close()
            
            with col2:
                st.markdown("##### 💡 Insights")
                
                # Calculate insights
                over_budget = [b['category'] for b in budgets 
                              if get_category_spending(user_id, b['category'], current_month) > b['limit_amount']]
                under_50 = [b['category'] for b in budgets 
                           if (get_category_spending(user_id, b['category'], current_month) / b['limit_amount'] * 100) < 50]
                
                if over_budget:
                    st.error(f"🚫 **{len(over_budget)}** categories over budget")
                    for cat in over_budget:
                        st.markdown(f"• {cat}")
                else:
                    st.success("✅ All budgets within limits!")
                
                st.markdown("---")
                
                if under_50:
                    st.success(f"✅ **{len(under_50)}** categories under 50%")
                
                st.markdown("---")
                st.metric("Total Categories", len(budgets))
        
        with viz_tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### Budget Distribution")
                fig2, ax2 = plt.subplots(figsize=(7, 7))
                
                categories = [b['category'] for b in budgets]
                limits = [b['limit_amount'] for b in budgets]
                
                colors_pie = plt.cm.Pastel1(range(len(categories)))
                wedges, texts, autotexts = ax2.pie(limits, labels=categories, autopct='%1.1f%%', 
                                                    startangle=90, colors=colors_pie,
                                                    textprops={'fontweight': 'bold'})
                ax2.axis('equal')
                ax2.set_title('Budget Allocation by Category', fontweight='bold', fontsize=13)
                st.pyplot(fig2)
                plt.close()
            
            with col2:
                st.markdown("##### Spending Distribution")
                fig3, ax3 = plt.subplots(figsize=(7, 7))
                
                spent_amounts = [get_category_spending(user_id, b['category'], current_month) for b in budgets]
                spent_amounts = [s if s > 0 else 0.01 for s in spent_amounts]  # Avoid zero values
                
                wedges, texts, autotexts = ax3.pie(spent_amounts, labels=categories, autopct='%1.1f%%',
                                                    startangle=90, colors=colors_pie,
                                                    textprops={'fontweight': 'bold'})
                ax3.axis('equal')
                ax3.set_title('Actual Spending by Category', fontweight='bold', fontsize=13)
                st.pyplot(fig3)
                plt.close()
        
        with viz_tab3:
            st.markdown("##### Budget Usage Percentage by Category")
            
            fig4, ax4 = plt.subplots(figsize=(10, 6))
            
            categories = [b['category'] for b in budgets]
            percentages = [(get_category_spending(user_id, b['category'], current_month) / b['limit_amount'] * 100) 
                          if b['limit_amount'] > 0 else 0 for b in budgets]
            
            # Color bars based on usage
            bar_colors = [get_alert_color(get_alert_level(p)) for p in percentages]
            
            bars = ax4.bar(categories, percentages, color=bar_colors, alpha=0.7, edgecolor='black', linewidth=1.5)
            
            # Add value labels on bars
            for bar, pct in zip(bars, percentages):
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height,
                        f'{pct:.1f}%', ha='center', va='bottom', fontweight='bold')
            
            # Add 100% reference line
            ax4.axhline(y=100, color='red', linestyle='--', linewidth=2, label='100% Budget Limit')
            
            ax4.set_ylabel('Usage (%)', fontweight='bold', fontsize=11)
            ax4.set_xlabel('Category', fontweight='bold', fontsize=11)
            ax4.set_title('Budget Usage Across Categories', fontweight='bold', fontsize=13)
            ax4.legend()
            ax4.grid(axis='y', alpha=0.3, linestyle='--')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig4)
            plt.close()
    
    # ===== SECTION 4: SPENDING SUMMARY TABLE =====
    st.markdown("---")
    st.subheader("📄 Detailed Budget Summary")
    
    summary_data = []
    for budget in budgets:
        category = budget['category']
        limit = budget['limit_amount']
        spent = get_category_spending(user_id, category, current_month)
        remaining = limit - spent
        percentage = (spent / limit * 100) if limit > 0 else 0
        status = get_alert_emoji(get_alert_level(percentage))
        
        summary_data.append({
            'Status': status,
            'Category': category,
            'Budget': f"₹{limit:,.0f}",
            'Spent': f"₹{spent:,.0f}",
            'Remaining': f"₹{remaining:,.0f}" if remaining >= 0 else f"-₹{abs(remaining):,.0f}",
            'Usage': f"{percentage:.1f}%"
        })
    
    df_summary = pd.DataFrame(summary_data)
    st.dataframe(df_summary, use_container_width=True, hide_index=True)

else:
    # No budgets yet - show onboarding
    st.info("💡 **Welcome to Budget Manager!** You haven't set any budgets yet.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 Why Set Budgets?
        
        - ✅ **Control your spending** in each category
        - ✅ **Get real-time alerts** when approaching limits
        - ✅ **Avoid overspending** and stay on track
        - ✅ **Visualize** where your money goes
        - ✅ **Make better** financial decisions
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Popular Categories
        
        - 🍔 **Food & Dining** - Groceries, restaurants
        - 🚗 **Transportation** - Fuel, public transport
        - 🏠 **Housing** - Rent, utilities, maintenance
        - 🎬 **Entertainment** - Movies, subscriptions
        - 🛒 **Shopping** - Clothes, electronics
        - 💊 **Healthcare** - Medicine, doctor visits
        - 📚 **Education** - Books, courses
        - 💰 **Savings** - Emergency fund, investments
        """)

# ===== SECTION 5: CREATE NEW BUDGET =====
st.markdown("---")
st.subheader("➕ Create New Budget")

with st.form("add_budget_form", clear_on_submit=True):
    st.markdown("##### Budget Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        category = st.text_input(
            "Category Name*",
            placeholder="e.g., Food & Dining, Transportation",
            help="Enter a descriptive name for this budget category"
        )
    
    with col2:
        limit_amount = st.number_input(
            "Monthly Budget Limit (₹)*",
            min_value=0.0,
            value=5000.0,
            step=500.0,
            help="Maximum amount you want to spend in this category per month"
        )
    
    st.markdown("##### 🔔 Alert Preferences")
    st.caption("Choose when you want to receive spending alerts:")
    
    col3, col4, col5 = st.columns(3)
    
    with col3:
        alert_50 = st.checkbox("⚠️ 50% Alert", value=True, 
                               help="Notify when you've spent half your budget")
    
    with col4:
        alert_75 = st.checkbox("🟠 75% Alert", value=True, 
                               help="Notify when you've spent three-quarters of your budget")
    
    with col5:
        alert_90 = st.checkbox("🔴 90% Alert", value=True, 
                               help="Critical alert when approaching budget limit")
    
    notes = st.text_area(
        "Notes (Optional)",
        placeholder="e.g., Monthly food budget including dining out and groceries",
        help="Add any additional information or reminders about this budget"
    )
    
    # Show estimated daily/weekly budget
    if limit_amount > 0:
        daily_budget = limit_amount / 30
        weekly_budget = limit_amount / 4.33
        
        st.markdown("##### 📅 Budget Breakdown")
        breakdown_col1, breakdown_col2, breakdown_col3 = st.columns(3)
        
        with breakdown_col1:
            st.info(f"**Daily:** ₹{daily_budget:.0f}")
        with breakdown_col2:
            st.info(f"**Weekly:** ₹{weekly_budget:.0f}")
        with breakdown_col3:
            st.info(f"**Monthly:** ₹{limit_amount:,.0f}")
    
    submit_budget = st.form_submit_button("💾 Create Budget", use_container_width=True, type="primary")
    
    if submit_budget:
        if not category or category.strip() == "":
            st.error("❌ Please enter a category name")
        elif limit_amount <= 0:
            st.error("❌ Budget limit must be greater than 0")
        else:
            category_clean = category.strip().title()
            if add_budget_to_db(user_id, category_clean, limit_amount, alert_50, alert_75, alert_90, notes):
                st.success(f"✅ Budget created successfully!")
                st.success(f"💰 **{category_clean}**: ₹{limit_amount:,.0f}/month")
                st.balloons()
                st.rerun()
            else:
                st.error(f"❌ Budget for '{category_clean}' already exists!")
                st.info("💡 Tip: Update the existing budget below instead of creating a duplicate.")

# ===== SECTION 6: MANAGE EXISTING BUDGETS =====
if budgets:
    st.markdown("---")
    st.subheader("🗂️ Manage Existing Budgets")
    
    manage_tab1, manage_tab2 = st.tabs(["✏️ Update Budget", "🗑️ Delete Budget"])
    
    with manage_tab1:
        update_col1, update_col2 = st.columns([2, 1])
        
        with update_col1:
            categories = [b['category'] for b in budgets]
            selected_category = st.selectbox(
                "Select category to update",
                categories,
                help="Choose which budget you want to modify"
            )
        
        if selected_category:
            selected_budget = next((b for b in budgets if b['category'] == selected_category), None)
            
            if selected_budget:
                current_spent = get_category_spending(user_id, selected_category, current_month)
                
                st.info(f"💳 **Current spending:** ₹{current_spent:,.0f} this month")
                
                with st.form("update_budget_form"):
                    st.markdown("##### Update Budget Details")
                    
                    new_limit = st.number_input(
                        "New Monthly Budget Limit (₹)",
                        min_value=0.0,
                        value=float(selected_budget['limit_amount']),
                        step=500.0
                    )
                    
                    st.markdown("##### Alert Settings")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        new_alert_50 = st.checkbox("⚠️ 50% Alert", value=bool(selected_budget['alert_50']))
                    with col2:
                        new_alert_75 = st.checkbox("🟠 75% Alert", value=bool(selected_budget['alert_75']))
                    with col3:
                        new_alert_90 = st.checkbox("🔴 90% Alert", value=bool(selected_budget['alert_90']))
                    
                    new_notes = st.text_area("Notes", value=selected_budget.get('notes', ''))
                    
                    submit_update = st.form_submit_button("💾 Update Budget", use_container_width=True, type="primary")
                    
                    if submit_update:
                        if new_limit <= 0:
                            st.error("❌ Budget limit must be greater than 0")
                        else:
                            if update_budget(user_id, selected_category, new_limit, 
                                           new_alert_50, new_alert_75, new_alert_90, new_notes):
                                st.success(f"✅ Budget updated successfully!")
                                st.success(f"💰 **{selected_category}**: ₹{new_limit:,.0f}/month")
                                st.rerun()
                            else:
                                st.error("❌ Error updating budget")
    
    with manage_tab2:
        delete_col1, delete_col2 = st.columns([2, 1])
        
        with delete_col1:
            delete_category = st.selectbox(
                "Select category to delete",
                [b['category'] for b in budgets],
                key="delete_select",
                help="Choose which budget you want to remove permanently"
            )
        
        st.warning("⚠️ **Warning:** Deleting a budget is permanent and cannot be undone!")
        
        if delete_category:
            delete_budget_data = next((b for b in budgets if b['category'] == delete_category), None)
            if delete_budget_data:
                current_spent = get_category_spending(user_id, delete_category, current_month)
                st.info(f"💳 This category has ₹{current_spent:,.0f} in spending this month")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Delete Budget", type="secondary", use_container_width=True):
                if delete_budget(user_id, delete_category):
                    st.success(f"✅ Budget deleted: **{delete_category}**")
                    st.rerun()
                else:
                    st.error("❌ Error deleting budget")
        
        with col2:
            st.markdown("")  # Spacer

# ===== SECTION 7: TIPS & INFORMATION =====
st.markdown("---")
with st.expander("💡 Budget Management Tips & Info", expanded=False):
    tip_col1, tip_col2 = st.columns(2)
    
    with tip_col1:
        st.markdown("""
        ### 🎯 How Budgets Work
        
        **Alert Levels:**
        - **50% Alert** ⚠️: Halfway through your budget
        - **75% Alert** 🟠: Three-quarters spent
        - **90% Alert** 🔴: Critical - approaching limit
        - **100%+ Exceeded** 🚫: Over budget
        
        **Budget Cycle:**
        - Budgets are tracked monthly
        - Spending resets automatically each month
        - Alerts are based on current month spending
        - Historical data is preserved
        """)
    
    with tip_col2:
        st.markdown("""
        ### 🏆 Best Practices
        
        **Setting Budgets:**
        - Review past 2-3 months of spending
        - Set realistic, achievable limits
        - Include a buffer (5-10%) for unexpected costs
        - Separate needs vs wants categories
        
        **Monitoring:**
        - Check budget status weekly
        - Review and adjust monthly
        - Track trends over time
        - Celebrate wins when under budget
        """)

# Footer
st.markdown("---")
st.caption("💰 Budget Manager | BudgetBuddy")
st.caption(f"📅 Tracking Period: {current_month} | Budgets reset monthly at the start of each month")
st.caption("💡 Pro Tip: Set budgets for all major spending categories to get complete financial visibility")
