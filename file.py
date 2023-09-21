import pandas as pd
import util.mappings as mappings
from util.utilitiy_functions import replace_non_accepted_cpts, replace_new_pt_cpts
from util.logger_config import logger
import os

class Raw_File():

    def __init__(self, source_path: str):
        self.source_path = source_path
        
        self.template = pd.read_excel('./references/ccn_template.xlsx')
        
        self.file_data = self.read_data()
        self.file_data = self.format_output_file()
    
    def read_data(self):
        logger.debug('reading data')
        if os.path.exists(self.source_path):
            file_data = pd.read_excel(self.source_path, skiprows=1, names=mappings.columns, dtype=mappings.dtypes, parse_dates=['Max New Pt Rejection', 'Pend Date - Due for FU'])

            file_data = self.filter_data(file_data)
            logger.success('data read and filtered')            

            return file_data
        else:
            logger.critical('File does not exist')
    
    def filter_data(self, file_data: pd.DataFrame):
        logger.debug('filtering data')
        # EXCLUSIONS AS OF 9/20/2023
        # remove vendor inventory
        # remove balance < 304
        file_data['Outsource Tag'].fillna('', inplace=True)

        # filter file_data on Outsource Tag column to remove rows where the Outsource Tag begins with IK, RC, IK, RB, or AP
        tags_to_exclude = ['AP', 'IK', 'RB', 'RC']
        file_data = file_data[~file_data['Outsource Tag'].str.startswith(
            tuple(tags_to_exclude))]
        file_data = file_data[file_data['Invoice Balance'] >= 304]
        
        # remove MCAD
        file_data = file_data[~file_data['FSC'].str.startswith('MCAD')]
        
        # remove any lines where the patient responsibility is = to the balance
        file_data = file_data[file_data['Patient Responsibility'] != file_data['Invoice Balance']]
        
        # remove any lines where the etm status contains charge correction
        file_data = file_data[~file_data['ETM Status'].str.contains('Charge Correction')]
        
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
        return file_data
        
    def generate_output(self, file_generation_date: str, save_location: str, file_name: str):
        logger.debug('generating output')
        for template_column, data_column in mappings.column_mappings.items():
            self.template[template_column] = self.file_data[data_column]
        self.template['Data'] = "Northwell"
        
        if not os.path.exists(f'{save_location}/{file_generation_date}'):
            logger.info(f'creating directory {save_location}/{file_generation_date}')
            os.makedirs(f'{save_location}/{file_generation_date}')
        
        self.template.to_excel(f'{save_location}/{file_generation_date}/{file_name}', index=None)
        logger.success(f'file saved to {save_location}/{file_generation_date}/{file_name}')    