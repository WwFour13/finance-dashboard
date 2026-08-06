"""
SQLite data layer for the expense dashboard.
"""
import sqlite3
from datetime import datetime, date

DB_FILE = "expenses.db"

CATEGORIES = [
    "Food & Dining",
    "Groceries",
    "Transport",
    "Shopping",
    "Bills & Utilities",
    "Entertainment",
    "Health",
    "Education",
    "Travel",
    "Other",
]


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'Uncategorized',
            amount REAL NOT NULL,
            currency TEXT NOT NULL,
            gbp REAL NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def add_expense(iso_date, description, category, amount, currency, gbp):
    conn = get_connection()
    conn.execute(
        """INSERT INTO expenses (date, description, category, amount, currency, gbp, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (iso_date, description, category, amount, currency, gbp, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_expenses(start=None, end=None, category=None):
    conn = get_connection()
    query = "SELECT * FROM expenses WHERE 1=1"
    params = []
    if start:
        query += " AND date >= ?"
        params.append(start)
    if end:
        query += " AND date <= ?"
        params.append(end)
    if category and category != "All":
        query += " AND category = ?"
        params.append(category)
    query += " ORDER BY date DESC, id DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_category_breakdown():
    """Total GBP spend per category, all time."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT category, SUM(gbp) as total FROM expenses GROUP BY category ORDER BY total DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_monthly_trend(months_back=6):
    """Total GBP spend per month for the last `months_back` months."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT strftime('%Y-%m', date) as month, SUM(gbp) as total
           FROM expenses
           GROUP BY month
           ORDER BY month DESC
           LIMIT ?""",
        (months_back,),
    ).fetchall()
    conn.close()
    return list(reversed([dict(r) for r in rows]))


def get_month_total(year_month):
    """year_month like '2026-08'."""
    conn = get_connection()
    row = conn.execute(
        "SELECT SUM(gbp) as total FROM expenses WHERE strftime('%Y-%m', date) = ?",
        (year_month,),
    ).fetchone()
    conn.close()
    return row["total"] or 0.0


def get_all_time_total():
    conn = get_connection()
    row = conn.execute("SELECT SUM(gbp) as total FROM expenses").fetchone()
    conn.close()
    return row["total"] or 0.0


def get_recent(limit=10):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM expenses ORDER BY date DESC, id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_expense(expense_id):
    conn = get_connection()
    conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()


def convert_date(datestr):
    """Same behaviour as the original app: blank -> today, else DD/MM/YYYY -> ISO."""
    if not datestr or not datestr.strip():
        return date.today().isoformat()
    try:
        d = datetime.strptime(datestr.strip(), "%d/%m/%Y")
        return d.date().isoformat()
    except ValueError:
        raise ValueError("Invalid date. Use DD/MM/YYYY.")
