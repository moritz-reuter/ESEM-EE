#%% Packages
import pandas as pd
import os
#%%
### EXCEL ###

def sheet_xl(filename, sheetname):
  # does Excel file exist?
  if not filename or not os.path.isfile(filename):
      raise FileNotFoundError('Excel data file {} not found.'
                              .format(filename))
      
  xls = pd.ExcelFile(filename)
# Einlesen der Inputdaten abhängig vom gewählten Szenario  
  df    = xls.parse(sheetname, delimiter=',', index_col= [1])
  df    = df.dropna(how = 'all').dropna(axis = 1, how = 'all')
  df    = df.rename(columns=df.iloc[0]).drop(df.index[0])

  xls.close()

  return df

