import pandas as pd
import sqlite3
import re
import datetime
import os

class Database():
    def __init__(self, query_date: str, ccn_type: str = 'Electronic'):
        
        self.query_date = query_date
        
        # check if self.query_date is in MM DD YYYY format as a string using regex
        if not re.match(r'(\d{2}\s\d{2}\s\d{4})', self.query_date):
            raise ValueError(f'query_date must be in MM DD YYYY format as a string')
        
        self.year = self.query_date[6:10]
        self.month = self.query_date[0:2]
        self.day = self.query_date[3:5]
        
        self.ccn_type = ccn_type
        
        # if self.ccn_type not in "electronic" or "paper"
        if self.ccn_type not in ["Electronic", "Paper"]:
            raise ValueError(f'ccn_type must be "Electronic" or "Paper"')
        
        self.input_path = f'M:/CPP-Data/Sutherland RPA/Northwell Process Automation ETM Files/Monthly Reports/Charge Correction/New vs Established/ETM Export - {ccn_type}/{query_date}.xlsx'
        # print(self.input_path)
        self.output_path = f'M:/CPP-Data/Sutherland RPA/ChargeCorrection/{self.year}/{self.month} {self.year}/{self.month}{self.day}{self.year}/Northwell_ChargeCorrection_Output_{self.month}{self.day}{self.year}.xls'
        
    def open_database_connection(self):
        path = r'M:\CPP-Data\Sutherland RPA\Northwell Process Automation ETM Files\Monthly Reports\Charge Correction\New vs Established'
        conn = sqlite3.connect(f'{path}/Invoices and Status.db')
        return conn, conn.cursor()

    def close_database_connection(self, conn):
        conn.commit()
        conn.close()

    def read_input(self) -> pd.DataFrame:
        # read the input file
        file_data = pd.read_excel(self.input_path, skiprows=1)
        return file_data
    
    def add_input_to_db(self):
        # add the input file to the database table
        if os.path.exists(self.input_path):
            conn, cursor = self.open_database_connection()
            
            df_input = self.read_input()
            for index, row in df_input.iterrows():

                task_nm = str(row['Task Nm'])
                invoice_number = str(row['Invoice'])
                fsc = str(row['FSC'])
                tot_chg = float(row['Tot Chg'])
                invoice_balance = float(row['Invoice  Balance'])
                new_visit_cpt_list = str(row['New Visit CPT'])
                full_cpt_list = str(row['CPT  List'])
                tcn = str(row['TCN'])
                rejection_date = datetime.datetime.strptime(row['Max New Pt Rej Post Dt'], '%m/%d/%Y').date()
                outsource_tag = str(row['Outsource'])
                etm_status = str(row['Status'])
                review_date = row['Review  Dt'].date()
                
                # Check if the invoice and review date combination already exists in the database
                cursor.execute('SELECT * FROM invoices WHERE invoice_number=? AND review_date=?', (invoice_number, review_date))
                existing_entry = cursor.fetchone()

                if not existing_entry:
                    try:
                        # Insert the invoice into the database
                        cursor.execute('INSERT INTO invoices (task_nm, invoice_number, fsc, tot_chg, invoice_balance, new_visit_cpt_list, full_cpt_list, tcn, rejection_date, outsource_tag, etm_status, review_date, outcome) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                            (task_nm, invoice_number, fsc, tot_chg, invoice_balance, new_visit_cpt_list, full_cpt_list, tcn, rejection_date, outsource_tag, etm_status, review_date, None))
                    except Exception as e:
                        print(f"An error occurred: {str(e)}")
                        self.close_database_connection(conn)
            self.close_database_connection(conn)
        
    def read_output(self):
        # read the output file
        file_data = pd.read_excel(self.output_path)
        return file_data
    
    def add_output_to_db(self):
        if os.path.exists(self.output_path):
            df_output = self.read_output()
            conn, cursor = self.open_database_connection()
            review_date = pd.to_datetime(self.query_date).date()
            for index, row in df_output.iterrows():
                invoice_number = str(row['INVNUM'])
                outcome = str(row['RetrievalStatus'])
                
                cursor.execute('UPDATE invoices SET outcome=? WHERE invoice_number=? AND review_date=?', (outcome, invoice_number, review_date))
            
            self.close_database_connection(conn)
    
    
def backlog():            
    for ccn_type in ['Electronic', 'Paper']:
        for date in pd.date_range(start='09 19 2023', end='10 03 2023'):
            str_date = date.strftime('%m %d %Y')
            print(ccn_type, str_date)
            
            db = Database(str_date, ccn_type=ccn_type)
            db.add_input_to_db()
            db.add_output_to_db()