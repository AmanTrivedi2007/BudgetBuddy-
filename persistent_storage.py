import os

def get_db_path():
    """Safe DB path - no errors"""
    try:
        # Cloud first
        if os.path.exists('/mnt') or os.getenv('STREAMLIT_CLOUD_APP'):
            return "/mnt/data/budgetbuddy.db"
        # Local fallback
        return "budgetbuddy.db"
    except:
        return "budgetbuddy.db"  # Ultimate fallback
