# database.py
import sqlite3
import pandas as pd
from datetime import datetime

# Database file name
DB_FILE = "budgetbuddy.db"

def init_database():
    """Initialize database and create tables if they don't exist"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create income table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create expenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create goals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            target_amount REAL NOT NULL,
            saved_amount REAL DEFAULT 0,
            description TEXT,
            created_date TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create goal transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goal_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_name TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            note TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (goal_name) REFERENCES goals(name)
        )
    ''')
    
    conn.commit()
    conn.close()

# ===== INCOME FUNCTIONS =====
def add_income_to_db(source, amount, date, notes=""):
    """Add income record to database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO income (source, amount, date, notes)
        VALUES (?, ?, ?, ?)
    ''', (source, amount, str(date), notes))
    conn.commit()
    conn.close()

def get_all_income():
    """Get all income records from database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, source, amount, date, notes FROM income ORDER BY date DESC')
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to list of dictionaries
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

def delete_income_from_db(income_id):
    """Delete income record from database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM income WHERE id = ?', (income_id,))
    conn.commit()
    conn.close()

# ===== EXPENSE FUNCTIONS =====
def add_expense_to_db(category, amount, date, description=""):
    """Add expense record to database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO expenses (category, amount, date, description)
        VALUES (?, ?, ?, ?)
    ''', (category, amount, str(date), description))
    conn.commit()
    conn.close()

def get_all_expenses():
    """Get all expense records from database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, category, amount, date, description FROM expenses ORDER BY date DESC')
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to list of dictionaries
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

def delete_expense_from_db(expense_id):
    """Delete expense record from database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
    conn.commit()
    conn.close()

# ===== GOAL FUNCTIONS =====
def add_goal_to_db(name, target_amount, description=""):
    """Add new goal to database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO goals (name, target_amount, saved_amount, description, created_date)
            VALUES (?, ?, 0, ?, ?)
        ''', (name, target_amount, description, str(datetime.now().date())))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False  # Goal name already exists

def get_all_goals():
    """Get all goals from database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT name, target_amount, saved_amount, description, created_date 
        FROM goals
    ''')
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
            'transactions': get_goal_transactions(row[0])
        }
        goals_list.append(goal)
    return goals_list

def add_money_to_goal(goal_name, amount, note=""):
    """Add money to a specific goal"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Update goal saved amount
    cursor.execute('''
        UPDATE goals SET saved_amount = saved_amount + ?
        WHERE name = ?
    ''', (amount, goal_name))
    
    # Record transaction
    cursor.execute('''
        INSERT INTO goal_transactions (goal_name, amount, date, note)
        VALUES (?, ?, ?, ?)
    ''', (goal_name, amount, str(datetime.now().date()), note))
    
    conn.commit()
    conn.close()

def withdraw_from_goal(goal_name, amount, note=""):
    """Withdraw money from a specific goal"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Update goal saved amount
    cursor.execute('''
        UPDATE goals SET saved_amount = saved_amount - ?
        WHERE name = ?
    ''', (amount, goal_name))
    
    # Record transaction (negative amount)
    cursor.execute('''
        INSERT INTO goal_transactions (goal_name, amount, date, note)
        VALUES (?, ?, ?, ?)
    ''', (goal_name, -amount, str(datetime.now().date()), note))
    
    conn.commit()
    conn.close()

def get_goal_transactions(goal_name):
    """Get all transactions for a specific goal"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT amount, date, note FROM goal_transactions
        WHERE goal_name = ?
        ORDER BY date DESC
    ''', (goal_name,))
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

def delete_goal_from_db(goal_name):
    """Delete goal and all its transactions"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Delete transactions first
    cursor.execute('DELETE FROM goal_transactions WHERE goal_name = ?', (goal_name,))
    
    # Delete goal
    cursor.execute('DELETE FROM goals WHERE name = ?', (goal_name,))
    
    conn.commit()
    conn.close()
