from bulk_combine import RPA_CCN_Bulk_Combine
from file import Raw_File

if __name__ == '__main__':
    for ccn_type in ['Electronic', 'Paper']:
        RPA_CCN_Bulk_Combine(ccn_type=ccn_type)
