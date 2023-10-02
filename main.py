from bulk_combine import RPA_CCN_Bulk_Combine
from file import Raw_File
# from resubmission import Resubmission

if __name__ == '__main__':
    RPA_CCN_Bulk_Combine(ccn_type="Electronic", query_date='09 29 2023')
    RPA_CCN_Bulk_Combine(ccn_type="Paper", query_date='09 29 2023')

    # Resubmission(ccn_type="Electronic", query_date='09 29 2023')
    # Resubmission(ccn_type="Paper", query_date='09 29 2023')
