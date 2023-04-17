import os
import pandas as pd
import numpy as np


# __________ Directory
def relative_path(mod_path, relative_path, file_name):
    src_path = (mod_path / relative_path).resolve()
    filename = os.path.join(src_path, file_name)
    return(filename)



# __________ Data formating
# - IMF data formatting
# IFS
def clean_IFS(base, colname):
    base.index = base['ISO']
    base.drop(labels=['ISO','Country Name', 'Country Code', 'Indicator Name', 'Indicator Code', 'Attribute', 'Base Year'], axis=1, inplace=True)
    base = pd.DataFrame(base.stack(dropna=False))
    base = base.rename(columns = {0: colname})
    base.index.names = ['ISO', 'YEAR']
    base = base.sort_index()
    return base


# - Datastream data formatting
def clean_DS(base, colname):
    base.index = base['ISO']
    base.drop(labels='ISO', axis=1, inplace=True)
    base.drop(labels=['SOURCE', 'CODE', 'CURRENCY'], axis=0, inplace=True)
    base = pd.DataFrame(base.stack(dropna=False))
    base = base.rename(columns = {0: colname})
    base.index.names = ['YEAR', 'ISO']
    base = base.reorder_levels(['ISO','YEAR'])
    base = base.sort_index()
    return base
  


# __________ NA
# - Fill NA
# with the last observed value for a maximum of p consecutive periods but only till the last observed value.
def fillna_downbet(df, p):
    for col in df:
        non_nans   = np.where(df[col].isna()==False)
        if len(non_nans[0]) < 2 :
            continue
        else:
            start, end = non_nans[0][0], non_nans[0][-1]
            df[col].iloc[start:end] = df[col].iloc[start:end].fillna(method='ffill', limit=p)
    return df



# __________ Euro Area
# - Fill in missing/erroneous data for euro area member countries from their date of entry into the monetary union
def fill_euro(df, df_w, euro_mb, col_val, col_year):
    iso     = np.unique(df.index.get_level_values(0))
    iso_mb  = np.unique(euro_mb['ISO'])
    iso_int = list(set(iso) & set(iso_mb))
    if (len(iso_int)==1):
        start  = float(euro_mb['Adoption date'][euro_mb['ISO'].isin(iso_int)].str[:4])
        euz_df = pd.DataFrame(df_w[col_val][(df_w.index.get_level_values(0)=='EUZ') & (df_w[col_year] >= start)])
        euz_df.rename(index={'EUZ':iso_int[0]}, inplace=True) 
        #euz_df = euz_df.reset_index(level=0, drop=True)
        df.loc[(df.index.get_level_values(0)==iso_int[0]) & (df[col_year] >= start), col_val] = euz_df[col_val]
    return(df)
    
    

