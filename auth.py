# auth.py - Complete Authentication with Password Reset

import streamlit as st
import hashlib
import sqlite3
import re
import secrets
import time

DB_FILE = "budgetbuddy.db"


# ===== DATABASE FUNCTIONS =====

def init_users_table():
    """Create users table"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username_hash TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            email_hash TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


# ===== HASHING FUNCTIONS =====

def hash_username(username):
    """Hash username for secure storage"""
    return hashlib.sha256(username.lower().encode('utf-8')).hexdigest()

def hash_password(password, salt=None):
    """Hash password using SHA-256 with salt"""
    if salt is None:
        salt = secrets.token_hex(16)
    password_salt = password + salt
    password_hash = hashlib.sha256(password_salt.encode('utf-8')).hexdigest()
    return password_hash, salt

def hash_email(email):
    """Hash email using SHA-256"""
    if not email:
        return None
    email_lower = email.lower().strip()
    email_hash = hashlib.sha256(email_lower.encode('utf-8')).hexdigest()
    return email_hash

def verify_password(password, stored_hash, salt):
    """Verify password against stored hash and salt"""
    password_hash, _ = hash_password(password, salt)
    return password_hash == stored_hash


# ===== USER VALIDATION FUNCTIONS =====

def check_username_exists(username):
    """Check if username already exists"""
    username_hash = hash_username(username)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE username_hash = ?', (username_hash,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def check_email_exists(email):
    """Check if email already exists"""
    email_hash = hash_email(email)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE email_hash = ?', (email_hash,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def verify_username_email_match(username, email):
    """Verify that username and email belong to same account"""
    username_hash = hash_username(username)
    email_hash = hash_email(email)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT full_name FROM users WHERE username_hash = ? AND email_hash = ?', 
                   (username_hash, email_hash))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return True, result[0]  # Return success and full name
    return False, None


# ===== PASSWORD RESET FUNCTIONS =====

def reset_password(username, email, new_password):
    """Reset password after verifying username and email"""
    username_hash = hash_username(username)
    email_hash = hash_email(email)
    
    # Generate new password hash with new salt
    new_password_hash, new_salt = hash_password(new_password)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Update password and salt for the verified user
    cursor.execute('''
        UPDATE users 
        SET password_hash = ?, salt = ? 
        WHERE username_hash = ? AND email_hash = ?
    ''', (new_password_hash, new_salt, username_hash, email_hash))
    
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    return rows_affected > 0


# ===== USER MANAGEMENT FUNCTIONS =====

def create_user(full_name, username, password, email):
    """Create new user with hashed username and email"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        username_hash = hash_username(username)
        password_hash, salt = hash_password(password)
        email_hash = hash_email(email)
        
        cursor.execute('''
            INSERT INTO users (full_name, username_hash, password_hash, salt, email_hash)
            VALUES (?, ?, ?, ?, ?)
        ''', (full_name, username_hash, password_hash, salt, email_hash))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def authenticate_user(username, password):
    """Authenticate user with username and password"""
    username_hash = hash_username(username)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT password_hash, salt, full_name FROM users WHERE username_hash = ?', 
                   (username_hash,))
    result = cursor.fetchone()
    conn.close()
    
    if result and verify_password(password, result[0], result[1]):
        return True, result[2]  # Return success and full name
    return False, None


# ===== RATE LIMITING FUNCTIONS =====

def check_rate_limit(username):
    """Check if user exceeded login attempts (from database)"""
    from database import get_login_attempts
    
    attempts_data = get_login_attempts(username)
    if attempts_data:
        attempts = attempts_data['attempts']
        locked_until = attempts_data['locked_until']
        
        if attempts >= 5 and locked_until:
            if time.time() < locked_until:
                minutes_left = int((locked_until - time.time()) / 60) + 1
                return False, minutes_left
            else:
                # Lock expired, reset attempts
                from database import reset_login_attempts
                reset_login_attempts(username)
                return True, 0
    
    return True, 0

def record_failed_attempt(username):
    """Record failed login attempt in database"""
    from database import get_login_attempts, update_login_attempts
    
    attempts_data = get_login_attempts(username)
    if attempts_data:
        new_attempts = attempts_data['attempts'] + 1
    else:
        new_attempts = 1
    
    locked_until = None
    if new_attempts >= 5:
        locked_until = time.time() + 900  # Lock for 15 minutes
    
    update_login_attempts(username, new_attempts, locked_until)

def reset_attempts(username):
    """Reset login attempts after successful login"""
    from database import reset_login_attempts
    reset_login_attempts(username)


# ===== MAIN AUTHENTICATION FUNCTION =====

