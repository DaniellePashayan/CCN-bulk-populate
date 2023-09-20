import sys
import os
from datetime import datetime
from tkinter import filedialog as fd

import pandas as pd
from loguru import logger

import util.date_functions as date_functions
import util.mappings as mappings
import util.utilitiy_functions as utilitiy_functions

handler = logger.add("./logs/{time:YYYY-MM-DD}.log", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} - {message}", colorize=True, backtrace=True, diagnose=True, level='SUCCESS')

class RPA_CCN_Bulk_Combine():
    def __init__(self, query_date: str = None, file_generation_date: str = None):
        """_summary_

        Args:
            query_date (str, optional): Date of the query in MM/DD/YYYY format. Defaults to None.
            file_generation_date (str, optional): Date that the file should be saved with in the name of the file in MM DD YYYY format. Defaults to None.
        """
        
        self.template = pd.read_excel('./references/ccn_template.xlsx')

        self.export_location = r'M:\CPP-Data\Sutherland RPA\Northwell Process Automation ETM Files\Monthly Reports\Charge Correction\New vs Established\ETM Export'

        if not query_date:
            self.file = fd.askopenfilename(defaultextension='.txt', filetypes=[(
                '.xlsx', '*.xlsx')], initialdir=self.export_location, title='Select a file')
        else:
            self.file = f'{self.export_location}/{query_date}.xlsx'
        
        logger.success(f'File selected: {self.file}')
        
        # if user presses cancel button when selecting the file, exit program
        if self.file == '':
            exit()
            
        self.export_date = datetime.strptime(
            self.file.split('/')[-1].split('.')[0], '%m %d %Y')

        self.file_date = date_functions.get_next_business_day(self.export_date)
        logger.debug(self.export_date)
        logger.debug(self.file_date)
        
        self.year = self.file_date.strftime(format='%Y')
        self.month = self.file_date.strftime(format='%m')

        self.file_date_nosp = self.file_date.strftime(format='%m%d%Y')

        self.output_location = f'M:/CPP-Data/Sutherland RPA/Northwell Process Automation ETM Files/Monthly Reports/Charge Correction/New vs Established/Formatted Inputs/'

        self.file_data = self.read_data(self.file)

    def read_data(self,file_path):
        if os.path.exists(file_path):
            data = pd.read_excel(file_path)
            return data
        else:
            logger.critical('File does not exist')

RPA_CCN_Bulk_Combine(query_date='09 20 2023')
