# categories.py - Shared Categories for BudgetBuddy

"""
Comprehensive yet concise expense categories covering all essential spending areas.
These categories are used across Expense Tracking, Budget Manager, and Recurring Transactions.
"""

# ===== EXPENSE CATEGORIES (18 categories) =====
EXPENSE_CATEGORIES = [
    # FOOD (2 categories)
    "🍔 Food & Dining",
    "🛒 Groceries",
    
    # HOUSING (2 categories)
    "🏠 Rent & Housing",
    "💡 Utilities",
    
    # TRANSPORTATION (2 categories)
    "🚗 Transportation",
    "⛽ Fuel",
    
    # SHOPPING (2 categories)
    "🛍️ Shopping",
    "👕 Clothing",
    
    # ENTERTAINMENT & LIFESTYLE (3 categories)
    "🎬 Entertainment",
    "🏋️ Gym & Sports",
    "✈️ Travel",
    
    # HEALTH & PERSONAL (2 categories)
    "💊 Healthcare",
    "💇 Personal Care",
    
    # BILLS & TECH (2 categories)
    "📞 Mobile & Internet",
    "📺 Subscriptions",
    
    # FINANCIAL (2 categories)
    "💰 EMI & Loans",
    "🏦 Insurance",
    
    # MISC (1 category)
    "📝 Other"
]

# ===== INCOME CATEGORIES (8 categories) =====
INCOME_CATEGORIES = [
    "💼 Salary",
    "💰 Freelance",
    "🏢 Business Income",
    "💹 Investment Returns",
    "🏠 Rental Income",
    "🎁 Gifts & Bonus",
    "💸 Refunds",
    "📝 Other"
]

# ===== CATEGORY DESCRIPTIONS (Optional - for tooltips) =====
CATEGORY_DESCRIPTIONS = {
    "🍔 Food & Dining": "Restaurants, cafes, food delivery",
    "🛒 Groceries": "Supermarket, fruits, vegetables, household items",
    "🏠 Rent & Housing": "Monthly rent, mortgage, property tax",
    "💡 Utilities": "Electricity, water, gas, maintenance",
    "🚗 Transportation": "Public transport, taxi, auto, parking",
    "⛽ Fuel": "Petrol, diesel, vehicle fuel",
    "🛍️ Shopping": "General shopping, electronics, gifts",
    "👕 Clothing": "Clothes, shoes, accessories",
    "🎬 Entertainment": "Movies, concerts, events, hobbies",
    "🏋️ Gym & Sports": "Gym membership, sports equipment, fitness",
    "✈️ Travel": "Vacation, trips, hotels, flights",
    "💊 Healthcare": "Doctor, hospital, medicines, medical tests",
    "💇 Personal Care": "Salon, grooming, beauty products",
    "📞 Mobile & Internet": "Phone bills, internet, broadband",
    "📺 Subscriptions": "Netflix, Spotify, apps, magazines",
    "💰 EMI & Loans": "Loan repayments, credit card bills",
    "🏦 Insurance": "Health, life, vehicle insurance",
    "📝 Other": "Miscellaneous expenses"
}
