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
# - Frankel and Rose criterion
th1 = 30 # depreciation rate y/y
th2 = 10 # percentage points higher than the rate of depreciation observed in the previous year

# - Exchange Market Pressure Index
num_std = 2 # number of standard deviations above EMP mean


#_________________________________________________________________________________
# ___ DATA
#_________________________________________________________________________________
# ___ Import data
# Frankel and Rose criterion     -> Nominal exchange rate (base value USD) : 2 datasets (IFS and datastream for complements)
# Exchange Market Pressure Index -> International reserves : 1 dataset (IFS)
#                                -> Policy rate (annual %) : 2 datasets (IFS and datastream for complements)
mod_path = Path(__file__).parent

exr      = pd.read_excel(cld.relative_path(mod_path, '../data/raw_data/IMF', 'IFS_base_quarters.xlsx')   , sheet_name='EXR')
res      = pd.read_excel(cld.relative_path(mod_path, '../data/raw_data/IMF', 'IFS_base_quarters.xlsx')   , sheet_name='RES_FX')
prate    = pd.read_excel(cld.relative_path(mod_path, '../data/raw_data/IMF', 'IFS_base_quarters.xlsx')   , sheet_name='PRATE')
exr_c    = pd.read_excel(cld.relative_path(mod_path, '../data/raw_data/datastream', 'DS_GLOBAL_add.xlsx'), sheet_name='EXR')
prate_cq = pd.read_excel(cld.relative_path(mod_path, '../data/raw_data/datastream', 'DS_GLOBAL_add.xlsx'), sheet_name='PRATE_q')
prate_cy = pd.read_excel(cld.relative_path(mod_path, '../data/raw_data/datastream', 'DS_GLOBAL_add.xlsx'), sheet_name='PRATE_y')
euro_mb  = pd.read_excel(cld.relative_path(mod_path, '../data/raw_data/others', 'OT_euro_countries.xlsx'))


# ___ Clean data
exr      = cld.clean_IFS(exr    , 'EXR')
res      = cld.clean_IFS(res    , 'RES')
prate    = cld.clean_IFS(prate  , 'PRATE')
exr_c    = cld.clean_DS(exr_c   , 'EXR')
prate_cq = cld.clean_DS(prate_cq, 'PRATE')
prate_cy = cld.clean_DS(prate_cy, 'PRATE')


# ___ Complete data
# - Exchange rate
exr = pd.merge(exr, exr_c, how='left', on=['ISO', 'YEAR'])
exr["EXR_x"] = np.where(exr["EXR_x"].isnull(), exr["EXR_y"], exr["EXR_x"])
exr.drop(labels='EXR_y', axis=1, inplace=True)
exr = exr.rename(columns = {'EXR_x': 'EXR'})

# - Policy rate (2 merge: DS quarterly and DS annual)
prate =  pd.merge(prate, prate_cq, how='left', on=['ISO', 'YEAR'])
prate["PRATE_x"] = np.where(prate["PRATE_x"].isnull(), prate["PRATE_y"], prate["PRATE_x"])
prate.drop(labels='PRATE_y', axis=1, inplace=True)
prate = prate.rename(columns = {'PRATE_x': 'PRATE'})

prate =  pd.merge(prate, prate_cy, how='left', on=['ISO', 'YEAR'])
prate["PRATE_x"] = np.where(prate["PRATE_x"].isnull(), prate["PRATE_y"], prate["PRATE_x"])
prate.drop(labels='PRATE_y', axis=1, inplace=True)
prate = prate.rename(columns = {'PRATE_x': 'PRATE'})


# ___ Working bases (FR : Frankel and Rose, EMP : Exchange Market Pressure Index)
base_FR  = exr
base_EMP = exr.merge(res       , left_index=True, right_on=['ISO', 'YEAR'])
base_EMP = base_EMP.merge(prate, left_index=True, right_on=['ISO', 'YEAR'])


# ___ Fill NA
base_FR  = base_FR.groupby('ISO').apply(cld.fillna_downbet, p=4)
base_EMP = base_EMP.groupby('ISO').apply(cld.fillna_downbet, p=4)


#_________________________________________________________________________________
# ___ CRISIS CRITERIA
#_________________________________________________________________________________
# ___ Frankel and Rose criterion
base_FR = base_FR.assign(EXR_g = base_FR.groupby(level='ISO')['EXR'].pct_change(4)*100)
base_FR.loc[base_FR['EXR'].isna(), 'EXR_g'] = np.nan
base_FR = base_FR.assign(EXR_d = base_FR.groupby(level='ISO')['EXR_g'].diff(4))
base_FR.loc[base_FR['EXR_g'].isna(), 'EXR_d'] = np.nan
base_FR = base_FR.assign(crisis_FR = 0)
base_FR.loc[base_FR['EXR_d'].isna(), 'crisis_FR'] = np.nan
base_FR.loc[(base_FR['EXR_g'] >= th1) & (base_FR['EXR_d'] >= th2), 'crisis_FR'] = 1


