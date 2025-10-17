# database.py - Complete Database with Budget, Recurring Transactions & All Original Features

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os
import hashlib
import calendar

# Database file name
DB_FILE = "budgetbuddy.db"

# ===== DATABASE INITIALIZATION =====

def init_database():
    """Initialize database - auto-migrates old schema to new"""
    # Check if database needs migration
    if os.path.exists(DB_FILE):
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Check if users table exists and has correct structure
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            users_table_exists = cursor.fetchone()
            
            if users_table_exists:
                # Check users table columns
                cursor.execute("PRAGMA table_info(users)")
                user_columns = [col[1] for col in cursor.fetchall()]
                
                # If old schema (has 'username' instead of 'username_hash'), delete database
                if 'username' in user_columns and 'username_hash' not in user_columns:
                    conn.close()
                    os.remove(DB_FILE)
                    print("✅ Old schema detected - recreating database")
                elif 'email_hash' not in user_columns:
                    # Missing email_hash column, recreate
                    conn.close()
                    os.remove(DB_FILE)
                    print("✅ Missing email_hash column - recreating database")
                else:
                    conn.close()
                    # Schema is correct, just ensure all tables exist
            else:
                # Users table doesn't exist, check income table
                cursor.execute("PRAGMA table_info(income)")
                income_columns = [col[1] for col in cursor.fetchall()]
                conn.close()
                if 'user_id' not in income_columns:
                    os.remove(DB_FILE)
                    print("✅ Old database format - recreating")
        except Exception as e:
            # Any error, just recreate
            try:
                os.remove(DB_FILE)
                print(f"✅ Database error - recreating: {e}")
            except:
                pass
    
    # Create all tables with correct schema
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create users table with hashed username and email
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
    
    # Create login attempts table (persistent)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_attempts (
            username_hash TEXT PRIMARY KEY,
            attempts INTEGER DEFAULT 0,
            last_attempt_time REAL,
            locked_until REAL
        )
    ''')
    
    # NEW: Create budgets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            category TEXT NOT NULL,
            limit_amount REAL NOT NULL,
            alert_50 BOOLEAN DEFAULT 1,
            alert_75 BOOLEAN DEFAULT 1,
            alert_90 BOOLEAN DEFAULT 1,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, category)
        )
    ''')
    
    # NEW: Create recurring transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recurring_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            frequency TEXT NOT NULL,
            start_date TEXT NOT NULL,
            next_date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")

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

# ===== LOGIN ATTEMPTS FUNCTIONS =====

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

# ===== BUDGET MANAGEMENT FUNCTIONS (NEW) =====

def get_all_budgets(user_id):
    """Get all budgets for specific user"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT category, limit_amount, alert_50, alert_75, alert_90, notes
        FROM budgets
        WHERE user_id = ?
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    budgets_list = []
    for row in rows:
        budgets_list.append({
            'category': row[0],
            'limit_amount': row[1],
            'alert_50': row[2],
            'alert_75': row[3],
            'alert_90': row[4],
            'notes': row[5]
        })
    return budgets_list

def add_budget_to_db(user_id, category, limit_amount, alert_50=True, alert_75=True, alert_90=True, notes=""):
    """Add new budget to database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO budgets (user_id, category, limit_amount, alert_50, alert_75, alert_90, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, category, limit_amount, alert_50, alert_75, alert_90, notes))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def update_budget(user_id, category, limit_amount, alert_50=True, alert_75=True, alert_90=True, notes=""):
    """Update existing budget"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE budgets
        SET limit_amount = ?, alert_50 = ?, alert_75 = ?, alert_90 = ?, notes = ?
        WHERE user_id = ? AND category = ?
    ''', (limit_amount, alert_50, alert_75, alert_90, notes, user_id, category))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

def delete_budget(user_id, category):
    """Delete budget from database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM budgets WHERE user_id = ? AND category = ?', (user_id, category))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

