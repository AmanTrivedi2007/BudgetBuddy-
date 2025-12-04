import os

def ensure_persistent_db():
    """Return persistent DB path for Streamlit Cloud or local"""
    if os.getenv('STREAMLIT_CLOUD') != 'true':
        return "budgetbuddy.db"
    
    persistent_db = "/mnt/data/budgetbuddy.db"
    
    # If DB already exists in persistent storage, use that
    if os.path.exists(persistent_db):
        return persistent_db
    
    # Else, use default - first run will create new DB
    return persistent_db

def get_db_path():
    return ensure_persistent_db()
