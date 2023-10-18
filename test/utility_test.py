import os
import sys
import pandas as pd

# Add the path to the directory containing date_functions to the PYTHONPATH environment variable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'util')))

from utilitiy_functions import replace_new_pt_cpts, replace_non_accepted_cpts

def test_replace_new_pt_cpts():
    # one code
    assert replace_new_pt_cpts('99203|||') == "99213|||"
    # two codes
    assert replace_new_pt_cpts('99386|99203|') == '99396|99213|'