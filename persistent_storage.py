import os

def get_db_path():
    """Streamlit Cloud persistent storage + Local fallback"""
    
    # Streamlit Cloud detection (multiple methods)
    is_cloud = (
        os.getenv('STREAMLIT_CLOUD_APP') or
        os.getenv('STREAMLIT_CLOUD') == 'true' or
        os.path.exists('/mount/src') or  # ✅ Updated for actual Streamlit Cloud path
        os.path.exists('/mnt')
    )
    
    if is_cloud:
        db_path = "/mount/src/budgetbuddy.db"  # ✅ Fixed path - no subdirectories
        print(f"🔄 Using Cloud persistent DB: {db_path}")
        return db_path
    
    # Local development
    db_path = "budgetbuddy.db"
    print(f"🔄 Using local DB: {db_path}")
    return db_path
