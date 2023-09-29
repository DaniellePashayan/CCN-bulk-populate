
import sqlite3
import uuid

# Connect to the SQLite database (creates the database file if it doesn't exist)
conn = sqlite3.connect('invoice_tracker.db')
cursor = conn.cursor()

# Create an invoices table (you can customize the schema as needed)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS invoices (
        id TEXT PRIMARY KEY,
        invoice_number TEXT,
        customer_name TEXT,
        invoice_date DATE,
        amount REAL,
        status TEXT
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()