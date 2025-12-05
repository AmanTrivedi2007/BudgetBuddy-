# database.py - Complete Database with Budget, Recurring Transactions, 2FA & SOC 2 Audit Trail

# Enhanced Security Features: Two-Factor Authentication + Audit Logging

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os
import hashlib
import calendar
import json

# Database file name
from persistent_storage import get_db_path
DB_FILE = get_db_path()



# ========================================
# DATABASE INITIALIZATION (FIXED - NO AUTO-DELETION)
# ========================================
def init_database():
    """Initialize database - creates tables if they don't exist, preserves all data"""
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
    
    # Create budgets table
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
    
    # Create recurring transactions table
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
    
    # Create user preferences table (for tutorial completion, dark mode, etc.)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id TEXT NOT NULL,
            preference_key TEXT NOT NULL,
            preference_value TEXT NOT NULL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, preference_key)
        )
    ''')
    
    # ========================================
    # SECURITY TABLES
    # ========================================
    
    # Two-Factor Authentication table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS two_factor_auth (
            user_id TEXT PRIMARY KEY,
            secret_key TEXT NOT NULL,
            backup_codes TEXT,
            enabled BOOLEAN DEFAULT 0,
            last_used TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Audit Logs table (SOC 2 Compliance)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            user_id TEXT,
            action TEXT NOT NULL,
            category TEXT NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            details TEXT,
            status TEXT DEFAULT 'SUCCESS',
            session_id TEXT
        )
    ''')
    
    # Create indexes for faster audit queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_category ON audit_logs(category)')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully with security features!")


# ========================================
# TWO-FACTOR AUTHENTICATION FUNCTIONS
# ========================================
def enable_2fa_for_user(user_id, secret_key, backup_codes):
    """Enable 2FA for a user"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Convert backup codes list to JSON string
        backup_codes_json = json.dumps(backup_codes)
        
        cursor.execute('''
            INSERT OR REPLACE INTO two_factor_auth (user_id, secret_key, backup_codes, enabled)
            VALUES (?, ?, ?, 1)
        ''', (user_id, secret_key, backup_codes_json))
        
        conn.commit()
        conn.close()
        
        # Log the event
        log_audit_event(user_id, "2FA_ENABLED", "SECURITY",
                       {"message": "Two-factor authentication enabled"}, "SUCCESS")
        return True
    except Exception as e:
        print(f"Error enabling 2FA: {e}")
        log_audit_event(user_id, "2FA_ENABLE_FAILED", "SECURITY",
                       {"error": str(e)}, "FAILURE")
        return False

def disable_2fa_for_user(user_id):
    """Disable 2FA for a user"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE two_factor_auth
            SET enabled = 0
            WHERE user_id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
        
        log_audit_event(user_id, "2FA_DISABLED", "SECURITY",
                       {"message": "Two-factor authentication disabled"}, "SUCCESS")
        return True
    except Exception as e:
        print(f"Error disabling 2FA: {e}")
        return False

def is_2fa_enabled(user_id):
    """Check if 2FA is enabled for user"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT enabled FROM two_factor_auth
            WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] == 1 if result else False
    except:
        return False

def get_2fa_secret(user_id):
    """Get 2FA secret key for user"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT secret_key FROM two_factor_auth
            WHERE user_id = ? AND enabled = 1
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    except:
        return None

