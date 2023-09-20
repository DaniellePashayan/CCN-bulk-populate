column_mappings = {
    "Invoice": "BAR_B_INV.INV_NUM",
    "ClaimReferenceNumber": "BAR_B_INV.REJ_REF_NUM",
    "InvoiceBalance": "BAR_B_INV.INV_BAL",
    "Insurance": "BAR_B_INV.FSC__5",
    "OriginalCPT": "Original CPT List",
    "NewCPT": "New CPT List",
    "ActionAddRemoveReplace": "Comment",
    "Reason": "Reason",
    "STEP": "Step"
}

cpt_crosswalk = {
    # outpatient / office visits
    "99202": "99212",
    "99203": "99213",
    "99204": "99214",
    "99205": "99215",
    # preventative medicine
    "99381": "99391",
    "99382": "99392",
    "99383": "99393",
    "99384": "99394",
    "99385": "99395",
    "99386": "99396",
    "99387": "99397",
    # home health - deactivated 1/1/2023
    "99324": "99334",
    "99325": "99335",
    "99326": "99336",
    "99327": "99337",
    "99328": "99337",
    # home health - activated 7/1/2023
    "99341": "99347",
    "99342": "99348",
    "99344": "99350",
    "99345": "99350",
    # opthamology
    "92002": "92012",
    "92004": "92014"
}

columns = [
    'Task',
    'Invoice',
    'FSC',
    'Tot Chg',
    'Invoice Balance',
    'New Visit CPTs',
    'CPT List',
    'TCN',
    'Max New Pt Rejection',
    'Outsource Tag'
]

dtypes = {
    'Task' : str,
    'Invoice': int,
    'FSC': str,
    'Tot Chg': float,
    'Invoice Balance': float,
    'New Visit CPTs': str,
    'CPT List': str,
    'TCN': str,
    # 'Max New Pt Rejection',
    'Outsource Tag': str
}