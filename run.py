import sys
import os
from datetime import datetime
from tkinter import filedialog as fd

import pandas as pd
from loguru import logger

import util.date_functions as date_functions
import util.mappings as mappings
import util.utilitiy_functions as utilitiy_functions

handler = logger.add("./logs/{time:YYYY-MM-DD}.log", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} - {message}",
                     colorize=True, backtrace=True, diagnose=True, level='SUCCESS')


class RPA_CCN_Bulk_Combine():
    def __init__(self, query_date: str = None, file_generation_date: str = None):
        """_summary_

        Args:
            query_date (str, optional): Date of the query in MM DD YYYY format. Defaults to None.
            file_generation_date (str, optional): Date that the file should be saved with in the name of the file in MM DD YYYY format. Defaults to None.
        """

        self.template = pd.read_excel('./references/ccn_template.xlsx')

        self.export_location = r'M:\CPP-Data\Sutherland RPA\Northwell Process Automation ETM Files\Monthly Reports\Charge Correction\New vs Established\ETM Export'

        # if user passes in a date, read the file manually, otherwise let the user select the file they want to run
        if not query_date:
            self.file = fd.askopenfilename(defaultextension='.txt', filetypes=[(
                '.xlsx', '*.xlsx')], initialdir=self.export_location, title='Select a file')
            # if user presses cancel button when selecting the file, exit program
            if self.file == '':
                exit()

            logger.info(f'File selected: {self.file}')
        else:
            self.file = f'{self.export_location}/{query_date}.xlsx'

        # export date is the date of the etm export and the date the process is being run
        self.export_date = datetime.strptime(
            self.file.split('/')[-1].split('.')[0], '%m %d %Y')

        # file date is the date to populate the charge correction file for

        if not file_generation_date:
            self.file_generation_date = date_functions.get_next_business_day(
                self.export_date)
        else:
            self.file_generation_date = datetime.strptime(
                file_generation_date, '%m %d %Y')
        logger.debug(self.export_date)
        logger.debug(self.file_generation_date)

        # year and month are needed to create dated folders
        self.year = self.file_generation_date.strftime(format='%Y')
        self.month = self.file_generation_date.strftime(format='%m')
        self.day = self.file_generation_date.strftime(format='%d')

        # takes the file date and converts into MMDDYYYY format as a string
        self.file_date_nosp = self.file_generation_date.strftime(
            format='%m%d%Y')

        self.output_location = f'M:/CPP-Data/Sutherland RPA/Northwell Process Automation ETM Files/Monthly Reports/Charge Correction/New vs Established/Formatted Inputs/'

        self.file_data = self.read_data(self.file)

    def read_data(self, file_path):
        if os.path.exists(file_path):
            file_data = pd.read_excel(file_path, skiprows=1, names=mappings.columns,
                                 dtype=mappings.dtypes, parse_dates=['Max New Pt Rejection'])
            logger.info('data read')
            file_data = self.filter_data(file_data)
            logger.success('data read and filtered')            

            return file_data
        else:
            logger.critical('File does not exist')

    def filter_data(self, file_data: pd.DataFrame):
        # EXCLUSIONS AS OF 9/20/2023
        # remove vendor inventory
        # remove balance < 304
        file_data['Outsource Tag'].fillna('', inplace=True)

        # filter file_data on Outsource Tag column to remove rows where the Outsource Tag begins with IK, RC, IK, RB, or AP
        tags_to_exclude = ['AP', 'IK', 'RB', 'RC']
        file_data = file_data[~file_data['Outsource Tag'].str.startswith(
            tuple(tags_to_exclude))]
        file_data = file_data[file_data['Invoice Balance'] >= 304]
        return file_data


RPA_CCN_Bulk_Combine(query_date='09 20 2023')
