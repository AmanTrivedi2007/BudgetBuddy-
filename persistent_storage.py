import os

def get_db_path():
    """Streamlit Cloud persistent storage + Local fallback"""
    
    # Streamlit Cloud detection (multiple methods)
    is_cloud = (
        os.getenv('STREAMLIT_CLOUD_APP') or
        os.getenv('STREAMLIT_CLOUD') == 'true' or
        os.path.exists('/mnt') or
        os.path.exists('/mnt/data')
    )
    
    if is_cloud:
        db_path = "/mnt/data/budgetbuddy.db"
        # Auto-create directory if missing
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        print(f"🔄 Using Cloud persistent DB: {db_path}")
        return db_path
    
    # Local development
    db_path = "budgetbuddy.db"
    print(f"🔄 Using local DB: {db_path}")
    return db_path
