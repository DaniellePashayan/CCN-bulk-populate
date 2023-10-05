import pandas as pd
import sqlite3
import re
import datetime
import os

def open_database_connection() -> tuple:
    path = r'M:\CPP-Data\Sutherland RPA\Northwell Process Automation ETM Files\Monthly Reports\Charge Correction\New vs Established'
    conn = sqlite3.connect(f'{path}/Invoices and Status.db')
    return conn, conn.cursor()

def close_database_connection(conn):
    conn.commit()
    conn.close()
    
def update_row_outcome(cursor, invoice_number: str, file_gen_date:str, outcome: str):
    cursor.execute(f"UPDATE invoices SET outcome =? WHERE invoice_number =? AND file_generation_date=?", (outcome, invoice_number, file_gen_date))