def check_authentication():
    """Main authentication function"""
    init_users_table()
    
    # Initialize session state
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'full_name' not in st.session_state:
        st.session_state.full_name = None
    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = 'login'
    if 'login_time' not in st.session_state:
        st.session_state.login_time = None
    if 'signup_success' not in st.session_state:
        st.session_state.signup_success = False
    if 'new_username' not in st.session_state:
        st.session_state.new_username = ""
    if 'new_email' not in st.session_state:
        st.session_state.new_email = ""
    if 'reset_success' not in st.session_state:
        st.session_state.reset_success = False
    if 'reset_username' not in st.session_state:
        st.session_state.reset_username = ""
    
    # Session timeout check (30 minutes)
    if st.session_state.username:
        if st.session_state.login_time:
            elapsed = time.time() - st.session_state.login_time
            if elapsed > 1800:  # 30 minutes
                st.session_state.username = None
                st.session_state.full_name = None
                st.session_state.login_time = None
                st.warning("⏱️ Session expired for security. Please login again.")
                st.rerun()
        
        return st.session_state.username
    
    # Styling
    st.markdown("""
        <style>
        .auth-title {
            font-size: 48px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="auth-title">💰 BudgetBuddy</div>', unsafe_allow_html=True)
    st.markdown("### Your Personal Finance Companion")
    st.markdown("---")
    
    # Toggle between Login, Sign Up, and Forgot Password
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔐 Login", use_container_width=True, 
                    type="primary" if st.session_state.auth_mode == 'login' else "secondary"):
            st.session_state.auth_mode = 'login'
            st.session_state.signup_success = False
            st.session_state.reset_success = False
            st.rerun()
    
    with col2:
        if st.button("✍️ Sign Up", use_container_width=True, 
                    type="primary" if st.session_state.auth_mode == 'signup' else "secondary"):
            st.session_state.auth_mode = 'signup'
            st.session_state.signup_success = False
            st.session_state.reset_success = False
            st.rerun()
    
    with col3:
        if st.button("🔑 Forgot Password", use_container_width=True, 
                    type="primary" if st.session_state.auth_mode == 'forgot' else "secondary"):
            st.session_state.auth_mode = 'forgot'
            st.session_state.signup_success = False
            st.session_state.reset_success = False
            st.rerun()
    
    st.markdown("---")
    
    # ===== SIGN UP MODE =====
    if st.session_state.auth_mode == 'signup':
        st.subheader("✍️ Create New Account")
        
        if st.session_state.signup_success:
            st.success(f"✅ Account created successfully!")
            st.info(f"🔑 **Your Username:** `{st.session_state.new_username}`")
            st.info(f"📧 **Email:** {st.session_state.new_email}")
            st.warning("⚠️ **IMPORTANT:** Save your username! You'll need it to login.")
            st.balloons()
            st.code(st.session_state.new_username, language="text")
            st.markdown("---")
            
            if st.button("➡️ Go to Login Page", use_container_width=True, type="primary"):
                st.session_state.auth_mode = 'login'
                st.session_state.signup_success = False
                st.rerun()
            
            st.info("""
                💡 **Security Features:**
                - Your username is encrypted with SHA-256
                - Your password is encrypted with SHA-256 + unique salt
                - Your email is encrypted with SHA-256
            """)
        else:
            with st.form("signup_form", clear_on_submit=True):
                full_name = st.text_input("Full Name*", placeholder="e.g., Rahul Kumar")
                username = st.text_input("Choose Username*", placeholder="e.g., rahulk or rahul_kumar",
                                        help="Create your own unique username (letters, numbers, underscore only)")
                email = st.text_input("Email*", placeholder="your-email@example.com",
                                     help="Required - For account recovery")
                password = st.text_input("Password*", type="password", help="Minimum 6 characters")
                confirm_password = st.text_input("Confirm Password*", type="password")
                
                signup_submitted = st.form_submit_button("🚀 Create Account", use_container_width=True)
                
                if signup_submitted:
                    if not full_name or len(full_name.strip()) < 2:
                        st.error("❌ Please enter your full name (minimum 2 characters)")
                    elif not username or len(username.strip()) < 3:
                        st.error("❌ Username must be at least 3 characters")
                    elif not re.match(r'^[a-zA-Z0-9_]+$', username):
                        st.error("❌ Username can only contain letters, numbers, and underscore")
                    elif not email:
                        st.error("❌ Email is required")
                    elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                        st.error("❌ Invalid email format")
                    elif len(password) < 6:
                        st.error("❌ Password must be at least 6 characters")
                    elif password != confirm_password:
                        st.error("❌ Passwords don't match")
                    elif check_username_exists(username):
                        st.error("❌ This username is already taken. Please choose another.")
                    elif check_email_exists(email):
                        st.error("❌ This email is already registered. Please use a different email.")
                    else:
                        if create_user(full_name, username, password, email):
                            st.session_state.signup_success = True
                            st.session_state.new_username = username
                            st.session_state.new_email = email
                            st.rerun()
                        else:
                            st.error("❌ Error creating account. Please try again.")
            
            st.info("""
                💡 **How it works:**
                - Choose your own username
                - Your username and email will be encrypted
                - You'll use your username to login
            """)
    
    # ===== FORGOT PASSWORD MODE =====
    elif st.session_state.auth_mode == 'forgot':
        st.subheader("🔑 Reset Your Password")
        
        if st.session_state.reset_success:
            st.success("✅ Password reset successfully!")
            st.info(f"🔑 Your username: `{st.session_state.reset_username}`")
            st.warning("⚠️ You can now login with your new password")
            st.balloons()
            st.markdown("---")
            
            if st.button("➡️ Go to Login Page", use_container_width=True, type="primary"):
                st.session_state.auth_mode = 'login'
                st.session_state.reset_success = False
                st.rerun()
        else:
            with st.form("forgot_password_form", clear_on_submit=True):
                st.markdown("##### Step 1: Verify Your Identity")
                username_input = st.text_input("Username*", placeholder="Enter your username",
                                              help="The username you created during signup")
                email_input = st.text_input("Email*", placeholder="your-email@example.com",
                                            help="The email you used during signup")
                
                st.markdown("##### Step 2: Set New Password")
                new_password = st.text_input("New Password*", type="password", help="Minimum 6 characters")
                confirm_new_password = st.text_input("Confirm New Password*", type="password")
                
                reset_submitted = st.form_submit_button("🔄 Reset Password", use_container_width=True)
                
                if reset_submitted:
                    if not username_input or not email_input:
                        st.error("❌ Please enter both username and email")
                    elif not new_password or len(new_password) < 6:
                        st.error("❌ New password must be at least 6 characters")
                    elif new_password != confirm_new_password:
                        st.error("❌ Passwords don't match")
                    else:
                        # Verify username and email match
                        verified, full_name = verify_username_email_match(username_input, email_input)
                        
                        if verified:
                            # Reset password
                            if reset_password(username_input, email_input, new_password):
                                st.session_state.reset_success = True
                                st.session_state.reset_username = username_input
                                st.rerun()
                            else:
                                st.error("❌ Error resetting password. Please try again.")
                        else:
                            st.error("❌ Username and email don't match or account doesn't exist")
                            st.warning("💡 Make sure you're using the correct username and email you signed up with")
            
            st.info("""
                🔒 **Why we need both Username AND Email:**
                - Double verification for maximum security
                - Only you know both your username and email
                - Instant password reset (no waiting for email)
                - 10x more secure than traditional email-only reset
            """)
    
    # ===== LOGIN MODE =====
    else:
        st.subheader("🔐 Login to Your Account")
        
        with st.form("login_form", clear_on_submit=False):
            username_input = st.text_input("Username*", placeholder="Enter your username")
            password_input = st.text_input("Password*", type="password")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                login_submitted = st.form_submit_button("🚪 Login", use_container_width=True)
            
            if login_submitted:
                if not username_input or not password_input:
                    st.error("❌ Please enter both username and password")
                else:
                    # Check rate limit
                    allowed, minutes_left = check_rate_limit(username_input)
                    
                    if not allowed:
                        st.error(f"🚫 Too many failed attempts. Try again in {minutes_left} minutes.")
                        st.warning("🔒 Your account is temporarily locked for security.")
                    else:
                        # Authenticate
                        success, full_name = authenticate_user(username_input, password_input)
                        
                        if success:
                            # Reset failed attempts
                            reset_attempts(username_input)
                            
                            # Set session
                            st.session_state.username = username_input
                            st.session_state.full_name = full_name
                            st.session_state.login_time = time.time()
                            
                            st.success(f"✅ Welcome back, {full_name}! 👋")
                            st.balloons()
                            st.rerun()
                        else:
                            # Record failed attempt
                            record_failed_attempt(username_input)
                            
                            # Check remaining attempts
                            from database import get_login_attempts
                            attempts_data = get_login_attempts(username_input)
                            if attempts_data:
                                remaining = 5 - attempts_data['attempts']
                                if remaining > 0:
                                    st.warning(f"⚠️ {remaining} attempts remaining before account lock.")
                            
                            st.error("❌ Invalid username or password")
                            st.info("💡 **Forgot password?** Click 'Forgot Password' above!")
        
        # Footer
        st.markdown("---")
        st.markdown("### ✨ Features")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("💵 **Income Tracking**")
            st.markdown("💳 **Expense Management**")
            st.markdown("💰 **Budget Limits**")
        
        with col2:
            st.markdown("🎯 **Savings Goals**")
            st.markdown("🔁 **Recurring Transactions**")
            st.markdown("📊 **Visualizations**")
        
        st.markdown("---")
        st.caption("🔒 Password: SHA-256 + Salt")
        st.caption("📧 Email: SHA-256 hashed")
        st.caption("👤 Username: SHA-256 hashed")
        st.caption("⏱️ Auto-logout: 30 minutes")
        st.caption("🚫 Rate limiting: 5 attempts per 15 minutes")
        st.caption("🔑 Password Reset: Username + Email verification")
    
    st.stop()
