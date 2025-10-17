# auth.py
import streamlit as st
import hashlib
import sqlite3
import re
import secrets

DB_FILE = "budgetbuddy.db"

def init_users_table():
    """Create users table if it doesn't exist"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            email TEXT UNIQUE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def generate_unique_username(full_name):
    """Generate a unique username from full name"""
    # Clean name: remove special chars, convert to lowercase
    clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', full_name).lower()
    parts = clean_name.split()
    
    if not parts:
        base_username = "user"
    elif len(parts) == 1:
        base_username = parts[0]
    else:
        # First name + first letter of last name
        base_username = parts[0] + parts[-1][0]
    
    # Check if username exists, add number if needed
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    username = base_username
    counter = 1
    
    while True:
        cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
        if cursor.fetchone() is None:
            break
        username = f"{base_username}{counter}"
        counter += 1
    
    conn.close()
    return username

def hash_password(password, salt=None):
    """Hash password using SHA-256 with salt"""
    if salt is None:
        # Generate random salt (16 bytes = 32 hex characters)
        salt = secrets.token_hex(16)
    
    # Combine password and salt, then hash
    password_salt = password + salt
    password_hash = hashlib.sha256(password_salt.encode('utf-8')).hexdigest()
    
    return password_hash, salt

def verify_password(password, stored_hash, salt):
    """Verify password against stored hash and salt"""
    password_hash, _ = hash_password(password, salt)
    return password_hash == stored_hash

def create_user(full_name, username, password, email=None):
    """Create new user in database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Hash password with random salt
        password_hash, salt = hash_password(password)
        
        cursor.execute('''
            INSERT INTO users (full_name, username, password_hash, salt, email)
            VALUES (?, ?, ?, ?, ?)
        ''', (full_name, username, password_hash, salt, email))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def authenticate_user(username, password):
    """Authenticate user with username and password"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT password_hash, salt, full_name FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result and verify_password(password, result[0], result[1]):
        return True, result[2]  # Return success and full name
    return False, None

def check_authentication():
    """Main authentication function with sign up and login"""
    
    # Initialize users table
    init_users_table()
    
    # Initialize session state
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'full_name' not in st.session_state:
        st.session_state.full_name = None
    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = 'login'
    
    # If already logged in, return username
    if st.session_state.username:
        return st.session_state.username
    
    # Show login/signup page with beautiful styling
    st.markdown("""
        <style>
        .auth-container {
            max-width: 500px;
            margin: 50px auto;
            padding: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .big-title {
            font-size: 48px !important;
            font-weight: bold;
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .stButton>button {
            border-radius: 10px !important;
            font-weight: bold !important;
            transition: all 0.3s !important;
        }
        .stButton>button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2) !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="big-title">💰 BudgetBuddy</p>', unsafe_allow_html=True)
    st.markdown("### Your Personal Finance Companion")
    st.markdown("---")
    
    # Toggle between Login and Sign Up
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔐 Login", use_container_width=True, 
                    type="primary" if st.session_state.auth_mode == 'login' else "secondary"):
            st.session_state.auth_mode = 'login'
            st.rerun()
    with col2:
        if st.button("✍️ Sign Up", use_container_width=True,
                    type="primary" if st.session_state.auth_mode == 'signup' else "secondary"):
            st.session_state.auth_mode = 'signup'
            st.rerun()
    
    st.markdown("---")
    
    # SIGN UP MODE
    if st.session_state.auth_mode == 'signup':
        st.subheader("✍️ Create New Account")
        
        with st.form("signup_form", clear_on_submit=True):
            full_name = st.text_input("Full Name*", placeholder="e.g., Rahul Kumar",
                                      help="Enter your complete name")
            email = st.text_input("Email (optional)", placeholder="rahul@example.com",
                                 help="For future account recovery features")
            password = st.text_input("Password*", type="password",
                                    help="Minimum 6 characters - Choose a strong password")
            confirm_password = st.text_input("Confirm Password*", type="password",
                                           help="Re-enter your password")
            
            signup_submitted = st.form_submit_button("🚀 Create Account", use_container_width=True)
            
            if signup_submitted:
                # Validation
                if not full_name or len(full_name.strip()) < 2:
                    st.error("❌ Please enter your full name (minimum 2 characters)")
                elif len(password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                elif password != confirm_password:
                    st.error("❌ Passwords don't match")
                elif email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                    st.error("❌ Invalid email format")
                else:
                    # Generate unique username
                    generated_username = generate_unique_username(full_name)
                    
                    # Create user
                    if create_user(full_name, generated_username, password, email):
                        st.success(f"✅ Account created successfully!")
                        st.info(f"🔑 **Your Username:** `{generated_username}`")
                        st.warning("⚠️ **IMPORTANT:** Save this username! You'll need it to login.")
                        st.balloons()
                        
                        # Show copy button for username
                        st.code(generated_username, language="text")
                        
                        st.markdown("---")
                        if st.button("➡️ Go to Login Page", use_container_width=True, type="primary"):
                            st.session_state.auth_mode = 'login'
                            st.rerun()
                    else:
                        st.error("❌ Error creating account. Please try a different name.")
        
        st.info("""
        💡 **How Username Generation Works:**
        - "Rahul Kumar" → username: `rahulk`
        - "Priya" → username: `priya`
        - If username exists, adds number: `rahulk1`, `rahulk2`
        """)
    
    # LOGIN MODE
    else:
        st.subheader("🔐 Login to Your Account")
        
        with st.form("login_form", clear_on_submit=False):
            username_input = st.text_input("Username*", placeholder="Enter your username",
                                          help="The username generated during signup")
            password_input = st.text_input("Password*", type="password",
                                          help="Your account password")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                login_submitted = st.form_submit_button("🚪 Login", use_container_width=True)
            
            if login_submitted:
                if not username_input or not password_input:
                    st.error("❌ Please enter both username and password")
                else:
                    # Authenticate
                    success, full_name = authenticate_user(username_input, password_input)
                    
                    if success:
                        st.session_state.username = username_input
                        st.session_state.full_name = full_name
                        st.success(f"✅ Welcome back, {full_name}! 👋")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                        st.warning("💡 Make sure you're using the correct username and password")
        
        st.info("💡 **Don't have an account?** Click 'Sign Up' above to create one!")
    
    # Footer
    st.markdown("---")
    st.markdown("### ✨ Features")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("💵 **Income Tracking**")
        st.caption("Monitor all income sources")
        st.markdown("💳 **Expense Management**")
        st.caption("Track daily spending")
    
    with col2:
        st.markdown("🎯 **Savings Goals**")
        st.caption("Set and achieve targets")
        st.markdown("📊 **Visualizations**")
        st.caption("Analyze spending patterns")
    
    st.markdown("---")
    st.caption("🔒 Your password is encrypted with SHA-256 + Salt")
    st.caption("🛡️ Each user has isolated, private data")
    
    # Stop here until logged in
    st.stop()
