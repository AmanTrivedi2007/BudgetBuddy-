# budget_manager.py - Complete Budget Management with Real-Time Alerts
import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# Set seaborn style
sns.set_style("whitegrid")
sns.set_palette("husl")

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

# Import database functions (these will be added to database.py)
from database import (
    get_all_budgets, 
    add_budget_to_db, 
    update_budget, 
    delete_budget,
    get_category_spending,
    get_all_expenses
)

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
        return "info"
    else:
        return "normal"

# Helper function to get alert icon and color
def get_alert_style(alert_level):
    """Return icon and color for alert level"""
    styles = {
        "exceeded": {"icon": "🚨", "color": "#FF4444", "bg": "#FFEEEE"},
        "critical": {"icon": "⚠️", "color": "#FF8800", "bg": "#FFF4E6"},
        "warning": {"icon": "📊", "color": "#FFA500", "bg": "#FFF8E6"},
        "info": {"icon": "💡", "color": "#4169E1", "bg": "#E6F3FF"},
        "normal": {"icon": "✅", "color": "#00AA00", "bg": "#E6FFE6"}
    }
    return styles.get(alert_level, styles["normal"])

# === SECTION 1: BUDGET OVERVIEW ===
st.markdown("---")
st.subheader("📊 Monthly Budget Overview")

budgets = get_all_budgets(user_id)

