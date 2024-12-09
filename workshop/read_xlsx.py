import pandas as pd

def read_excel_sheet_cell(filename, sheet, row, col):
     return pd.read_excel(filename, sheet).iat[row, col]

def read_excel_sheet_columns(filename, sheet):
    return pd.read_excel(filename, sheet).columns

def read_excel_sheet_index(filename, sheet):
    return pd.read_excel(filename, sheet).index

def read_excel_sheet_row(filename, sheet, row):
    return pd.read_excel(filename, sheet).loc[row]

def read_excel_sheet_col(filename, sheet, col):
    return pd.read_excel(filename, sheet).get(col)
