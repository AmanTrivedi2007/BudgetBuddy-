import os

def get_db_path():
    """Streamlit Cloud persistent storage - NO os.makedirs"""
    
    # Cloud detection
    is_cloud = (
        os.getenv('STREAMLIT_CLOUD_APP') or
        os.getenv('STREAMLIT_CLOUD') == 'true' or
        os.path.exists('/mnt')
    )
    
    if is_cloud:
        return "/mnt/data/budgetbuddy.db"  # NO os.makedirs!
    
    return "budgetbuddy.db"
