from datetime import datetime

import util.date_functions as date_functions
from util.logger_config import logger
from file import Raw_File


class RPA_CCN_Bulk_Combine():
    def __init__(self, ccn_type: str = "Electronic", query_date: str | None = None, file_generation_date: str | None = None):
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
            today=datetime.today()
            query_date = today.strftime('%m %d %Y')
            self.file = f'{self.export_location}/{query_date}.xlsx'
        else:
            # check if query_date is in the correct format
            try:
                datetime.strptime(query_date, '%m %d %Y')
            except ValueError:
                logger.critical('Invalid query date format. Must be MM DD YYYY')
                exit()
            self.file = f'{self.export_location}/{query_date}.xlsx'

        # export date is the date of the etm export and the date the process is being run
        self.export_date = datetime.strptime(
            self.file.split('/')[-1].split('.')[0], '%m %d %Y')

        # file date is the date to populate the charge correction file for

        if not file_generation_date:
            logger.info('no file generation date passed in, using next business day')
            self.file_generation_date = date_functions.get_next_business_day(
                self.export_date)
        else:
            # check if query_date is in the correct format
            try:
                datetime.strptime(file_generation_date, '%m %d %Y')
            except ValueError:
                logger.critical('Invalid file_generation_date format. Must be MM DD YYYY')
                exit()
            self.file_generation_date = datetime.strptime(
                file_generation_date, '%m %d %Y')
        logger.info(f'current date: {self.export_date}')
        logger.info(f'file generation date: {self.file_generation_date}')

        Raw_File(self.file, self.ccn_type, query_date)
    
    def cleanup(self):
        """
        The daily files are saved in the main directory. When the month ends, move files from the prior month into their respective dated folder
        """
        