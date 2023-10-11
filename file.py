#file.py

import os
from glob import glob

import pandas as pd

import util.mappings as mappings
from util.logger_config import logger
from util.utilitiy_functions import (replace_new_pt_cpts,
                                     replace_non_accepted_cpts)
from util.date_functions import get_next_business_day


class Raw_File():

    def __init__(self, source_path: str, ccn_type: str, query_date: str = None, file_generation_date: str = None):
        self.source_path = source_path
        self.ccn_type = ccn_type
        
        self.query_date = query_date
        if file_generation_date:
            self.file_generation_date = file_generation_date
        else:
            self.file_generation_date = get_next_business_day(pd.to_datetime(self.query_date)).strftime('%Y-%m-%d')
        
        self.template = pd.read_excel('./references/ccn_template.xlsx')
        
        self.file_data = self.read_data()
        self.file_data = self.format_output_file()

    
    def read_data(self):
        logger.debug('reading data')
        if os.path.exists(self.source_path):
            file_data = pd.read_excel(self.source_path, skiprows=1, names=mappings.columns, dtype=mappings.dtypes, usecols=range(14))
            file_data['Max New Pt Rejection'] = pd.to_datetime(file_data['Max New Pt Rejection']).dt.date
            file_data['Pend Date - Due for FU'] = pd.to_datetime(file_data['Pend Date - Due for FU']).dt.date
            
            # convert 'Pend Date - Due for FU' column to date
            file_data['Pend Date - Due for FU'] = pd.to_datetime(file_data['Pend Date - Due for FU']).dt.date

            file_data = self.filter_data_for_output(file_data)
            logger.success('data read and filtered')            

        
            return file_data
        else:
            logger.critical('File does not exist')
    
    def filter_data_for_output(self, file_data: pd.DataFrame):
        
        logger.debug('filtering data')
        # Only include ones that were pended by the auto process
        file_data = file_data[file_data['ETM Status'] == 'Hold-RPA Charge Correction']
        
        # filter file_data on Outsource Tag column to remove rows where the Outsource Tag begins with IK, RC, RB, or AP
        file_data['Outsource Tag'].fillna('', inplace=True)
        tags_to_exclude = ['AP', 'IK', 'RB', 'RC']
        
        filter_criteria = []


        # Append criteria based on 'Outsource Tag'
        filter_criteria.append(~file_data['Outsource Tag'].str.startswith(tuple(tags_to_exclude)))

        # Append criteria based on 'Invoice Balance'
        filter_criteria.append(file_data['Invoice Balance'] >= 304)

        # Append criteria based on 'Patient Responsibility'
        filter_criteria.append(file_data['Patient Responsibility'] != file_data['Invoice Balance'])

        # Check if the ccn_type is 'Paper' and append criteria accordingly
        if self.ccn_type == 'Paper':
            filter_criteria.append(file_data['FSC'].str.startswith(tuple(['MCAR', 'MCGH', 'MCRR'])))
            # Append criteria based on 'CPT List'
            filter_criteria.append(file_data['CPT List'].str.contains(',') == False)

        # Combine all filtering criteria using the logical AND operator
        combined_criteria = pd.Series(True, index=file_data.index)
        for criterion in filter_criteria:
            # Apply the combined criteria to filter the data
            combined_criteria = combined_criteria & criterion

        submitted_data = (file_data[combined_criteria]).reset_index()
        removed_data = (file_data[~combined_criteria]).reset_index()
        
        # fill in the blank TCN values with 'NA'
        submitted_data['TCN'] = submitted_data['TCN'].fillna('NA')
        
        # add "CLM" prefix to all TCN values
        submitted_data['TCN'] = 'CLM' + submitted_data['TCN'].astype(str)
        
        return submitted_data
    
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
            if not os.path.exists(f'{save_location}/{file_generation_date}/{file_name}'):
                self.template.to_excel(f'{save_location}/{file_generation_date}/{file_name}', index=None)
                logger.success(f'file saved to {save_location}/{file_generation_date}/{file_name}')
            else:
                logger.info(f'appending to existing file {save_location}/{file_generation_date}/{file_name}')
                existing_file = pd.read_excel(f'{save_location}/{file_generation_date}/{file_name}')
                data = pd.concat([existing_file, self.template])
                data = data.drop_duplicates()
                data.to_excel(f'{save_location}/{file_generation_date}/{file_name}', index=None)
                logger.success(f'file saved to {save_location}/{file_generation_date}/{file_name}')
        else:
            return self.template  