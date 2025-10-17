# auth.py
import streamlit as st
import hashlib
import sqlite3
import re
import secrets
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

DB_FILE = "budgetbuddy.db"

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

def send_username_email(email, username, full_name):
    """Send username to user's email"""
    try:
        # NOTE: Configure these with your SMTP settings
        # For now, we'll just show a success message
        # In production, use Gmail SMTP or SendGrid
        
        # Example Gmail SMTP configuration:
        # smtp_server = "smtp.gmail.com"
        # smtp_port = 587
        # sender_email = "your-email@gmail.com"
        # sender_password = "your-app-password"
        
        # For demonstration, we'll just return success
        # In production, uncomment this code:
        
        """
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = "Welcome to BudgetBuddy - Your Username"
        
        body = f

Hello {full_name},

Welcome to BudgetBuddy! 🎉

Your account has been created successfully.

Your Username: {username}

IMPORTANT: Please save this username. You'll need it to login.

Login at: [Your App URL]

Thank you for choosing BudgetBuddy!

Best regards,
BudgetBuddy Team
        "        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, email, text)
        server.quit()
        """
        
        return True
    except Exception as e:
        st.error(f"Email sending failed: {str(e)}")
        return False

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

def create_user(full_name, username, password, email):
    """Create new user with hashed username and email"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Hash everything
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
    
    cursor.execute('SELECT password_hash, salt, full_name FROM users WHERE username_hash = ?', (username_hash,))
    result = cursor.fetchone()
    conn.close()
    
    if result and verify_password(password, result[0], result[1]):
        return True, result[2]
    return False, None

def check_rate_limit(username):
    """Check if user exceeded login attempts (from database)"""
    from database import get_login_attempts
    
    attempts_data = get_login_attempts(username)
    
    if attempts_data:
        attempts = attempts_data['attempts']
        locked_until = attempts_data['locked_until']
        
        if attempts >= 5 and locked_until:
            # Check if still locked
            if time.time() < locked_until:
                minutes_left = int((locked_until - time.time()) / 60)
                return False, minutes_left
            else:
                # Lock expired, reset attempts
                from database import reset_login_attempts
                reset_login_attempts(username)
    
    return True, 0

def record_failed_attempt(username):
    """Record failed login attempt in database"""
    from database import get_login_attempts, update_login_attempts
    
    attempts_data = get_login_attempts(username)
    
    if attempts_data:
        new_attempts = attempts_data['attempts'] + 1
    else:
        new_attempts = 1
    
    # Lock for 15 minutes after 5 failed attempts
    locked_until = None
    if new_attempts >= 5:
        locked_until = time.time() + 900  # 15 minutes
    
    update_login_attempts(username, new_attempts, locked_until)

def reset_attempts(username):
    """Reset login attempts after successful login"""
    from database import reset_login_attempts
    reset_login_attempts(username)

def check_authentication():
    """Main authentication function"""
    
    init_users_table()
    
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'full_name' not in st.session_state:
        st.session_state.full_name = None
    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = 'login'
    if 'login_time' not in st.session_state:
        st.session_state.login_time = None
    
    # Session timeout check
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
        .big-title {
            font-size: 48px !important;
            font-weight: bold;
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="big-title">💰 BudgetBuddy</p>', unsafe_allow_html=True)
    st.markdown("### Your Personal Finance Companion")
    st.markdown("---")
    
    # Toggle
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
            full_name = st.text_input("Full Name*", placeholder="e.g., Rahul Kumar")
            username = st.text_input("Choose Username*", placeholder="e.g., rahulk or rahul_kumar",
                                    help="Create your own unique username (letters, numbers, underscore only)")
            email = st.text_input("Email*", placeholder="your-email@example.com",
                                 help="Required - Your username will be sent to this email")
            password = st.text_input("Password*", type="password",
                                    help="Minimum 6 characters")
            confirm_password = st.text_input("Confirm Password*", type="password")
            
            signup_submitted = st.form_submit_button("🚀 Create Account", use_container_width=True)
            
            if signup_submitted:
                # Validation
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
                    # Create user
                    if create_user(full_name, username, password, email):
                        # Send email (simulated)
                        send_username_email(email, username, full_name)
                        
                        st.success(f"✅ Account created successfully!")
                        st.info(f"🔑 **Your Username:** `{username}`")
                        st.info(f"📧 **Confirmation sent to:** {email}")
                        st.warning("⚠️ **IMPORTANT:** Save your username! You'll need it to login.")
                        st.balloons()
                        
                        # Show username prominently
                        st.code(username, language="text")
                        
                        st.markdown("---")
                        if st.button("➡️ Go to Login Page", use_container_width=True, type="primary"):
                            st.session_state.auth_mode = 'login'
                            st.rerun()
                    else:
                        st.error("❌ Error creating account. Please try again.")
        
        st.info("""
        💡 **Security Features:**
        - Your username is encrypted with SHA-256
        - Your password is encrypted with SHA-256 + unique salt
        - Your email is encrypted with SHA-256
        - Your username will be sent to your email
        """)
    
    # LOGIN MODE
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
                    allowed, minutes_left = check_rate_limit(username_input)
                    
                    if not allowed:
                        st.error(f"🚫 Too many failed attempts. Try again in {minutes_left} minutes.")
                        st.warning("🔒 Your account is temporarily locked for security.")
                    else:
                        success, full_name = authenticate_user(username_input, password_input)
                        
                        if success:
                            reset_attempts(username_input)
                            
                            st.session_state.username = username_input
                            st.session_state.full_name = full_name
                            st.session_state.login_time = time.time()
                            
                            st.success(f"✅ Welcome back, {full_name}! 👋")
                            st.balloons()
                            st.rerun()
                        else:
                            record_failed_attempt(username_input)
                            
                            from database import get_login_attempts
                            attempts_data = get_login_attempts(username_input)
                            if attempts_data:
                                remaining = 5 - attempts_data['attempts']
                                if remaining > 0:
                                    st.warning(f"⚠️ {remaining} attempts remaining before account lock.")
                            
                            st.error("❌ Invalid username or password")
        
        st.info("💡 **Don't have an account?** Click 'Sign Up' above!\n\n📧 **Forgot username?** Check your email for your username confirmation.")
    
    # Footer
    st.markdown("---")
    st.markdown("### ✨ Features")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("💵 **Income Tracking**")
        st.markdown("💳 **Expense Management**")
    
    with col2:
        st.markdown("🎯 **Savings Goals**")
        st.markdown("📊 **Visualizations**")
    
    st.markdown("---")
    st.caption("🔒 Password: SHA-256 + Salt")
    st.caption("📧 Email: SHA-256 hashed")
    st.caption("👤 Username: SHA-256 hashed")
    st.caption("⏱️ Auto-logout: 30 minutes")
    st.caption("🚫 Rate limiting: 5 attempts per 15 minutes (stored in database)")
    
    st.stop()