if budgets:
    # Calculate totals
    total_budget = sum([b['limit_amount'] for b in budgets])
    total_spent = sum([get_category_spending(user_id, b['category'], current_month) for b in budgets])
    remaining = total_budget - total_spent
    overall_percentage = (total_spent / total_budget * 100) if total_budget > 0 else 0
    
    # Display summary cards in 4 columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Total Budget",
            value=f"₹{total_budget:,.0f}",
            help="Total budget limit for all categories this month"
        )
    
    with col2:
        st.metric(
            label="💳 Total Spent",
            value=f"₹{total_spent:,.0f}",
            delta=f"-₹{total_spent:,.0f}",
            delta_color="inverse",
            help="Total amount spent across all categories"
        )
    
    with col3:
        st.metric(
            label="💵 Remaining",
            value=f"₹{remaining:,.0f}",
            delta=f"₹{remaining:,.0f}" if remaining >= 0 else f"-₹{abs(remaining):,.0f}",
            delta_color="normal" if remaining >= 0 else "inverse",
            help="Amount remaining before exceeding total budget"
        )
    
    with col4:
        st.metric(
            label="📈 Used",
            value=f"{overall_percentage:.1f}%",
            delta=f"{overall_percentage:.1f}%",
            delta_color="inverse",
            help="Percentage of total budget used"
        )
    
    # Overall progress bar
    st.markdown("##### Overall Budget Progress")
    overall_alert = get_alert_level(overall_percentage)
    overall_style = get_alert_style(overall_alert)
    
    progress_col1, progress_col2 = st.columns([4, 1])
    with progress_col1:
        st.progress(min(overall_percentage / 100, 1.0))
    with progress_col2:
        st.markdown(f"**{overall_style['icon']} {overall_percentage:.1f}%**")
    
    # Show overall alert if needed
    if overall_percentage >= 100:
        st.error(f"🚨 **TOTAL BUDGET EXCEEDED!** You've spent ₹{abs(remaining):,.0f} more than your total monthly budget!")
    elif overall_percentage >= 90:
        st.warning(f"⚠️ **CRITICAL ALERT!** You've used {overall_percentage:.1f}% of your total budget. Only ₹{remaining:,.0f} remaining!")
    elif overall_percentage >= 75:
        st.info(f"📊 **WARNING:** You've used {overall_percentage:.1f}% of your total budget. ₹{remaining:,.0f} remaining.")
    
    # === SECTION 2: CATEGORY-WISE BUDGET ALERTS ===
    st.markdown("---")
    st.subheader("🎯 Category-Wise Budget Status")
    
    # Create tabs for different alert levels
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🚨 Exceeded", 
        "⚠️ Critical (90%+)", 
        "📊 Warning (75%+)", 
        "💡 On Track (50%+)", 
        "✅ Safe (<50%)"
    ])
    
    # Categorize budgets by alert level
    exceeded_budgets = []
    critical_budgets = []
    warning_budgets = []
    info_budgets = []
    safe_budgets = []
    
    for budget in budgets:
        category = budget['category']
        limit = budget['limit_amount']
        spent = get_category_spending(user_id, category, current_month)
        percentage = (spent / limit * 100) if limit > 0 else 0
        
        budget_data = {
            'category': category,
            'limit': limit,
            'spent': spent,
            'percentage': percentage,
            'remaining': limit - spent
        }
        
        alert_level = get_alert_level(percentage)
        if alert_level == "exceeded":
            exceeded_budgets.append(budget_data)
        elif alert_level == "critical":
            critical_budgets.append(budget_data)
        elif alert_level == "warning":
            warning_budgets.append(budget_data)
        elif alert_level == "info":
            info_budgets.append(budget_data)
        else:
            safe_budgets.append(budget_data)
    
    # Display budgets in tabs
    def display_budget_cards(budget_list, alert_level):
        """Display budget cards for given alert level"""
        if not budget_list:
            st.info(f"No budgets in this category 🎉")
            return
        
        for budget_data in budget_list:
            style = get_alert_style(alert_level)
            
            with st.container():
                # Create custom styled container
                st.markdown(f"""
                <div style="background-color: {style['bg']}; padding: 15px; border-radius: 10px; border-left: 5px solid {style['color']}; margin-bottom: 15px;">
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
                
                with col1:
                    st.markdown(f"### {style['icon']} {budget_data['category']}")
                
                with col2:
                    st.markdown(f"**Spent:** ₹{budget_data['spent']:,.0f}")
                    st.markdown(f"**Limit:** ₹{budget_data['limit']:,.0f}")
                
                with col3:
                    progress_value = min(budget_data['percentage'] / 100, 1.0)
                    st.progress(progress_value)
                    st.markdown(f"**{budget_data['percentage']:.1f}%**")
                
                with col4:
                    if budget_data['remaining'] >= 0:
                        st.success(f"✅ ₹{budget_data['remaining']:,.0f} left")
                    else:
                        st.error(f"❌ Over by ₹{abs(budget_data['remaining']):,.0f}")
                
                # Show detailed alert message
                if alert_level == "exceeded":
                    st.error(f"🚨 **EXCEEDED!** You've spent ₹{abs(budget_data['remaining']):,.0f} more than your {budget_data['category']} budget ({budget_data['percentage']:.1f}%)")
                elif alert_level == "critical":
                    st.warning(f"⚠️ **CRITICAL!** Only ₹{budget_data['remaining']:,.0f} left in {budget_data['category']} budget ({budget_data['percentage']:.1f}%)")
                elif alert_level == "warning":
                    st.info(f"📊 **WARNING:** You've used {budget_data['percentage']:.1f}% of your {budget_data['category']} budget. ₹{budget_data['remaining']:,.0f} remaining.")
                elif alert_level == "info":
                    st.info(f"💡 Halfway there: {budget_data['percentage']:.1f}% of {budget_data['category']} budget used.")
                
                st.markdown("</div>", unsafe_allow_html=True)
    
    with tab1:
        st.markdown("### 🚨 Budgets Exceeded (100%+)")
        display_budget_cards(exceeded_budgets, "exceeded")
    
    with tab2:
        st.markdown("### ⚠️ Critical Alert (90-100%)")
        display_budget_cards(critical_budgets, "critical")
    
    with tab3:
        st.markdown("### 📊 Warning (75-90%)")
        display_budget_cards(warning_budgets, "warning")
    
    with tab4:
        st.markdown("### 💡 On Track (50-75%)")
        display_budget_cards(info_budgets, "info")
    
    with tab5:
        st.markdown("### ✅ Safe (<50%)")
        display_budget_cards(safe_budgets, "normal")
    
    # === SECTION 3: VISUAL ANALYTICS ===
    st.markdown("---")
    st.subheader("📈 Budget Analytics")
    
    # Prepare data for visualizations
    budget_df = pd.DataFrame([
        {
            'Category': b['category'], 
            'Limit': b['limit'], 
            'Spent': get_category_spending(user_id, b['category'], current_month)
        }
        for b in budgets
    ])
    budget_df['Remaining'] = budget_df['Limit'] - budget_df['Spent']
    budget_df['Percentage'] = (budget_df['Spent'] / budget_df['Limit'] * 100).round(1)
    
    # Create visualizations
    viz_col1, viz_col2 = st.columns(2)
    
    with viz_col1:
        # Pie chart: Spending Distribution
        st.markdown("##### Spending Distribution by Category")
        fig1, ax1 = plt.subplots(figsize=(8, 6))
        colors = sns.color_palette("pastel")
        wedges, texts, autotexts = ax1.pie(
            budget_df['Spent'], 
            labels=budget_df['Category'],
            autopct='%1.1f%%',
            startangle=90,
            colors=colors
        )
        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        ax1.axis('equal')
        st.pyplot(fig1)
        plt.close()
    
    with viz_col2:
        # Bar chart: Budget vs Spent comparison
        st.markdown("##### Budget vs Actual Spending")
        fig2, ax2 = plt.subplots(figsize=(8, 6))
        x = range(len(budget_df))
        width = 0.35
        
        bars1 = ax2.bar(
            [i - width/2 for i in x], 
            budget_df['Limit'],
            width,
            label='Budget Limit',
            color='lightblue',
            edgecolor='navy',
            alpha=0.7
        )
        bars2 = ax2.bar(
            [i + width/2 for i in x], 
            budget_df['Spent'],
            width,
            label='Spent',
            color='salmon',
            edgecolor='darkred',
            alpha=0.7
        )
        
        ax2.set_xlabel('Category', fontweight='bold')
        ax2.set_ylabel('Amount (₹)', fontweight='bold')
        ax2.set_title('Budget vs Actual Spending', fontweight='bold', fontsize=14)
        ax2.set_xticks(x)
        ax2.set_xticklabels(budget_df['Category'], rotation=45, ha='right')
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close()
    
    # Additional chart: Progress bar chart
    st.markdown("---")
    st.markdown("##### Budget Usage Progress")
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    
    # Create horizontal bar chart
    categories = budget_df['Category']
    percentages = budget_df['Percentage']
    
    # Color bars based on alert level
    colors_list = []
    for pct in percentages:
        if pct >= 100:
            colors_list.append('#FF4444')  # Red - Exceeded
        elif pct >= 90:
            colors_list.append('#FF8800')  # Orange - Critical
        elif pct >= 75:
            colors_list.append('#FFA500')  # Yellow-orange - Warning
        elif pct >= 50:
            colors_list.append('#4169E1')  # Blue - Info
        else:
            colors_list.append('#00AA00')  # Green - Safe
    
    bars = ax3.barh(categories, percentages, color=colors_list, edgecolor='black', alpha=0.8)
    
    # Add percentage labels on bars
    for i, (bar, pct) in enumerate(zip(bars, percentages)):
        width = bar.get_width()
        label_x_pos = width if width < 95 else width - 5
        ax3.text(label_x_pos, bar.get_y() + bar.get_height()/2, 
                f'{pct:.1f}%',
                va='center', ha='right' if width >= 95 else 'left',
                fontweight='bold', color='white' if width >= 95 else 'black')
    
    # Add 100% reference line
    ax3.axvline(x=100, color='red', linestyle='--', linewidth=2, alpha=0.5, label='Budget Limit')
    
    ax3.set_xlabel('Percentage Used (%)', fontweight='bold')
    ax3.set_ylabel('Category', fontweight='bold')
    ax3.set_title('Budget Usage by Category', fontweight='bold', fontsize=14)
    ax3.set_xlim(0, max(110, max(percentages) + 10))
    ax3.legend()
    ax3.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig3)
    plt.close()
    
    # === SECTION 4: DETAILED TABLE ===
    st.markdown("---")
    st.subheader("📋 Detailed Budget Report")
    
    detailed_df = pd.DataFrame([
        {
            'Category': b['category'],
            'Budget Limit': f"₹{b['limit']:,.0f}",
            'Spent': f"₹{get_category_spending(user_id, b['category'], current_month):,.0f}",
            'Remaining': f"₹{(b['limit'] - get_category_spending(user_id, b['category'], current_month)):,.0f}",
            'Used %': f"{(get_category_spending(user_id, b['category'], current_month) / b['limit'] * 100):.1f}%",
            'Status': get_alert_level((get_category_spending(user_id, b['category'], current_month) / b['limit'] * 100)).upper()
        }
        for b in budgets
    ])
    
    st.dataframe(
        detailed_df,
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("💡 **No budgets set yet!** Create your first budget below to start tracking your spending limits.")

# === SECTION 5: ADD/EDIT BUDGET ===
st.markdown("---")
st.subheader("➕ Set Budget Limit")

with st.form("add_budget_form", clear_on_submit=True):
    st.markdown("##### Budget Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        category = st.selectbox(
            "Category*", 
            ["Food", "Transportation", "Entertainment", "Shopping", 
             "Healthcare", "Education", "Bills & Utilities", "Rent", 
             "Insurance", "Personal Care", "Other"],
            help="Choose a category to set spending limit"
        )
    
    with col2:
        limit_amount = st.number_input(
            "Monthly Budget Limit (₹)*", 
            min_value=0.0, 
            value=5000.0, 
            step=500.0,
            help="Maximum amount you want to spend in this category per month"
        )
    
    # Alert preferences
    st.markdown("##### Alert Preferences")
    st.caption("Choose when you want to receive budget alerts")
    
    col3, col4, col5 = st.columns(3)
    with col3:
        alert_50 = st.checkbox("Alert at 50% spent", value=True, 
                               help="Get notified when you've used half your budget")
    with col4:
        alert_75 = st.checkbox("Alert at 75% spent", value=True,
                               help="Warning when you're nearing your limit")
    with col5:
        alert_90 = st.checkbox("Alert at 90% spent", value=True,
                               help="Critical alert before exceeding budget")
    
    # Additional settings
    st.markdown("##### Additional Settings")
    notes = st.text_area("Notes (optional)", 
                        placeholder="e.g., Includes dining out and groceries",
                        help="Add any notes about this budget category")
    
    submit_budget = st.form_submit_button("💾 Save Budget Limit", use_container_width=True, type="primary")
    
    if submit_budget:
        if limit_amount <= 0:
            st.error("❌ Budget limit must be greater than 0")
        else:
            # Check if budget exists for this category
            existing = [b for b in budgets if b['category'] == category]
            if existing:
                # Update existing budget
                if update_budget(user_id, category, limit_amount, alert_50, alert_75, alert_90, notes):
                    st.success(f"✅ Budget limit for **{category}** updated to **₹{limit_amount:,.0f}**!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Error updating budget limit")
            else:
                # Add new budget
                if add_budget_to_db(user_id, category, limit_amount, alert_50, alert_75, alert_90, notes):
                    st.success(f"✅ Budget limit set for **{category}**: **₹{limit_amount:,.0f}**!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Error setting budget limit")

# === SECTION 6: MANAGE BUDGETS ===
if budgets:
    st.markdown("---")
    st.subheader("🗂️ Manage Budgets")
    
    # Delete budget
    st.markdown("##### Delete Budget")
    delete_col1, delete_col2 = st.columns([3, 1])
    
    with delete_col1:
        delete_category = st.selectbox(
            "Select budget to delete", 
            [b['category'] for b in budgets],
            help="Choose which budget limit you want to remove"
        )
    
    with delete_col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        if st.button("🗑️ Delete", type="secondary", use_container_width=True):
            if delete_budget(user_id, delete_category):
                st.success(f"✅ Budget for **{delete_category}** deleted!")
                st.rerun()
            else:
                st.error("❌ Error deleting budget")

# === SECTION 7: TIPS & INSIGHTS ===
st.markdown("---")
with st.expander("💡 Budget Management Tips", expanded=False):
    st.markdown("""
    ### Smart Budgeting Strategies:
    
    **Setting Budgets:**
    - Follow the 50/30/20 rule: 50% needs, 30% wants, 20% savings
    - Set realistic limits based on past 3 months average
    - Leave 10-15% buffer for unexpected expenses
    
    **Staying on Track:**
    - Review budgets weekly
    - Adjust limits seasonally (festivals, holidays)
    - Use cash for categories you overspend
    
    **Alert Thresholds:**
    - **50% Alert**: Midpoint check - pace yourself
    - **75% Alert**: Slow down spending in this category
    - **90% Alert**: Stop spending unless essential
    - **100% Alert**: Budget exceeded - review immediately
    
    **Pro Tips:**
    - Set separate budgets for "Fixed" vs "Variable" expenses
    - Create "Emergency" category with strict limit
    - Track daily for better control
    - Celebrate when you stay under budget! 🎉
    """)

# Footer
st.markdown("---")
st.caption("💰 Budget Manager | BudgetBuddy | Budgets reset monthly")
st.caption("🔔 Alerts shown at 50%, 75%, 90%, and 100% of budget limits")
