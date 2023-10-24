# import mappings
try:
    import util.mappings as mappings
    from util.logger_config import logger
except ModuleNotFoundError:
    import mappings
    from logger_config import logger

def replace_non_accepted_cpts(CPT_List: str) -> str:
    """CPT list is delimited by a pipe. CPTs appear in the list in the same order they appear by txn_num. This function uses the cpt_mappings crosswalk. Any codes not in the crosswalk are replaced by an empty string, leaving only the new patient CPT code in the correct position.

    Args:
        CPT_List (str): CPT list from query (ex: 99203|36415|76817)

    Returns:
        str: CPT list only containing the CPT that needs to be changed (ex: 99203||)
    """
    # original cpt list from etm view is delimited by a comma
    return "|".join([cpt if cpt in mappings.cpt_crosswalk.keys() else '' for cpt in CPT_List.split(',')])

def replace_new_pt_cpts(Parsed_CPT_List: str)->str:
    """Takes the parsed CPT list and changes the new patient CPT code and replaces with the established CPT code while preserving the structure/formatting.

    Args:
        Parsed_CPT_List (str): CPT list, delimited by a pipe, where all non-new patient CPT codes have been replaced by an empty string (ex: 99203||)

    Returns:
        str: CPT list, delimited by a pipe, where the new patient cpt has been changed to the established patient cpt (ex: 99213||)
    """
    return "|".join([mappings.cpt_crosswalk[cpt] if cpt in mappings.cpt_crosswalk.keys() else '' for cpt in Parsed_CPT_List.split(',')])