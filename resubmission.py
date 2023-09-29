import pandas as pd
from util.logger_config import logger
import util.mappings as mappings
import os
from util.date_functions import get_next_business_day as get_next_business_day
from file import Raw_File

class Resubmission():
    def __init__(self, query_date: str, ccn_type: str = 'Electronic'):
        """
        The ETM view will automatically pend invoices for 6 days when the denial comes in. The submission will only send invoices where the pend date is 6 days from the query date, as to prevent sending invoices that have already been sent. The combination process will take all invoices and check if they were already submitted on a previous days file (6 days prior). If an invoice did appear within the last 6 submissions, it will be excluded. However, if the bot fails to complete the inventory and the retrieval status is null, it needs to be resubmitted to the bot. 
        
        This process will look at the prior submissions and compare the current inventory on the view to the prior submissions to see how many got returned with a null retrieval status. The invoices that were returned with a null retrieval status will be resubmitted to the bot.

        Args:
            query_date (str): date in MM DD YYYY format
        """
        self.query_date = query_date
        self.ccn_type = ccn_type
        if self.ccn_type != 'Electronic' and self.ccn_type != 'Paper':
            logger.critical('Invalid CCN Type')
            exit()
        
        self.path = fr'M:\CPP-Data\Sutherland RPA\Northwell Process Automation ETM Files\Monthly Reports\Charge Correction\New vs Established\ETM Export - {self.ccn_type}'
        
        self.today_df = self.read_today()
        self.min_date = self.get_min_and_max_date()[0]
        self.max_date = self.get_min_and_max_date()[1]
        self.get_min_and_max_date()
        self.not_worked = self.get_unworked_invoice_list()
        self.filter_current_view_for_resubmission()
        self.add_resubmissions_to_current_file()
        
    def read_today(self):
        """
        Reads in the current day's ETM view and returns a dataframe.

        Returns:
            dataframe: dataframe of the current day's ETM view
        """
        logger.info('Reading in today\'s ETM view')

        # reads the electronic and paper etm view and stores in today_df
        today_df = pd.read_excel(f'{self.path}/{self.query_date}.xlsx', skiprows=1, names=mappings.columns, dtype=mappings.dtypes)
        
        # converts the pend date to a date object
        today_df['Pend Date - Due for FU'] = pd.to_datetime(today_df['Pend Date - Due for FU']).dt.date
        return today_df
    
    def get_min_and_max_date(self):
        min_date = (pd.to_datetime(self.query_date) - pd.DateOffset(days=6))
        max_date = pd.to_datetime(self.query_date)
        return min_date, max_date

    def get_unworked_invoice_list(self):
        logger.info('Getting the invoices that were not worked on the prior days outputs')

        # gets the invoices that were not worked on the current day's ETM view
        not_worked = []
        for date in pd.date_range(self.min_date, self.max_date):
            
            year = str(date.year).zfill(2)
            month = str(date.month).zfill(2)
            day = str(date.day).zfill(2)
            output_folder = fr'M:\CPP-Data\Sutherland RPA\ChargeCorrection\{year}\{month} {year}\{month}{day}{year}'

            if os.path.exists(output_folder):
                prev_file = pd.read_excel(f'{output_folder}/Northwell_ChargeCorrection_Output_{month}{day}{year}.xls', usecols=['INVNUM','ActionAddRemoveReplace','RetrievalStatus','RetrievalDescription'])
                # filters the prev_files to remove all C00 from RetrievalStatus
                prev_file = prev_file[prev_file['RetrievalStatus'] != 'C00']
                #keep rows where "ActionAddRemoveReplace" does not contain "Auto"
                prev_file = prev_file[prev_file['ActionAddRemoveReplace'].str.contains('Auto:')]
                
                prev_file['RetrievalStatus'] = prev_file['RetrievalStatus'].fillna('Not Worked')
                
                nw_df = prev_file[prev_file['RetrievalStatus'] == 'Not Worked']
                logger.info(f'{month}/{day}/{year} - {len(nw_df)} not worked')
                not_worked.append(nw_df)
                
        if len(not_worked) > 0:
            not_worked = pd.concat(not_worked)
            not_worked = set(not_worked['INVNUM'])
            return not_worked
        else:
            exit()
                 
    def filter_current_view_for_resubmission(self):
        logger.info('Filtering current view for resubmission')
        self.today_df = self.today_df[self.today_df['Invoice'].isin(self.not_worked)]
        print(self.today_df)
        logger.info(f'{len(self.today_df)} invoices to be resubmitted')

    def add_resubmissions_to_current_file(self):
        logger.info('Adding resubmissions to current file')
        resubmission_data = Raw_File(self.path, self.ccn_type, self.query_date)
        
        
        file_generation_date = get_next_business_day(pd.to_datetime(self.query_date).date())
        logger.debug(file_generation_date)
        
        fgd_spaces = file_generation_date.strftime('%m %d %Y')
        fgd_no_spaces = file_generation_date.strftime('%m%d%Y')
        todays_file = fr'M:\CPP-Data\Sutherland RPA\Northwell Process Automation ETM Files\Monthly Reports\Charge Correction\New vs Established\Formatted Inputs\{fgd_no_spaces}\HCOB16{self.ccn_type} {fgd_spaces}.xlsx'
        
        file_name = f'HCOB16{self.ccn_type} {fgd_spaces}.xlsx'
        
        resubmission_data = resubmission_data.format_output_file(fgd_no_spaces, self.path, file_name, save=False)
        
        # append the resubmissions to the current file
        if os.path.exists(todays_file):
            existing_file = pd.read_excel(todays_file)
            data = pd.concat([existing_file, self.today_df])
            data.drop_duplicates(inplace=True)
            data.to_excel(todays_file, index=False)
            
Resubmission(ccn_type="Electronic", query_date='09 28 2023')