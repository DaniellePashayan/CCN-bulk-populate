import pandas as pd
from glob import glob
import util.mappings as mappings
from util.utilitiy_functions import replace_non_accepted_cpts, replace_new_pt_cpts
from util.logger_config import logger
import os

class Raw_File():

    def __init__(self, source_path: str, ccn_type: str, query_date: str):
        self.source_path = source_path
        self.ccn_type = ccn_type
        self.query_date = query_date
        
        self.template = pd.read_excel('./references/ccn_template.xlsx')
        
        self.file_data = self.read_data()
        self.file_data = self.format_output_file()
    
    def read_data(self):
        logger.debug('reading data')
        if os.path.exists(self.source_path):
            file_data = pd.read_excel(self.source_path, skiprows=1, names=mappings.columns, dtype=mappings.dtypes, parse_dates=['Max New Pt Rejection', 'Pend Date - Due for FU'])
            
            # convert 'Pend Date - Due for FU' column to date
            file_data['Pend Date - Due for FU'] = pd.to_datetime(file_data['Pend Date - Due for FU']).dt.date

            file_data = self.filter_data_for_output(file_data)
            logger.success('data read and filtered')            

            return file_data
        else:
            logger.critical('File does not exist')
    
    def filter_data_for_output(self, file_data: pd.DataFrame):
        logger.debug('filtering data')
        # EXCLUSIONS AS OF 9/20/2023
        # remove vendor inventory
        # remove balance < 304
        
        # review date is the query date + 6 days
        review_date = (pd.to_datetime(self.query_date) + pd.Timedelta(days=6)).date()
        # anything with a review date of less than 6 days means it appeared on the report before the query date
        file_data = file_data[file_data['Pend Date - Due for FU'] == review_date].reset_index()
        
        # filter file_data on Outsource Tag column to remove rows where the Outsource Tag begins with IK, RC, RB, or AP
        file_data['Outsource Tag'].fillna('', inplace=True)
        tags_to_exclude = ['AP', 'IK', 'RB', 'RC']
        file_data = file_data[~file_data['Outsource Tag'].str.startswith(
            tuple(tags_to_exclude))]
        file_data = file_data[file_data['Invoice Balance'] >= 304]
        
        if self.ccn_type == 'Paper':
            file_data = file_data[file_data['FSC'].str.startswith(tuple(['MCAR', 'MCGH']))]
            # filter to remove any lines wwhere there is more than 1 CPT code in the CPT list
            file_data = file_data[file_data['CPT List'].str.contains(',') == False]
        
        # remove any lines where the patient responsibility is = to the balance
        file_data = file_data[file_data['Patient Responsibility'] != file_data['Invoice Balance']]

        # fill in the blank TCN values with 'NA'
        file_data['TCN'] = file_data['TCN'].fillna('NA')
        
        # add "CLM" prefix to all TCN values
        file_data['TCN'] = 'CLM' + file_data['TCN'].astype(str)
        return file_data
    
    def format_output_file(self):
        logger.debug('formatting output file')
        # drop rows where invoice number is blank
        file_data = self.file_data.dropna(subset=['Invoice'])
        file_data['CPT List'] = file_data['CPT List'].replace(', ', ',', regex=True)
        
        #iterate through the rows to get the value of the CPTlist column
        file_data['Original CPT List'] = file_data['CPT List'].apply(lambda x: replace_non_accepted_cpts(x))
        
        # copy the original CPT list and then use the crosswalk to change the CPT codes
        file_data['New CPT List'] = file_data['CPT List'].apply(lambda x: replace_new_pt_cpts(x))

        # populate "2" if the balance = totchg else populate "3" for all else
        file_data['Step'] = file_data.apply(lambda x: '2' if x['Invoice Balance'] == x['Tot Chg'] else '3', axis=1)
        file_data['Reason'] = '1'
        file_data['Comment'] = 'Auto: New to Established'
        file_data = file_data.drop_duplicates()
        # get the number of rows in the dataframe
        logger.info(f'{file_data.shape[0]} on view after filter')
        
        return file_data
    
    def read_last_six_days(self):
        folder = r'M:\CPP-Data\Sutherland RPA\Northwell Process Automation ETM Files\Monthly Reports\Charge Correction\New vs Established\Formatted Inputs'
        before_filter_shape = self.file_data.shape[0]
        before_filter = self.file_data.copy()
        invoices_before_filter = set(before_filter['Invoice'].unique())
        logger.debug(len(invoices_before_filter))
        
        # get all the files in folder if the creation date is within the last 6 days from self.query_date (excludes current date)
        prev_files = [f for f in glob(f'{folder}/*/*.xlsx') if pd.to_datetime(os.path.getctime(f),  unit='s') > pd.to_datetime(self.query_date) - pd.Timedelta(days=6)]
        prev_files = pd.concat([pd.read_excel(f) for f in prev_files])
        
        # filter out rows from self.file_data if the invoice appears in prev_files
        self.file_data = self.file_data[~self.file_data['Invoice'].isin(prev_files['Invoice'])]
        
        invoices_after_filter = set(self.file_data['Invoice'].unique())
        logger.debug(len(invoices_after_filter))
        logger.info(f'{(len(invoices_before_filter) - len(invoices_after_filter))} invoices removed (already sent to bot within last 6 days)')    
        
        logger.debug(f'invoices removed: \n{(invoices_before_filter - invoices_after_filter)}')
          
        logger.success(f'{self.file_data.shape[0]} invoices sent to bot')

    
    def generate_output(self, file_generation_date: str, save_location: str, file_name: str, save = True):
        files = self.read_last_six_days()
        logger.debug('generating output')
        for template_column, data_column in mappings.column_mappings.items():
            self.template[template_column] = self.file_data[data_column]
        self.template['Data'] = "Northwell"
        
        if not os.path.exists(f'{save_location}/{file_generation_date}'):
            logger.info(f'creating directory {save_location}/{file_generation_date}')
            os.makedirs(f'{save_location}/{file_generation_date}')
        
        if save:
            self.template.to_excel(f'{save_location}/{file_generation_date}/{file_name}', index=None)
            logger.success(f'file saved to {save_location}/{file_generation_date}/{file_name}')  
        else:
            return self.template  