# ___ Exchange Market Pressure Index
# - Weights
EXR_w   = base_EMP.groupby(level='ISO')['EXR'].expanding().std()
RES_w   = base_EMP.groupby(level='ISO')['RES'].expanding().std()
PRATE_w = base_EMP.groupby(level='ISO')['PRATE'].expanding().std()

EXR_w   = pd.DataFrame(EXR_w.droplevel(1))
RES_w   = pd.DataFrame(RES_w.droplevel(1))
PRATE_w = pd.DataFrame(PRATE_w.droplevel(1))

EXR_w   = EXR_w.rename(columns   = {'EXR'  : 'EXR_w'})
RES_w   = RES_w.rename(columns   = {'RES'  : 'RES_w'})
PRATE_w = PRATE_w.rename(columns = {'PRATE': 'PRATE_w'})

base_EMP = base_EMP.merge(EXR_w,   left_index=True, right_on=['ISO', 'YEAR'])
base_EMP = base_EMP.merge(RES_w,   left_index=True, right_on=['ISO', 'YEAR'])
base_EMP = base_EMP.merge(PRATE_w, left_index=True, right_on=['ISO', 'YEAR'])

base_EMP.loc[base_EMP['EXR'].isna(), 'EXR_w']     = np.nan
base_EMP.loc[base_EMP['RES'].isna(), 'RES_w']     = np.nan
base_EMP.loc[base_EMP['PRATE'].isna(), 'PRATE_w'] = np.nan

# - EMP properties
base_EMP['EMP'] = base_EMP['EXR'] * (1/base_EMP['EXR_w']) - base_EMP['RES'] * (1/base_EMP['RES_w']) + base_EMP['PRATE'] * (1/base_EMP['PRATE_w'])
base_EMP['EMP'] = base_EMP['EMP'].replace([np.inf, -np.inf], np.nan)

EMP_std  = base_EMP.groupby(level='ISO')['EMP'].expanding().std()
EMP_mean = base_EMP.groupby(level='ISO')['EMP'].expanding().mean()
EMP_std  = pd.DataFrame(EMP_std.droplevel(1))
EMP_mean = pd.DataFrame(EMP_mean.droplevel(1))
EMP_std  = EMP_std.rename(columns  = {'EMP': 'EMP_std'})
EMP_mean = EMP_mean.rename(columns = {'EMP': 'EMP_mean'})
base_EMP = base_EMP.merge(EMP_std,  left_index=True, right_on=['ISO', 'YEAR'])
base_EMP = base_EMP.merge(EMP_mean, left_index=True, right_on=['ISO', 'YEAR'])
base_EMP.loc[base_EMP['EMP'].isna(),'EMP_std']  = np.nan
base_EMP.loc[base_EMP['EMP'].isna(),'EMP_mean'] = np.nan

# - Threshold
base_EMP['threshold'] = base_EMP['EMP_mean'] + num_std * base_EMP['EMP_std']
base_EMP = base_EMP.assign(crisis_EMP = 0)
base_EMP.loc[base_EMP['threshold'].isna(), 'crisis_EMP'] = np.nan
base_EMP.loc[base_EMP['EMP'] >= base_EMP['threshold'], 'crisis_EMP'] = 1


#_________________________________________________________________________________
# ___ EUROZONE
#_________________________________________________________________________________
# Exchange rate are not reported for countries that have joined the euro area (from their entry into the monetary union)
# in the IFS file. Assignment of the value of the euro area currency crisis criterion (iso=EUZ) to member countries.

base_FR['Y'] = base_FR.index.get_level_values(1).str[:4]
base_FR['Y'] = pd.to_numeric(base_FR['Y'])

base_EMP['Y'] = base_EMP.index.get_level_values(1).str[:4]
base_EMP['Y'] = pd.to_numeric(base_EMP['Y'])

base_FR  = base_FR.groupby(['ISO']).apply(cld.fill_euro , df_w=base_FR , euro_mb=euro_mb, col_val='crisis_FR' , col_year='Y')
base_EMP = base_EMP.groupby(['ISO']).apply(cld.fill_euro, df_w=base_EMP, euro_mb=euro_mb, col_val='crisis_EMP', col_year='Y')


#_________________________________________________________________________________
# ___ FINAL FILE
#_________________________________________________________________________________
base = pd.merge(base_FR, base_EMP, on = ['ISO', 'YEAR'], how = 'outer')
base = base.drop(['EXR_y', 'RES', 'PRATE','EXR_w',
                  'RES_w', 'PRATE_w', 'EMP', 'EMP_std',
                  'EMP_mean', 'threshold', 'Y_x', 'Y_y',
                  'EXR_x', 'EXR_g', 'EXR_d'
                  ], axis=1)

base.to_csv('currency_crises.csv', sep=';')
