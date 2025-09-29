"""
Excel file reader utility.
"""

import pandas as pd


def read_excel(filename, sheet_name, skiprows):
    """Read an Excel sheet with optional skipped rows."""
    return pd.read_excel(filename, sheet_name=sheet_name, skiprows=skiprows)
