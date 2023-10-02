
import sqlite3
import uuid

db_path = 'M:/CPP-Data/Sutherland RPA/Northwell Process Automation ETM Files/Monthly Reports/Charge Correction/New vs Established/Invoices and Status.db'

# Connect to the SQLite database (creates the database file if it doesn't exist)
conn = sqlite3.connect(db_path)
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

def add_invoice(invoice_number, customer_name, invoice_date, amount, status):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Generate a UUID for the invoice
    invoice_id = str(uuid.uuid4())

    # Insert the invoice data into the table with the generated UUID
    cursor.execute('''
        INSERT INTO invoices (id, invoice_number, customer_name, invoice_date, amount, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (invoice_id, invoice_number, customer_name, invoice_date, amount, status))

    conn.commit()
    conn.close()
    
def update_invoice_status(invoice_id, new_status):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Update the status of the invoice with the given ID
    cursor.execute('UPDATE invoices SET status = ? WHERE id = ?', (new_status, invoice_id))

    conn.commit()
    conn.close()
    

def get_invoices():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Retrieve all invoices
    cursor.execute('SELECT * FROM invoices')
    invoices = cursor.fetchall()

    conn.close()
    return invoices
