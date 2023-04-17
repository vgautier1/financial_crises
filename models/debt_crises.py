#_________________________________________________________________________________
#___ LIBRARIES 
#_________________________________________________________________________________
import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(os.path.abspath("__file__")), '../../utils'))
import clean_dataset as cld


#_________________________________________________________________________________
# ___ DATA
#_________________________________________________________________________________
# ___ Import data
# GDP at current prices (USD) : 2 datasets (WEO and datastream for complements)
# Sovereign debt : 1 dataset (BoE-BoC dating)

mod_path = Path(__file__).parent

gdp   = pd.read_excel(cld.relative_path(mod_path, '../data/raw_data/IMF', 'WEO_GDP_current_USD.xlsx'))
gdp_c = pd.read_excel(cld.relative_path(mod_path, '../data/raw_data/datastream', 'DS_GLOBAL_add.xlsx'), sheet_name='GDP_CUR_USD_y')
debt  = pd.read_excel(cld.relative_path(mod_path, '../data/financial_crises/clean_databases', 'BoC_BoK_2022.xlsx'))


# ___ Clean data
# - gdp
gdp.index = gdp['ISO']
gdp.drop(labels='ISO', axis=1, inplace=True)
gdp.drop(labels=['SOURCE', 'CURRENCY'], axis=0, inplace=True)
gdp = gdp / 1000000 # millions

# - gdp_c
gdp_c.index = gdp_c['ISO']
gdp_c.drop(labels='ISO', axis=1, inplace=True)
gdp_c.drop(labels=['SOURCE', 'CODE', 'CURRENCY'], axis=0, inplace=True)

# - debt
debt = debt[debt['ISO'].notna()]
debt = debt.set_index(['ISO', 'YEAR'])
debt.drop(labels= ['CODE', 'COUNTRY GROUP', 'COUNTRY'], axis=1, inplace=True)


# ___ Complete data
#list(set(gdp_c.columns) - set(gdp.columns))
gdp = gdp.merge(gdp_c, how='left', left_on=gdp.index, right_on=gdp_c.index, right_index=False, left_index=False)
gdp = gdp.rename(columns = {'key_0':'YEAR'})
gdp.index       = gdp['YEAR']
gdp.drop(labels ='YEAR', axis=1, inplace=True)
gdp = pd.DataFrame(gdp.stack(dropna=False))
gdp = gdp.rename(columns = {0:'GDP'})
gdp.index.names = ['YEAR', 'ISO']
gdp = gdp.reorder_levels(['ISO','YEAR'])


# ___ Final base
#base = gdp.merge(debt, left_index=True, right_on=['ISO', 'YEAR'])
base = pd.merge(gdp, debt, on = ['ISO', 'YEAR'], how = 'outer')
base = base.sort_index(level=1)
base = base.sort_index(level=0)


# ___ Fill NA
base = base.groupby('ISO').apply(cld.fillna_downbet, p=1)


#_________________________________________________________________________________
# ___ CRISIS CRITERION
#_________________________________________________________________________________
# Nguyen T.C., Castro V. and Wood J. (2022) criterion :
#   - Total sovereign default exceed 1% of GDP in at least three consecutive years, or
#   - Total sovereign default exceed 7% of GDP.

# ___ Parameters
# - Fisrt condition NGC
th1   = 1 # 1% GDP
th1_y = 3 # 3 years

# - Second condition NGC
th2   = 7 # 7% GDP


# ___ Criterion
# - First condition
base['TH1'] = base['TOTAL_2022'] / base['GDP'] * 100
base.loc[base['TH1'] < th1, 'TH1']  = 0

iso = np.unique(base.index.get_level_values('ISO'))
yrs = np.unique(base.index.get_level_values('YEAR'))

base['YEAR']      = base.index.get_level_values('YEAR')
base['START1']    = base['TH1']
base['DURATION1'] = base['TH1']