def get_backup_codes(user_id):
    """Get backup codes for user"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT backup_codes FROM two_factor_auth
            WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            return json.loads(result[0])
        return []
    except:
        return []

def use_backup_code(user_id, code):
    """Use a backup code and remove it from list"""
    try:
        backup_codes = get_backup_codes(user_id)
        
        if code in backup_codes:
            backup_codes.remove(code)
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE two_factor_auth
                SET backup_codes = ?, last_used = ?
                WHERE user_id = ?
            ''', (json.dumps(backup_codes), datetime.now().isoformat(), user_id))
            
            conn.commit()
            conn.close()
            
            log_audit_event(user_id, "2FA_BACKUP_CODE_USED", "SECURITY",
                           {"message": f"Backup code used. {len(backup_codes)} codes remaining"}, "SUCCESS")
            return True
        return False
    except Exception as e:
        print(f"Error using backup code: {e}")
        return False

def update_2fa_last_used(user_id):
    """Update last used timestamp for 2FA"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE two_factor_auth
            SET last_used = ?
            WHERE user_id = ?
        ''', (datetime.now().isoformat(), user_id))
        
        conn.commit()
        conn.close()
    except:
        pass


# ========================================
# AUDIT LOGGING FUNCTIONS (SOC 2)
# ========================================
def log_audit_event(user_id, action, category, details=None, status="SUCCESS", ip_address=None, user_agent=None, session_id=None):
    """
    Log an audit event for SOC 2 compliance
    
    Parameters:
    - user_id: User identifier
    - action: Action performed (e.g., LOGIN_SUCCESS, ADD_EXPENSE, DELETE_BUDGET)
    - category: Category (AUTH, TRANSACTION, BUDGET, GOAL, SECURITY, DATA)
    - details: Additional details as dictionary
    - status: SUCCESS, FAILURE, WARNING
    - ip_address: User's IP address
    - user_agent: Browser/device information
    - session_id: Session identifier
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Convert details dict to JSON
        details_json = json.dumps(details) if details else None
        
        cursor.execute('''
            INSERT INTO audit_logs
            (user_id, action, category, ip_address, user_agent, details, status, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, action, category, ip_address, user_agent, details_json, status, session_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Audit logging error: {e}")
        return False

def get_audit_logs(user_id=None, limit=100, action=None, category=None, start_date=None, end_date=None):
    """
    Retrieve audit logs with optional filters
    
    Parameters:
    - user_id: Filter by user (None = all users)
    - limit: Maximum number of records
    - action: Filter by specific action
    - category: Filter by category
    - start_date: Filter from date (YYYY-MM-DD)
    - end_date: Filter to date (YYYY-MM-DD)
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        query = "SELECT * FROM audit_logs WHERE 1=1"
        params = []
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        if action:
            query += " AND action = ?"
            params.append(action)
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if start_date:
            query += " AND DATE(timestamp) >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(timestamp) <= ?"
            params.append(end_date)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        
        results = []
        for row in cursor.fetchall():
            log_dict = dict(zip(columns, row))
            # Parse JSON details
            if log_dict.get('details'):
                try:
                    log_dict['details'] = json.loads(log_dict['details'])
                except:
                    pass
            results.append(log_dict)
        
        conn.close()
        return results
    except Exception as e:
        print(f"Error retrieving audit logs: {e}")
        return []

def get_audit_summary(user_id, days=30):
    """Get audit summary statistics for user"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Total events
        cursor.execute('''
            SELECT COUNT(*) FROM audit_logs
            WHERE user_id = ? AND DATE(timestamp) >= DATE('now', '-' || ? || ' days')
        ''', (user_id, days))
        total_events = cursor.fetchone()[0]
        
        # Events by category
        cursor.execute('''
            SELECT category, COUNT(*) as count FROM audit_logs
            WHERE user_id = ? AND DATE(timestamp) >= DATE('now', '-' || ? || ' days')
            GROUP BY category
            ORDER BY count DESC
        ''', (user_id, days))
        by_category = dict(cursor.fetchall())
        
        # Failed attempts
        cursor.execute('''
            SELECT COUNT(*) FROM audit_logs
            WHERE user_id = ? AND status = 'FAILURE'
            AND DATE(timestamp) >= DATE('now', '-' || ? || ' days')
        ''', (user_id, days))
        failed_attempts = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_events': total_events,
            'by_category': by_category,
            'failed_attempts': failed_attempts,
            'period_days': days
        }
    except Exception as e:
        print(f"Error getting audit summary: {e}")
        return None

def export_audit_logs_csv(user_id=None, filename="audit_logs.csv"):
    """Export audit logs to CSV file"""
    try:
        logs = get_audit_logs(user_id=user_id, limit=10000)
        if not logs:
            return False
        
        df = pd.DataFrame(logs)
        df.to_csv(filename, index=False)
        
        log_audit_event(user_id or "SYSTEM", "AUDIT_EXPORT", "DATA",
                       {"filename": filename, "record_count": len(logs)}, "SUCCESS")
        return True
    except Exception as e:
        print(f"Error exporting audit logs: {e}")
        return False


