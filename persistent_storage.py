import os

def get_db_path():
    """Streamlit Cloud persistent storage + Local fallback"""
    is_cloud = (
        os.getenv('STREAMLIT_CLOUD_APP') or
        os.getenv('STREAMLIT_CLOUD') == 'true' or
        os.path.exists('/mount/src')
    )
    
    if is_cloud:
        db_path = "/mount/src/budgetbuddy.db"  # ✅ Correct Streamlit Cloud path
        print(f"🔄 Using Cloud persistent DB: {db_path}")
        return db_path
    
    # Local development
    db_path = "budgetbuddy.db"
    print(f"🔄 Using local DB: {db_path}")
    return db_path
