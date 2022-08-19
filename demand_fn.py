#%% Packages
import demandlib.bdew as bdew
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

    pr_holidays = [holi.Germany(years = [year], prov = x) for x in pr_keys]
    #key = sector, value = annual_value
    lp_dict = {sector: ann_demand}
    # pr_dict = dict(zip(pr_keys, pr_holidays))
    #%% Datetime - Index
    index=pd.date_range(
        datetime.datetime(year, 1, 1, 0), periods=8760, freq="H"
    )
    ##

    #%% Electricity profiles (bdew)
    e_slp = bdew.elec_slp.ElecSlp(year, holidays=pr_dict[province])

    elec_demand = e_slp.get_profile(lp_dict).asfreq('H')


    return elec_demand

# %% Function - HeatSlp
def heat_slp(year, province, sector, ann_demand, weather):
    heat_slp_types  = helper_functions.sheet_xl(data, "heat_slp")
    heat_prov       = helper_functions.sheet_xl(data, "heat_prov")

    # Building Parameters (demand, share of total demand and )
    b_keys = list(heat_slp_types.index) # --> EFH... GHD
    b_demand = [1]*14   #GWh, since annual load data is given in GWh!
    pr_class = heat_prov['class'].loc[province]
    b_class = [pr_class if b in ['EFH','MFH'] else 0 for b in b_keys] 

    b_lists = [b_keys, b_demand, b_class]

    dict_building = {
        k[0]: list(k[1:]) for k in zip(*b_lists)
    }

    # Province parameters
    pr_keys = [prov for prov in heat_prov.index]
    pr_holidays = [holi.Germany(years = [year], prov = x) for x in pr_keys]
    pr_wind = heat_prov['windy'].values

    pr_lists = [pr_keys, pr_holidays, pr_wind]

    dict_provinces = {
        k[0]: list(k[1:]) for k in zip(*pr_lists)
    }

    #%% Dataframes

    ##
    df_building = pd.DataFrame.from_dict(
        data = dict_building,
        orient = 'index',
        columns = ['heat_demand', 'building_class']
        )
    ##

    df_province = pd.DataFrame.from_dict(
        data = dict_provinces,
        orient = 'index',
        columns = ['holidays', 'wind_class']
    )
    heat_demand_hourly = bdew.HeatBuilding(
            pd.date_range(datetime.datetime(year, 1, 1, 0), periods=8760, freq="H"), 
            holidays=df_province['holidays'].loc[province],      #dict province
            temperature=weather['temp_air'],    #series csv read in
            shlp_type=sector,  #database building_type --> join?
            building_class= int(df_building['building_class'].loc[sector]), #dict province --> always 0!
            wind_class= int(df_province['wind_class'].loc[province]),  #dict province
            annual_heat_demand=ann_demand,
            ww_incl=True,   #IMMER TRUE!
            name=sector,
        ).get_bdew_profile()

    # regions = config.index

    return heat_demand_hourly
