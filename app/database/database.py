# In database/database.py
import sqlite3
from models.receipt import ReceiptData # TODO: Make sure the import path is correct

# TODO: The database name should be configured, not hardcoded.
DATABASE_FILE = "receipts.db"

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_FILE)
    # This allows us to access columns by name
    conn.row_factory = sqlite3.Row
    return conn
# In database/database.py
import sqlite3
from models.receipt import ReceiptData # TODO: Make sure the import path is correct

# TODO: The database name should be configured, not hardcoded.
DATABASE_FILE = "receipts.db"

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_FILE)
    # This allows us to access columns by name
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    """Creates the receipts table if it doesn't already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor TEXT NOT NULL,
            transaction_date TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT,
            raw_text TEXT NOT NULL,
            upload_timestamp TEXT NOT NULL
            -- TODO: Decide if raw_data and raw_data_extension should be stored.
            -- Storing large blobs (raw_data) in the DB is generally not recommended.
            -- It might be better to save the file to disk and store the path.
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
    cursor.execute("""
        INSERT INTO receipts (vendor, transaction_date, amount, currency, category, raw_text, upload_timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        receipt.vendor,
        receipt.transaction_date.isoformat(),
        receipt.amount,
        receipt.currency, # Add the currency field here
        receipt.category,
        receipt.raw_text,
        receipt.upload_timestamp.isoformat()
    ))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

def get_all_receipts() -> list[dict]:
    """Retrieves all receipts from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM receipts ORDER BY transaction_date DESC")
    receipts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return receipts


# Call create_table() when the application starts.
# You might run this once manually or build it into your app's startup sequence.
create_table()

# In database/database.py

# ... (all your existing functions: get_db_connection, create_table, save_receipt)

# Add this block to the end of the file
if __name__ == '__main__':
    print("Initializing the database...")
    create_table()
    print("Database 'receipts.db' and table 'receipts' created successfully.")

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
    cursor.execute("""
        INSERT INTO receipts (vendor, transaction_date, amount, category, raw_text, upload_timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        receipt.vendor,
        receipt.transaction_date.isoformat(),
        receipt.amount,
        receipt.category,
        receipt.raw_text,
        receipt.upload_timestamp.isoformat()
    ))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

def get_all_receipts() -> list[dict]:
    """Retrieves all receipts from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM receipts ORDER BY transaction_date DESC")
    receipts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return receipts


# Call create_table() when the application starts.
# You might run this once manually or build it into your app's startup sequence.
create_table()

# In database/database.py

# ... (all your existing functions: get_db_connection, create_table, save_receipt)

# Add this block to the end of the file
if __name__ == '__main__':
    print("Initializing the database...")
    create_table()
    print("Database 'receipts.db' and table 'receipts' created successfully.")