#%% Packages
import pandas as pd
import numpy as np

############################
import helper_functions

#%%
def co2_kwh(tech, tech_data, energy_hourly):
    co2_factor = tech_data.loc[tech]['ef']

    emissions_hourly = co2_factor * pd.Series(energy_hourly)

    return emissions_hourly


def price_kwh(tech, tech_data, energy_hourly):
    price_factor = tech_data.loc[tech]['price']

    price_hourly = pd.Series(energy_hourly) * price_factor

    return price_hourly

def co2_price(co2_price_sim, data):
    co2_data= helper_functions.sheet_xl(data, "co2")
    co2_price = co2_data.loc[co2_price_sim]['co2_price']

    return co2_price