# ========================================
# INCOME FUNCTIONS (WITH AUDIT LOGGING)
# ========================================
def add_income_to_db(user_id, source, amount, date, notes=""):
    """Add income record to database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO income (user_id, source, amount, date, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, source, amount, str(date), notes))
        conn.commit()
        conn.close()
        
        # Log the audit event
        log_audit_event(user_id, "ADD_INCOME", "TRANSACTION",
                       {"source": source, "amount": amount, "date": str(date)}, "SUCCESS")
        return True
    except Exception as e:
        log_audit_event(user_id, "ADD_INCOME_FAILED", "TRANSACTION",
                       {"error": str(e)}, "FAILURE")
        return False

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
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM income WHERE id = ? AND user_id = ?', (income_id, user_id))
        conn.commit()
        conn.close()
        
        log_audit_event(user_id, "DELETE_INCOME", "TRANSACTION",
                       {"income_id": income_id}, "SUCCESS")
        return True
    except Exception as e:
        log_audit_event(user_id, "DELETE_INCOME_FAILED", "TRANSACTION",
                       {"error": str(e)}, "FAILURE")
        return False


# ========================================
# EXPENSE FUNCTIONS (WITH AUDIT LOGGING)
# ========================================
def add_expense_to_db(user_id, category, amount, date, description=""):
    """Add expense record to database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO expenses (user_id, category, amount, date, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, category, amount, str(date), description))
        conn.commit()
        conn.close()
        
        # Log the audit event
        log_audit_event(user_id, "ADD_EXPENSE", "TRANSACTION",
                       {"category": category, "amount": amount, "date": str(date)}, "SUCCESS")
        return True
    except Exception as e:
        log_audit_event(user_id, "ADD_EXPENSE_FAILED", "TRANSACTION",
                       {"error": str(e)}, "FAILURE")
        return False

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
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM expenses WHERE id = ? AND user_id = ?', (expense_id, user_id))
        conn.commit()
        conn.close()
        
        log_audit_event(user_id, "DELETE_EXPENSE", "TRANSACTION",
                       {"expense_id": expense_id}, "SUCCESS")
        return True
    except Exception as e:
        log_audit_event(user_id, "DELETE_EXPENSE_FAILED", "TRANSACTION",
                       {"error": str(e)}, "FAILURE")
        return False


# ========================================
# GOAL FUNCTIONS (WITH AUDIT LOGGING)
# ========================================
def add_goal_to_db(user_id, name, target_amount, description=""):
    """Add new goal to database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO goals (user_id, name, target_amount, saved_amount, description, created_date)
            VALUES (?, ?, ?, 0, ?, ?)
        ''', (user_id, name, target_amount, description, str(datetime.now().date())))
        conn.commit()
        conn.close()
        
        log_audit_event(user_id, "CREATE_GOAL", "GOAL",
                       {"name": name, "target_amount": target_amount}, "SUCCESS")
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
    try:
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
        
        log_audit_event(user_id, "GOAL_DEPOSIT", "GOAL",
                       {"goal_name": goal_name, "amount": amount}, "SUCCESS")
        return True
    except Exception as e:
        log_audit_event(user_id, "GOAL_DEPOSIT_FAILED", "GOAL",
                       {"error": str(e)}, "FAILURE")
        return False

def withdraw_from_goal(user_id, goal_name, amount, note=""):
    """Withdraw money from a specific goal"""
    try:
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
        
        log_audit_event(user_id, "GOAL_WITHDRAWAL", "GOAL",
                       {"goal_name": goal_name, "amount": amount}, "SUCCESS")
        return True
    except Exception as e:
        log_audit_event(user_id, "GOAL_WITHDRAWAL_FAILED", "GOAL",
                       {"error": str(e)}, "FAILURE")
        return False

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
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM goal_transactions WHERE goal_name = ? AND user_id = ?', (goal_name, user_id))
        cursor.execute('DELETE FROM goals WHERE name = ? AND user_id = ?', (goal_name, user_id))
        conn.commit()
        conn.close()
        
        log_audit_event(user_id, "DELETE_GOAL", "GOAL",
                       {"goal_name": goal_name}, "SUCCESS")
        return True
    except Exception as e:
        log_audit_event(user_id, "DELETE_GOAL_FAILED", "GOAL",
                       {"error": str(e)}, "FAILURE")
        return False


# ========================================
# LOGIN ATTEMPTS FUNCTIONS
# ========================================
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


# ========================================
# BUDGET MANAGEMENT FUNCTIONS (WITH AUDIT LOGGING)
# ========================================
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
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO budgets (user_id, category, limit_amount, alert_50, alert_75, alert_90, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, category, limit_amount, alert_50, alert_75, alert_90, notes))
        conn.commit()
        conn.close()
        
        log_audit_event(user_id, "CREATE_BUDGET", "BUDGET",
                       {"category": category, "limit_amount": limit_amount}, "SUCCESS")
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def update_budget(user_id, category, limit_amount, alert_50=True, alert_75=True, alert_90=True, notes=""):
    """Update existing budget"""
    try:
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
        
        if rows_affected > 0:
            log_audit_event(user_id, "UPDATE_BUDGET", "BUDGET",
                           {"category": category, "new_limit": limit_amount}, "SUCCESS")
        return rows_affected > 0
    except Exception as e:
        log_audit_event(user_id, "UPDATE_BUDGET_FAILED", "BUDGET",
                       {"error": str(e)}, "FAILURE")
        return False

def delete_budget(user_id, category):
    """Delete budget from database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM budgets WHERE user_id = ? AND category = ?', (user_id, category))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        if rows_affected > 0:
            log_audit_event(user_id, "DELETE_BUDGET", "BUDGET",
                           {"category": category}, "SUCCESS")
        return rows_affected > 0
    except Exception as e:
        log_audit_event(user_id, "DELETE_BUDGET_FAILED", "BUDGET",
                       {"error": str(e)}, "FAILURE")
        return False

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


