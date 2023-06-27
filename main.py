import configparser
import pandas as pd
from tkinter import filedialog as fd


class Bulk_File():
    def __init__(self, file: str, output_location:str):
        self.file = file
        self.template = pd.read_excel('./resources/ccn_form.xlsx', header=0)
        self.accepted_fscs = pd.read_excel(
            'M:/CPP-Data/Sutherland RPA/Northwell Process Automation ETM Files/Monthly Reports/Charge Correction/References/FSCs that accept electronic CCL.xlsx')
        self.columns = [
            'BAR_B_INV.INV_NUM',
            'BAR_B_INV.FSC__5',
            'BAR_B_INV.TOT_CHG',
            'BAR_B_INV.INV_BAL',
            'PROC__2',
            'BAR_B_TXN.U_CPTCODE_LIST',
            'BAR_B_INV.REJ_REF_NUM',
            'BAR_B_TXN_LI_PAY.POST_DT'
        ]
        self.dtypes = {
            'BAR_B_INV.GRP__2': int,
            'BAR_B_INV.INV_NUM': int,
            'BAR_B_INV.TOT_CHG': float,
            'BAR_B_INV.INV_BAL': float,
            'PROC__2': str,
            'BAR_B_TXN.U_CPTCODE_LIST': str,
            'BAR_B_INV.REJ_REF_NUM': str,
        }

        self.crosswalk = {
            '99202': '99212',
            '99203': '99213',
            '99204': '99214',
            '99205': '99215',
            '92002': '92012',
            '92004': '92014',
            '99381': '99391',
            '99382': '99392',
            '99383': '99393',
            '99384': '99394',
            '99385': '99395',
            '99386': '99396',
            '99387': '99397'
        }
        self.data = self.read_file()
        self.column_mappings = {
            'Invoice': 'BAR_B_INV.INV_NUM',
            'ClaimReferenceNumber': 'BAR_B_INV.REJ_REF_NUM',
            'InvoiceBalance': 'BAR_B_INV.INV_BAL',
            'Insurance': 'BAR_B_INV.FSC__5',
            'OriginalCPT': 'Original CPT List',
            'NewCPT': 'New CPT List',
            'ActionAddRemoveReplace': 'Comment',
            'Reason': 'Reason',
            'STEP': 'Step'
        }
        self.formatted_file = self.format_file(self.data)
        self.formatted_file.to_excel(output_location, index=False)        

    def replace_non_accepted_cpts(self, data: pd.DataFrame):
        return "|".join([cpt if cpt in self.crosswalk.keys() else '' for cpt in data.split('|')])

    def replace_new_pt_cpts(self, data: pd.DataFrame):
        return "|".join([self.crosswalk[cpt] if cpt in self.crosswalk.keys() else '' for cpt in data.split('|')])

    def read_file(self):
        data = pd.read_csv(self.file, sep='\t', header=None,
                           names=self.columns, dtype=self.dtypes, parse_dates=['BAR_B_TXN_LI_PAY.POST_DT'])
        return data

    def format_file(self, data: pd.DataFrame):
        # Formats the CPT List column to only display the new patient codes
        data['Original CPT List'] = data['BAR_B_TXN.U_CPTCODE_LIST'].apply(
            lambda x: self.replace_non_accepted_cpts(x))

        # copies the original CPT List column and replaces the new patient codes with the old patient codes
        data['New CPT List'] = data['Original CPT List'].copy()
        data['New CPT List'] = data['New CPT List'].apply(
            lambda x: self.replace_new_pt_cpts(x))

        # filter out FSCs that do not accept electronic CCL
        data = data[data['BAR_B_INV.FSC__5'].isin(self.accepted_fscs['FSC'])]
        data = data.reset_index()

        # append "CLM" at the start of every "BAR_B_INV.REJ_REF_NUM" value
        data['BAR_B_INV.REJ_REF_NUM'] = data['BAR_B_INV.REJ_REF_NUM'].apply(
            lambda x: 'CLM' + str(x))

        data['BAR_B_INV.REJ_REF_NUM'] = data['BAR_B_INV.REJ_REF_NUM'].replace(
            'CLMnan', 'CLMNA')

        # populate "2" if the balance = totchg else populate "3" for all else
        data['Step'] = data.apply(
            lambda x: '2' if x['BAR_B_INV.INV_BAL'] == x['BAR_B_INV.TOT_CHG'] else '3', axis=1)

        data['Reason'] = '1'
        data['Comment'] = 'Auto: New to Established'

        data = data.drop_duplicates()

        # Iterate through the crosswalk
        for template_column, data_column in self.column_mappings.items():
            self.template[template_column] = data[data_column]
            
        self.template['Data'] = "Northwell"
        return self.template

if __name__ == '__main__':

    config = configparser.ConfigParser()
    config.read('./config/config.ini')

    root = config['DEFAULT']['QUERY_LOCATION']
    output_location = config['DEFAULT']['FORMATTED_INPUT_LOCATION']
    date_format = config['DEFAULT']['OUTPUT_DATE_FORMAT']
    title = config['GUI']['WINDOW_TITLE']
    width = int(config['GUI']['WINDOW_WIDTH'])
    height = int(config['GUI']['WINDOW_HEIGHT'])

    file = fd.askopenfilename(defaultextension='.txt', filetypes=[
                              ('txt', '*.txt')], initialdir=root)
    
    # extract date from file
    date = file.split('/')[-1].split('.')[0]
    # remove spaces from date
    date = date.replace(' ', '')
    output_location = f'{output_location}/{date}.xlsx'
    
    Bulk_File(file, output_location)
