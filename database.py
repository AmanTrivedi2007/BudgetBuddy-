# database.py
import sqlite3
import pandas as pd
from datetime import datetime
import os
import hashlib

# Database file name
DB_FILE = "budgetbuddy.db"

def init_database():
    """Initialize database - auto-deletes old database without user_id"""
    
    # Delete old database if it doesn't have user_id column
    if os.path.exists(DB_FILE):
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(income)")
            columns = [col[1] for col in cursor.fetchall()]
            conn.close()
            
            if 'user_id' not in columns:
                os.remove(DB_FILE)
        except:
            pass
    
    # Create tables
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create income table WITH user_id
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            source TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create expenses table WITH user_id
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create goals table WITH user_id
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            target_amount REAL NOT NULL,
            saved_amount REAL DEFAULT 0,
            description TEXT,
            created_date TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, name)
        )
    ''')
    
    # Create goal transactions table WITH user_id
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goal_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            goal_name TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            note TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # NEW: Login attempts table (persistent across reboots)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_attempts (
            username_hash TEXT PRIMARY KEY,
            attempts INTEGER DEFAULT 0,
            last_attempt_time REAL,
            locked_until REAL
        )
    ''')
    
    conn.commit()
    conn.close()

# ===== INCOME FUNCTIONS =====
def add_income_to_db(user_id, source, amount, date, notes=""):
    """Add income record to database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO income (user_id, source, amount, date, notes)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, source, amount, str(date), notes))
    conn.commit()
    conn.close()

def get_all_income(user_id):
    """Get all income records for specific user"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, source, amount, date, notes FROM income WHERE user_id = ? ORDER BY date DESC', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    income_list = []
    for row in rows:
        income_list.append({
            'id': row[0],
            'source': row[1],
            'amount': row[2],
            'date': row[3],
            'notes': row[4]
        })
    return income_list

def delete_income_from_db(user_id, income_id):
    """Delete income record from database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM income WHERE id = ? AND user_id = ?', (income_id, user_id))
    conn.commit()
    conn.close()

# ===== EXPENSE FUNCTIONS =====
def add_expense_to_db(user_id, category, amount, date, description=""):
    """Add expense record to database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO expenses (user_id, category, amount, date, description)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, category, amount, str(date), description))
    conn.commit()
    conn.close()

def get_all_expenses(user_id):
    """Get all expense records for specific user"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, category, amount, date, description FROM expenses WHERE user_id = ? ORDER BY date DESC', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    expense_list = []
    for row in rows:
        expense_list.append({
            'id': row[0],
            'category': row[1],
            'amount': row[2],
            'date': row[3],
            'description': row[4]
        })
    return expense_list

def delete_expense_from_db(user_id, expense_id):
    """Delete expense record from database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM expenses WHERE id = ? AND user_id = ?', (expense_id, user_id))
    conn.commit()
    conn.close()

# ===== GOAL FUNCTIONS =====
def add_goal_to_db(user_id, name, target_amount, description=""):
    """Add new goal to database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO goals (user_id, name, target_amount, saved_amount, description, created_date)
            VALUES (?, ?, ?, 0, ?, ?)
        ''', (user_id, name, target_amount, description, str(datetime.now().date())))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def get_all_goals(user_id):
    """Get all goals for specific user"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT name, target_amount, saved_amount, description, created_date 
        FROM goals WHERE user_id = ?
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    goals_list = []
    for row in rows:
        goal = {
            'name': row[0],
            'target_amount': row[1],
            'saved_amount': row[2],
            'description': row[3],
            'created_date': row[4],
            'transactions': get_goal_transactions(user_id, row[0])
        }
        goals_list.append(goal)
    return goals_list

def add_money_to_goal(user_id, goal_name, amount, note=""):
    """Add money to a specific goal"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE goals SET saved_amount = saved_amount + ?
        WHERE name = ? AND user_id = ?
    ''', (amount, goal_name, user_id))
    
    cursor.execute('''
        INSERT INTO goal_transactions (user_id, goal_name, amount, date, note)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, goal_name, amount, str(datetime.now().date()), note))
    
    conn.commit()
    conn.close()

def withdraw_from_goal(user_id, goal_name, amount, note=""):
    """Withdraw money from a specific goal"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE goals SET saved_amount = saved_amount - ?
        WHERE name = ? AND user_id = ?
    ''', (amount, goal_name, user_id))
    
    cursor.execute('''
        INSERT INTO goal_transactions (user_id, goal_name, amount, date, note)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, goal_name, -amount, str(datetime.now().date()), note))
    
    conn.commit()
    conn.close()

def get_goal_transactions(user_id, goal_name):
    """Get all transactions for a specific goal"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT amount, date, note FROM goal_transactions
        WHERE goal_name = ? AND user_id = ?
        ORDER BY date DESC
    ''', (goal_name, user_id))
    rows = cursor.fetchall()
    conn.close()
    
    transactions = []
    for row in rows:
        transactions.append({
            'amount': row[0],
            'date': row[1],
            'note': row[2]
        })
    return transactions

def delete_goal_from_db(user_id, goal_name):
    """Delete goal and all its transactions"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM goal_transactions WHERE goal_name = ? AND user_id = ?', (goal_name, user_id))
    cursor.execute('DELETE FROM goals WHERE name = ? AND user_id = ?', (goal_name, user_id))
    
    conn.commit()
    conn.close()

# ===== LOGIN ATTEMPTS FUNCTIONS (NEW) =====
def get_login_attempts(username):
    """Get login attempts from database"""
    username_hash = hashlib.sha256(username.lower().encode()).hexdigest()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT attempts, last_attempt_time, locked_until FROM login_attempts WHERE username_hash = ?', (username_hash,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {'attempts': result[0], 'last_attempt_time': result[1], 'locked_until': result[2]}
    return None

def update_login_attempts(username, attempts, locked_until=None):
    """Update login attempts in database"""
    import time
    username_hash = hashlib.sha256(username.lower().encode()).hexdigest()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO login_attempts (username_hash, attempts, last_attempt_time, locked_until)
        VALUES (?, ?, ?, ?)
    ''', (username_hash, attempts, time.time(), locked_until))
    
    conn.commit()
    conn.close()

def reset_login_attempts(username):
    """Reset login attempts for user"""
    username_hash = hashlib.sha256(username.lower().encode()).hexdigest()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM login_attempts WHERE username_hash = ?', (username_hash,))
    conn.commit()
    conn.close()