# ========================================
# RECURRING TRANSACTIONS FUNCTIONS (WITH AUDIT LOGGING)
# ========================================
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
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO recurring_transactions
            (user_id, type, category, amount, frequency, start_date, next_date, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, trans_type, category, amount, frequency, start_date, start_date, description))
        conn.commit()
        conn.close()
        
        log_audit_event(user_id, "CREATE_RECURRING", "TRANSACTION",
                       {"type": trans_type, "category": category, "amount": amount, "frequency": frequency}, "SUCCESS")
        return True
    except Exception as e:
        print(f"Error adding recurring transaction: {e}")
        log_audit_event(user_id, "CREATE_RECURRING_FAILED", "TRANSACTION",
                       {"error": str(e)}, "FAILURE")
        return False

def delete_recurring_transaction(transaction_id):
    """Delete recurring transaction"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM recurring_transactions WHERE id = ?', (transaction_id,))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        if rows_affected > 0:
            log_audit_event("SYSTEM", "DELETE_RECURRING", "TRANSACTION",
                           {"transaction_id": transaction_id}, "SUCCESS")
        return rows_affected > 0
    except Exception as e:
        log_audit_event("SYSTEM", "DELETE_RECURRING_FAILED", "TRANSACTION",
                       {"error": str(e)}, "FAILURE")
        return False

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
    processed_count = 0
    
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
        if trans_type == 'Income':
            cursor.execute('''
                INSERT INTO income (user_id, source, amount, date, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, category, amount, str(today), f"[Recurring] {description}"))
        else:
            cursor.execute('''
                INSERT INTO expenses (user_id, category, amount, date, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, category, amount, str(today), f"[Recurring] {description}"))
        
        processed_count += 1
        
        # Calculate next date
        next_date_obj = datetime.strptime(next_date, '%Y-%m-%d').date()
        
        if frequency == 'Daily':
            new_next_date = next_date_obj + timedelta(days=1)
        elif frequency == 'Weekly':
            new_next_date = next_date_obj + timedelta(weeks=1)
        elif frequency == 'Monthly':
            # Add 1 month
            month = next_date_obj.month + 1
            year = next_date_obj.year
            if month > 12:
                month = 1
                year += 1
            try:
                new_next_date = next_date_obj.replace(year=year, month=month)
            except ValueError:
                # Use last day of month
                last_day = calendar.monthrange(year, month)[1]
                new_next_date = next_date_obj.replace(year=year, month=month, day=last_day)
        elif frequency == '3 Months':
            # Add 3 months
            month = next_date_obj.month + 3
            year = next_date_obj.year
            while month > 12:
                month -= 12
                year += 1
            try:
                new_next_date = next_date_obj.replace(year=year, month=month)
            except ValueError:
                last_day = calendar.monthrange(year, month)[1]
                new_next_date = next_date_obj.replace(year=year, month=month, day=last_day)
        elif frequency == '6 Months':
            # Add 6 months
            month = next_date_obj.month + 6
            year = next_date_obj.year
            while month > 12:
                month -= 12
                year += 1
            try:
                new_next_date = next_date_obj.replace(year=year, month=month)
            except ValueError:
                last_day = calendar.monthrange(year, month)[1]
                new_next_date = next_date_obj.replace(year=year, month=month, day=last_day)
        elif frequency == 'Yearly':
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
    
    if processed_count > 0:
        log_audit_event(user_id, "RECURRING_PROCESSED", "TRANSACTION",
                       {"count": processed_count}, "SUCCESS")
    return processed_count


# ========================================
# USER PREFERENCES FUNCTIONS
# ========================================
def save_user_preference(user_id, preference_key, preference_value):
    """Save user preference to database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO user_preferences (user_id, preference_key, preference_value, updated_at)
        VALUES (?, ?, ?, ?)
    """, (user_id, preference_key, preference_value, str(datetime.now())))
    
    conn.commit()
    conn.close()

def get_user_preference(user_id, preference_key, default_value=None):
    """Get user preference from database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT preference_value FROM user_preferences 
        WHERE user_id = ? AND preference_key = ?
    """, (user_id, preference_key))
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else default_value

def delete_user_preference(user_id, preference_key):
    """Delete user preference from database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        DELETE FROM user_preferences 
        WHERE user_id = ? AND preference_key = ?
    """, (user_id, preference_key))
    
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    return rows_affected > 0


# Initialize database when module is imported


