import sys
import os
from datetime import datetime
from tkinter import filedialog as fd

import pandas as pd

import util.date_functions as date_functions
import util.utilitiy_functions as utilitiy_functions
from util.logger_config import logger
from file import Raw_File


class RPA_CCN_Bulk_Combine():
    def __init__(self, ccn_type: str = "Electronic", query_date: str = None, file_generation_date: str = None):
        """_summary_

        Args:
            query_date (str, optional): Date of the query in MM DD YYYY format. Defaults to None.
            file_generation_date (str, optional): Date that the file should be saved with in the name of the file in MM DD YYYY format. Defaults to None.
        """
        
        self.ccn_type = ccn_type
        
        logger.info(f'ccn type: {self.ccn_type}')
        
        if self.ccn_type != 'Electronic' and self.ccn_type != 'Paper':
            logger.critical('Invalid CCN Type')
            exit()

        self.export_location = fr'M:\CPP-Data\Sutherland RPA\Northwell Process Automation ETM Files\Monthly Reports\Charge Correction\New vs Established\ETM Export - {self.ccn_type}'

        # if user passes in a date, read the file manually, otherwise let the user select the file they want to run
        if not query_date:
            self.file = fd.askopenfilename(defaultextension='.txt', filetypes=[(
                '.xlsx', '*.xlsx')], initialdir=self.export_location, title='Select a file')
            # if user presses cancel button when selecting the file, exit program
            if self.file == '':
                logger.critical('no file selected')
                exit()

            logger.info(f'File selected: {self.file}')
        else:
            self.file = f'{self.export_location}/{query_date}.xlsx'
            logger.debug(self.file)

        # export date is the date of the etm export and the date the process is being run
        self.export_date = datetime.strptime(
            self.file.split('/')[-1].split('.')[0], '%m %d %Y')

        # file date is the date to populate the charge correction file for

        if not file_generation_date:
            logger.info('no file generation date passed in, using next business day')
            self.file_generation_date = date_functions.get_next_business_day(
                self.export_date)
        else:
            self.file_generation_date = datetime.strptime(
                file_generation_date, '%m %d %Y')
        logger.info(f'current date: {self.export_date}')
        logger.info(f'file generation date: {self.file_generation_date}')


        # takes the file date and converts into MMDDYYYY format as a string
        file_date_spaces = self.file_generation_date.strftime(
            format='%m %d %Y')
        file_date_no_spaces = self.file_generation_date.strftime(
            format='%m%d%Y')

        output_location = 'M:/CPP-Data/Sutherland RPA/Northwell Process Automation ETM Files/Monthly Reports/Charge Correction/New vs Established/Formatted Inputs'
        
        file_name = f'HCOB16{ccn_type} {file_date_spaces}.xlsx'
        
        logger.info(f'output location: {output_location}/{file_date_no_spaces}/{file_name}')
        
        data = Raw_File(self.file, self.ccn_type, query_date)
        data.generate_output(file_date_no_spaces, output_location, file_name)
        