base.loc[base['START1'].notna(), 'START1']       = 0
base.loc[base['DURATION1'].notna(), 'DURATION1'] = 0


# Loop to identify onset and duration of crises (+ duration condition)
for i in iso:
    df = base[(base.index.get_level_values('ISO') == i) & (base['TH1'] > 0)]

    # identification of the years for which the criterion (threshold) is met and was met in the previous year
    df['DIFF'] = df['YEAR'].diff(1)
    df.loc[df['DIFF'] != 1, 'DIFF'] = 0

    # number of successive years during which the criterion is met (conditional cumsum)
    g = df['DIFF'].eq(0).shift().bfill().cumsum()
    df['CUMSUM'] = df.groupby(g)['DIFF'].cumsum()
    df.loc[df['DIFF'] == 0, 'CUMSUM'] = 0

    # deletion of years that do not meet the duration criterion
    year = df['YEAR'][df['CUMSUM'] >= th1_y-1]
    start = year - df['CUMSUM'][df['YEAR'].isin(year)]
    start = list(np.unique(start))

    # assign 1 during crisis => identify year(s) during crisis
    year   = list(year)
    year_m = list(range(0,th1_y))
    for s in start:
        year_t = list(year_m + s)
        year  += year + year_t
        
    year = np.unique(year)

    # assign starting dates and durations on the original base
    base.loc[(base.index.get_level_values('ISO') == i) & (base.index.get_level_values('YEAR').isin(start)), 'START1']   = 1
    base.loc[(base.index.get_level_values('ISO') == i) & (base.index.get_level_values('YEAR').isin(year)), 'DURATION1'] = 1

    
 
# - Second condition
base['TH2'] = base['TOTAL_2022'] / base['GDP'] * 100
base.loc[base['TH2'] <  th2, 'TH2']  = 0

iso = np.unique(base.index.get_level_values('ISO'))
yrs = np.unique(base.index.get_level_values('YEAR'))

base['START2'] = base['TH2']
base.loc[base['START2'].notna(), 'START2'] = 0

base.loc[base['TH2'] >= th2, 'TH2'] = 1
base['DURATION2'] = base['TH2']



# Loop to identify onset and duration of crises
for i in iso:
    df = base[(base.index.get_level_values('ISO') == i) & (base['TH2'] > 0)]
    #df = df[base['DURATION1'] < 1]

    # identification of the years for which the criterion (threshold) is met and was met in the previous year
    df['DIFF'] = df['YEAR'].diff(1)
    df.loc[df['DIFF'] != 1, 'DIFF'] = 0
    
    df.loc[df['DIFF']==0, 'START2'] = 1
    start = list(df.loc[df['START2']==1   , 'YEAR'])

    # assign starting dates on the original base
    base.loc[(base.index.get_level_values('ISO') == i) & (base.index.get_level_values('YEAR').isin(start)), 'START2']   = 1


# ___ Condition 1 or condition 2 
base['START']    = base['START1']
base['DURATION'] = base['DURATION1']

base.loc[(base['DURATION1']==0) & (base['START2']==1)   , 'START']    = 1
base.loc[(base['DURATION1']==0) & (base['DURATION2']==1), 'DURATION'] = 1


#_________________________________________________________________________________
# ___ FINAL FILE
#_________________________________________________________________________________
base = base.drop(['IBRD_2022', 'IDA_2022','PARIS_CLUB_2022', 'CHINA_2022',
                  'OTHER_OFFICIAL_CREDITORS_2022','PRIVATE_CREDITORS_2022',
                  'FC_BANK_LOANS_2022', 'FC_BONDS_2022','LC_2022', 'FISCAL_ARREARS_2022',
                  'GDP', 'TOTAL_2022', 'IMF_2022', 'TH1', 
                  'YEAR', 'START1', 'TH2', 'DURATION1', 'START2', 'DURATION2'], axis=1)

base.to_csv('debt_crises.csv', sep=';')
