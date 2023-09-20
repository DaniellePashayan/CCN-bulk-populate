from datetime import datetime
from tkinter import filedialog as fd

import pandas as pd

from util import date_functions, mappings, utilitiy_functions
from loguru import logger


class RPA_CCN_Bulk_Combine():
    def __init__(self, query_date: str = None, file_generation_date: str = None):
        """_summary_

        Args:
            query_date (str, optional): Date of the query in MM/DD/YYYY format. Defaults to None.
            file_generation_date (str, optional): Date that the file should be saved with in the name of the file in MM DD YYYY format. Defaults to None.
        """
        self.template = pd.read_excel('./references/ccn_template.xlsx')
        
        self.query_location = r'M:\CPP-Data\Sutherland RPA\Northwell Process Automation ETM Files\Monthly Reports\Charge Correction\New vs Established\ETM Export'
        
        self.file = fd.askopenfilename(defaultextension='.txt', filetypes=[(
            '.txt', '*.txt')], initialdir=self.query_location, title='Select a file')
        logger.info(f'File selected: {self.file}')
        self.query_date =  datetime.strptime(self.file.split('/')[-1].split('.')[0], '%m %d %Y')

        # if user presses cancel button when selecting the file, exit program
        if self.file == '':
            exit()
        
        self.file_date = get_bot_file_date(date).strftime(format='%m %d %Y')
        year = self.file_date.strftime(format='%Y')
        month = self.file_date.strftime(format='%m')
        print(year, month)
        
        self.file_date_nosp = get_bot_file_date(date).strftime(format='%m%d%Y')
            
        self.output_location = f'M:/CPP-Data/Sutherland RPA/Northwell Process Automation ETM Files/Monthly Reports/Charge Correction/New vs Established/Formatted Inputs/'
        
RPA_CCN_Bulk_Combine()
