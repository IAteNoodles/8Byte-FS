# Database Module

This module handles all database operations for the receipt analysis system using SQLite.

## Components

### 🗄️ database.py
**SQLite database management and operations**

**Key Functions:**
- `get_db_connection()` - Establish database connection
- `save_receipt(receipt)` - Save receipt to database
- `get_all_receipts()` - Retrieve all receipts
- `initialize_database()` - Setup database schema
- `migrate_database()` - Handle schema migrations

**Features:**
- Automatic schema creation and migration
- Connection pooling and management
- Data validation and integrity checks
- Error handling and rollback support
- Configurable database path

## Database Schema

### receipts Table
```sql
CREATE TABLE receipts (
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
```

### Field Descriptions
- `id` - Auto-incrementing primary key
- `vendor` - Business/store name (required)
- `transaction_date` - Transaction date in ISO format (required)
- `amount` - Transaction amount, must be positive (required)
- `currency` - ISO 4217 currency code (default: INR)
- `category` - Optional category classification
- `raw_text` - Original extracted text from receipt
- `upload_timestamp` - When the receipt was processed
- `created_at` - Database insertion timestamp

## Usage Examples

### Basic Operations
```python
from database.database import save_receipt, get_all_receipts
from models.receipt import ReceiptData
from datetime import date, datetime

# Create a receipt
receipt = ReceiptData(
    vendor="Starbucks",
    transaction_date=date(2024, 1, 15),
    amount=4.50,
    currency="USD",
    category="restaurant",
    raw_text="STARBUCKS COFFEE...",
    raw_data=b"binary_data_here",
    raw_data_extension="jpg"
)

# Save to database
receipt_id = save_receipt(receipt)
print(f"Saved receipt with ID: {receipt_id}")

# Retrieve all receipts
receipts = get_all_receipts()
print(f"Found {len(receipts)} receipts")
```

### Advanced Queries
```python
import sqlite3
from database.database import get_db_connection

def get_receipts_by_vendor(vendor_name):
    """Get all receipts from a specific vendor"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT * FROM receipts WHERE vendor LIKE ? ORDER BY transaction_date DESC",
            (f"%{vendor_name}%",)
        )
        receipts = [dict(row) for row in cursor.fetchall()]
        return receipts
    finally:
        conn.close()

def get_spending_by_month():
    """Get monthly spending totals"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                strftime('%Y-%m', transaction_date) as month,
                SUM(amount) as total_amount,
                COUNT(*) as transaction_count
            FROM receipts 
            GROUP BY strftime('%Y-%m', transaction_date)
            ORDER BY month DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()
```

## Configuration

### Environment Variables
- `DATABASE_PATH` - Custom database file path (default: `receipts.db`)
- `DATABASE_TIMEOUT` - Connection timeout in seconds (default: 30)

### Database Settings
```python
# Default configuration
DATABASE_FILE = os.getenv('DATABASE_PATH', 'receipts.db')
CONNECTION_TIMEOUT = int(os.getenv('DATABASE_TIMEOUT', '30'))

# Connection settings
conn = sqlite3.connect(
    DATABASE_FILE,
    timeout=CONNECTION_TIMEOUT,
    check_same_thread=False
)
conn.row_factory = sqlite3.Row  # Enable column access by name
```

## Schema Migration

The database module includes automatic schema migration:

### Migration Process
1. Check current schema version
2. Compare with expected schema
3. Apply necessary migrations
4. Update schema version

### Adding New Migrations
```python
def migrate_add_new_column():
    """Example migration to add a new column"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(receipts)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'new_column' not in columns:
            cursor.execute("ALTER TABLE receipts ADD COLUMN new_column TEXT")
            print("Added new_column to receipts table")
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()
```


### Indexing
```sql
-- Add indexes for common queries
CREATE INDEX IF NOT EXISTS idx_receipts_vendor ON receipts(vendor);
CREATE INDEX IF NOT EXISTS idx_receipts_date ON receipts(transaction_date);
CREATE INDEX IF NOT EXISTS idx_receipts_amount ON receipts(amount);
CREATE INDEX IF NOT EXISTS idx_receipts_category ON receipts(category);
```

## Future Enhancements

- [ ] PostgreSQL support for production deployments
- [ ] Database connection pooling
- [ ] Read replicas for scaling
- [ ] Automated backup scheduling
- [ ] Data archiving strategies
- [ ] Full-text search capabilities