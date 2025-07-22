import sqlite3
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))

from models.receipt import ReceiptData

# Configuration - can be overridden by environment variable
DATABASE_FILE = os.getenv('DATABASE_PATH', 'receipts.db')

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_FILE)
    # This allows us to access columns by name
    conn.row_factory = sqlite3.Row
    return conn

def check_schema_version():
    """Check if the database schema needs to be updated."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if currency column exists
    cursor.execute("PRAGMA table_info(receipts)")
    columns = [column[1] for column in cursor.fetchall()]
    conn.close()
    
    return 'currency' in columns

def migrate_database():
    """Migrate database schema to include missing fields."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Add currency column if it doesn't exist
        if not check_schema_version():
            print("Adding currency column to database...")
            cursor.execute("ALTER TABLE receipts ADD COLUMN currency TEXT DEFAULT 'INR'")
            print("Database migration completed successfully.")
        else:
            print("Database schema is up to date.")
            
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

def create_table():
    """Creates the receipts table if it doesn't already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor TEXT NOT NULL,
            transaction_date TEXT NOT NULL,
            amount REAL NOT NULL CHECK(amount > 0),
            currency TEXT NOT NULL DEFAULT 'INR',
            category TEXT,
            raw_text TEXT NOT NULL,
            upload_timestamp TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

def save_receipt(receipt: ReceiptData) -> int:
    """
    Saves a validated receipt record to the database.

    Args:
        receipt: A validated ReceiptData object.

    Returns:
        The ID of the newly inserted record.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO receipts (vendor, transaction_date, amount, currency, category, raw_text, upload_timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            receipt.vendor,
            receipt.transaction_date.isoformat(),
            receipt.amount,
            receipt.currency,
            receipt.category,
            receipt.raw_text,
            receipt.upload_timestamp.isoformat()
        ))
        conn.commit()
        last_id = cursor.lastrowid
        return last_id
    except sqlite3.Error as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_all_receipts() -> list[dict]:
    """Retrieves all receipts from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM receipts ORDER BY transaction_date DESC")
        receipts = [dict(row) for row in cursor.fetchall()]
        return receipts
    except sqlite3.Error as e:
        print(f"Database query error: {e}")
        return []
    finally:
        conn.close()

def initialize_database():
    """Initialize database with proper schema and migrations."""
    print("Initializing database...")
    create_table()
    migrate_database()
    print("Database initialization completed.")

# Initialize database when module is imported
initialize_database()

if __name__ == '__main__':
    print("Running database initialization...")
    initialize_database()
    print("Database setup completed successfully.")