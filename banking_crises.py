#_________________________________________________________________________________
#___ LIBRARIES 
#_________________________________________________________________________________
import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(os.path.abspath("__file__")), '../utils'))
import clean_dataset as cld


#_________________________________________________________________________________
# ___ PARAMETERS
#_________________________________________________________________________________
# - Baron, Verner and Xiong
th = 30 # "bank equity crash": annual bank equity decline in %, or cumulative since the last peak of return

#_________________________________________________________________________________
# ___ DATA
#_________________________________________________________________________________
# ___ Import data
mod_path = Path(__file__).parent
stocks   = pd.read_excel(cld.relative_path(mod_path, '../data/raw_data/datastream', 'DS_GLOBAL_add.xlsx')   , sheet_name='BANK_STOCKS')

# ___ Clean data
stocks   = cld.clean_DS(stocks, 'STOCKS')

# ___ Fill NA
stocks  = stocks.groupby('ISO').apply(cld.fillna_downbet, p=1)


#_________________________________________________________________________________
# ___ CRISIS CRITERION
#_________________________________________________________________________________
# ___ Annual declines
stocks['RETURN'] = stocks.groupby('ISO').pct_change(periods=1)*100
stocks.loc[stocks['STOCKS'].isna(), 'RETURN'] = np.nan

stocks['ANNUAL'] = 0
stocks.loc[stocks['RETURN'].isna(), 'ANNUAL'] = np.nan
stocks.loc[stocks['RETURN'] <= -th, 'ANNUAL']  = 1


# ___ Cumulative declines (encompasses annual declines above threshold)
stocks['PEAK'] = 0
stocks.loc[stocks['STOCKS'].isna(), 'PEAK'] = np.nan
stocks.loc[(stocks.STOCKS.shift(1) < stocks.STOCKS) & (stocks.STOCKS.shift(-1) < stocks.STOCKS), 'PEAK'] = 1


stocks['CUMUL_RET'] = 0
stocks.loc[stocks['RETURN'].isna(), 'CUMUL_RET'] = np.nan

iso = np.unique(stocks.index.get_level_values('ISO'))

for i in iso:
    df     = stocks[stocks.index.get_level_values('ISO') == i]
    colsum = df.PEAK. sum()

    if colsum > 0 :
        df['CUMSUM'] = df['PEAK'].cumsum()

        # Case 1 : peak before
        temp = df.loc[df['PEAK'] == 1, ['STOCKS','CUMSUM']]
        temp = temp.reset_index(level=1, drop=True)
        idx  = df.index
        df   = pd.merge(df, temp, on = ['CUMSUM', 'CUMSUM'], how = 'left')
        df.index = idx
        df  = df.rename(columns  = {'STOCKS_x': 'STOCKS', 'STOCKS_y': 'STOCKS_lag'})

        # Case 2 : peak
        temp['CUMSUM'] = temp['CUMSUM']+1
        df = pd.merge(df, temp, on = ['CUMSUM', 'CUMSUM'], how = 'left')
        df = df.rename(columns  = {'STOCKS_x': 'STOCKS', 'STOCKS_y': 'STOCKS_lag_peak'})
        df.loc[df['PEAK'] == 1, 'STOCKS_lag'] = df.loc[df['PEAK'] == 1, 'STOCKS_lag_peak']
        df.index = idx
        
        df['CUMUL_RET'] = (df['STOCKS']/df['STOCKS_lag']-1)*100
        
        # Case 3 : first peak
        #df['CUMUL_RET'][df['PEAK'] ==1].iloc[0] = df['RETURN'][df['PEAK'] ==1].iloc[0]
        df.loc[df[df['PEAK'] ==1].index[0], 'CUMUL_RET'] = df['RETURN'][df['PEAK'] ==1].iloc[0]

        # Case 4 : no peak before
        df.loc[df['CUMSUM'] == 0, 'CUMUL_RET'] = df.loc[df['CUMSUM'] == 0, 'RETURN']
        
    else:
        df['CUMUL_RET'] = df['RETURN']

    stocks.loc[stocks.index.get_level_values('ISO') == i, 'CUMUL_RET'] = df['CUMUL_RET']
    
stocks['CUMUL'] = 0
stocks.loc[stocks['CUMUL_RET'].isna(), 'CUMUL'] = np.nan
stocks.loc[stocks['CUMUL_RET'] <= -th, 'CUMUL']  = 1


#_________________________________________________________________________________
# ___ FINAL FILE
#_________________________________________________________________________________
stocks = stocks.drop(['STOCKS', 'RETURN', 'ANNUAL','PEAK', 'CUMUL_RET'], axis=1)
stocks = stocks.rename(columns  = {'CUMUL': 'BANKING_CRISIS'})

stocks.to_csv('banking_crises.csv', sep=';')