def get_category_spending(user_id, category, month):
    """Get total spending for a specific category in a specific month"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # month format should be 'YYYY-MM'
    cursor.execute('''
        SELECT SUM(amount)
        FROM expenses
        WHERE user_id = ? AND category = ? AND strftime('%Y-%m', date) = ?
    ''', (user_id, category, month))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result[0] is not None else 0.0

# ===== RECURRING TRANSACTIONS FUNCTIONS (NEW) =====

def get_all_recurring_transactions(user_id):
    """Get all recurring transactions for user"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, type, category, amount, frequency, start_date, next_date, description
        FROM recurring_transactions
        WHERE user_id = ?
        ORDER BY next_date
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    recurring_list = []
    for row in rows:
        recurring_list.append({
            'id': row[0],
            'type': row[1],
            'category': row[2],
            'amount': row[3],
            'frequency': row[4],
            'start_date': row[5],
            'next_date': row[6],
            'description': row[7]
        })
    return recurring_list

def add_recurring_transaction(user_id, trans_type, category, amount, frequency, start_date, description=""):
    """Add new recurring transaction"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO recurring_transactions
            (user_id, type, category, amount, frequency, start_date, next_date, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, trans_type, category, amount, frequency, start_date, start_date, description))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding recurring transaction: {e}")
        conn.close()
        return False

def delete_recurring_transaction(transaction_id):
    """Delete recurring transaction"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM recurring_transactions WHERE id = ?', (transaction_id,))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

def get_recurring_transaction_by_id(transaction_id):
    """Get single recurring transaction by ID"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM recurring_transactions WHERE id = ?', (transaction_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def process_recurring_transactions(user_id):
    """Process all pending recurring transactions"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    today = datetime.now().date()
    processed_count = 0  # ← ADDED: Track how many processed
    
    # Get all recurring transactions that are due
    cursor.execute('''
        SELECT id, type, category, amount, frequency, next_date, description
        FROM recurring_transactions
        WHERE user_id = ? AND date(next_date) <= date(?)
    ''', (user_id, str(today)))
    
    due_transactions = cursor.fetchall()
    
    for trans in due_transactions:
        trans_id, trans_type, category, amount, frequency, next_date, description = trans
        
        # Add to income or expense
        if trans_type == 'Income':  # ← FIXED: Capital 'I'
            cursor.execute('''
                INSERT INTO income (user_id, source, amount, date, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, category, amount, str(today), f"[Recurring] {description}"))
        else:
            cursor.execute('''
                INSERT INTO expenses (user_id, category, amount, date, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, category, amount, str(today), f"[Recurring] {description}"))
        
        processed_count += 1  # ← ADDED: Increment counter
        
        # Calculate next date
        next_date_obj = datetime.strptime(next_date, '%Y-%m-%d').date()
        
        if frequency == 'Daily':  # ← FIXED: Capital 'D'
            new_next_date = next_date_obj + timedelta(days=1)
        elif frequency == 'Weekly':  # ← FIXED: Capital 'W'
            new_next_date = next_date_obj + timedelta(weeks=1)
        elif frequency == 'Monthly':  # ← FIXED: Capital 'M'
            # Add 1 month
            month = next_date_obj.month + 1
            year = next_date_obj.year
            if month > 12:
                month = 1
                year += 1
            try:
                new_next_date = next_date_obj.replace(year=year, month=month)
            except ValueError:
                # Handle case where day doesn't exist in next month (e.g., Jan 31 -> Feb 31)
                # Use last day of month
                last_day = calendar.monthrange(year, month)[1]
                new_next_date = next_date_obj.replace(year=year, month=month, day=last_day)
        elif frequency == 'Yearly':  # ← FIXED: Capital 'Y'
            new_next_date = next_date_obj.replace(year=next_date_obj.year + 1)
        else:
            new_next_date = next_date_obj
        
        # Update next_date
        cursor.execute('''
            UPDATE recurring_transactions 
            SET next_date = ? 
            WHERE id = ?
        ''', (str(new_next_date), trans_id))
    
    conn.commit()
    conn.close()
    
    return processed_count  # ← ADDED: Return the count!

# Initialize database when module is imported
init_database()
