#%% Packages
import demandlib as demand
import holidays as holi
import helper_functions
import os
import pandas as pd
import datetime

## Data - Filepath ##
data = 'data.xlsx'

##% Function - ElecSlp
def elec_slp(year, province, sector, ann_demand):
    
    provinces_df = helper_functions.sheet_xl(data, 'provinces')
    provinces = provinces_df.index.tolist()

    pr_keys = provinces
    pr_holidays = [holi.Germany(years = [year], prov = x) for x in pr_keys]

    pr_dict = dict(zip(pr_keys, pr_holidays))
    # %% Dictionaries
    # Load profile demand

    # lp_dict = dict(zip(lp_keys,lp_demand))

    pr_holidays = holi.Germany(years = [year], prov = pr_dict[province])
    #key = sector, value = annual_value
    lp_dict = {sector: ann_demand}
    # pr_dict = dict(zip(pr_keys, pr_holidays))
    #%% Datetime - Index
    index=pd.date_range(
        datetime.datetime(year, 1, 1, 0), periods=8760, freq="H"
    )
    ##

    #%% Electricity profiles (bdew)
    e_slp = demand.bdew.ElecSlp(year, holidays=pr_dict[province])

    elec_demand = e_slp.get_profile(lp_dict).asfreq('H')


    return elec_demand

# %% Function - HeatSlp
def heat_slp(year, province, sector, ann_demand):

    return heat_demand
