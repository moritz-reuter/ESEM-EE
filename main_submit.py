#%% Packages
import streamlit as st
import pvlib as pv
import windpowerlib as wind
import oemof.thermal as therm
import pandas as pd
import numpy as np

### User 'packages'
import demand_fn
import weather_fn
import thermal_fn
import helper_functions
import feedin_fn
import calc
import gui

###########################
data = '/Users/mreuter/Documents/GitHub/ESEM----EE/data.xlsx'
###########################'

def submit(submission):
    # year                    = submission['year']
    # # number_household        = submission['number_household'] # --> is this important?
    # annual_elec_demand      = submission['annual_elec_demand']  # kWh
    # annual_heat_demand      = submission['annual_heat_demand'] # kWh
    # slp_type_heat           = submission['slp_type_heat'] # MFH
    # slp_type_elec           = submission['slp_type_elec']  # --> write function to determine elec_slp based on heat_slp (only household implementation) 
    # lat                     = submission['lat']
    # lon                     = submission['lon']
    # province                = submission['province'] #see list of provinces in XL
    # elec_mix_old            = submission['elec_mix_old']
    # heat_tech               = submission['heat_tech_old'] # read in from list of heat_techs
    # heat_system             = submission['heat_system']
    # co2_price_sim           = submission['co2_price_sim'] # €/tCO2 --> write function to determine price per kg for sim selection

    # pv_area                 = submission['pv_area'] # m2
    # heat_pump               = submission['heat_pump'] # HP_ground, HP_water
    # st_collector            = submission['st_collector']
    # st_area                 = submission['st_area']
    # hub_height              = submission['hub_height']
    
    year                    = submission[0]
    # number_household        = submission['number_household'] # --> is this important?
    annual_elec_demand      = submission[1]  # kWh
    annual_heat_demand      = submission[2] # kWh
    slp_type_elec           = submission[3]  # --> write function to determine elec_slp based on heat_slp (only household implementation) 
    slp_type_heat           = submission[4] # MFH
    lat                     = submission[5]
    lon                     = submission[6]
    province                = submission[7] #see list of provinces in XL
    elec_mix_old            = submission[8]
    heat_tech               = submission[9] # read in from list of heat_techs
    heat_system             = submission[10]
    co2_price_sim           = submission[11] # €/tCO2 --> write function to determine price per kg for sim selection

    pv_area                 = submission[12] # m2
    heat_pump               = submission[13] # HP_ground, HP_water
    st_collector            = submission[14]
    st_area                 = submission[15]
    ###############################################
    ###############################################
    co2_price = calc.co2_price(co2_price_sim, data)

    #%% Weather
    weather_hourly          = weather_fn.tmy_data(lat, lon)
    # wind_hourly             = weather_hourly[['wind_speed', 'pressure']].rename_axis(None, axis=0)
    # wind_hourly.columns     = pd.MultiIndex.from_product([wind_hourly.columns, [hub_height]])

    # pv_hourly = weather_fn.era5_weather(lat, lon, year, 'pvlib')
    # wind_hourly = weather_fn.era5_weather(lat, lon, year, 'windpowerlib')

    #%%#########    Demand      ###########################

    ### Electrical load profile ###
    elec_demand_hourly = demand_fn.elec_slp(year,province, sector = slp_type_elec, ann_demand= annual_elec_demand).iloc[:,0]

    ### Heat load profile ###
    heat_demand_hourly = demand_fn.heat_slp(year, province, slp_type_heat, annual_heat_demand, weather = weather_hourly)

    time_index_year = elec_demand_hourly.index

    #%% Technology Data
    tech_data   = helper_functions.sheet_xl(data, "tech")

    #%%########     Feed-in (elec)  ##################################
    renewable_elec = ['PV', 'Wind']
    ### PV [kWh] ###
    module              = "Silevo_Triex_U300_Black__2014_"
    inverter            = "ABB__MICRO_0_3_I_OUTD_US_240__240V_"
    pv_elec_watt_per_m2 = feedin_fn.pv_elec(weather_hourly, module, inverter, lat, lon)
    pv_elec             = pd.DataFrame((pv_elec_watt_per_m2*pv_area) / 1000).set_index(time_index_year)

    #%%
    ### Wind [kWh] ### --> BUG
    # wind_weather = weather_hourly
    # wind_weather.index.name = None
    # wind_elec_watt      = feedin_fn.wind_elec(wind_hourly, hub_height, data, lat, lon)
    # wind_elec           = pd.DataFrame(wind_elec_watt).set_index(time_index_year)
    wind_elec           = pd.DataFrame([0]*len(pv_elec), index= time_index_year)

    ##########      Heat        #################################
    #%% Solar thermal - Heat feedin
    soltherm_data = helper_functions.sheet_xl(data, 'soltherm_data')

    st_feedin_spec  = thermal_fn.soltherm_heat(st_collector, lat, lon, soltherm_data, weather_hourly, time_index_year) / 1000
    st_feedin       = st_feedin_spec * st_area

    #%% Heat pump
    '''
    heat_pump_el returns the electrical demand kWh of a heat pump that satisfies the hourly heat demand given by the gas slp profile
    '''

    T_in, T_out, quality_grade_hp = thermal_fn.heating_params(heat_system, heat_pump, weather_hourly)

    heat_demand_renewable = heat_demand_hourly - st_feedin['collectors_heat']

    '''
    heat_pump_el calculates the (additional) hourly electricity demand stemming from the use of a heat pump for heating.
    Units (and dimensions) are derived from the input paramater heat_demand_renewable, which calculates the excess heat_demand after factoring 
    in the heat energy that is provided through a solar thermal (roof) 
    '''
    heat_pump_el, cop = thermal_fn.heat_pump_el(T_in, T_out, heat_demand_renewable, quality_grade_hp)

    # jaz = heat_demand_hourly.sum() / heat_pump_el.sum()


    #%% ###### CO2 emissions ##############

    co2_price_kg = co2_price/1000 # €/kgCO2

    #%% Electricity
    co2_old_elec = calc.co2_kwh(elec_mix_old, tech_data, elec_demand_hourly) /1000

    ####
    new_elec_demand = heat_pump_el + elec_demand_hourly

    renewable_feedin_dict = {'PV': pv_elec[0],
                        'Wind': wind_elec[0]
                        }
    renewable_feedin = pd.DataFrame.from_dict(renewable_feedin_dict)

    ren_tech_co2 = []
    for ren_tech in renewable_elec:
        ren_tech_co2.append(calc.co2_kwh(ren_tech, tech_data, renewable_feedin_dict[ren_tech]) /1000)


    residual_load = new_elec_demand - renewable_feedin.sum(axis = 1)

    co2_grid = calc.co2_kwh(elec_mix_old, tech_data, residual_load) / 1000

    co2_sum_new = co2_grid + sum(ren_tech_co2)
    #%%
    co2_new_elec = pd.DataFrame(co2_sum_new).set_index(time_index_year)

    ##%% Gas 
    co2_old_gas = calc.co2_kwh(heat_tech, tech_data, heat_demand_hourly) / 1000


    #### --> adapt to necessary gas demand...
    new_gas_demand = pd.DataFrame([0]*len(weather_hourly)).set_index(time_index_year)
    ####
    co2_new_gas = pd.DataFrame([0]*len(weather_hourly)).set_index(time_index_year)

    #%% ############## Compensation ##########
    old_co2 = co2_old_gas + co2_old_elec
    new_co2 = co2_new_elec[0] + co2_new_gas[0]

    # If comp > 0 --> new_co2 is smaller than old_co2!
    comp =  pd.DataFrame(np.subtract(old_co2.values, new_co2.values), columns = ['comp']).set_index(time_index_year)

    #%%######### Savings ###########
    #%% Without CO2-price ####
    old_price_elec = calc.price_kwh(elec_mix_old,tech_data,elec_demand_hourly)
    old_price_gas = calc.price_kwh(heat_tech, tech_data, heat_demand_hourly)

    new_price_elec = calc.price_kwh(elec_mix_old, tech_data, new_elec_demand)
    new_price_gas  = calc.price_kwh(heat_tech, tech_data, new_gas_demand[0])
    old_price_energy = old_price_elec + old_price_gas
    new_price_energy  = new_price_gas + new_price_elec

    ## Savings in €
    price_diff = pd.DataFrame(np.subtract(old_price_energy, new_price_energy) /100, columns = ['price_diff']) # positive means savings! 

    #%% With CO2-Price
    old_price_co2 = old_co2 * co2_price_kg
    old_price_total = old_price_co2 + old_price_energy/100

    new_price_co2 = new_co2* co2_price_kg
    new_price_total = new_price_co2 + new_price_energy/100

    total_diff = pd.DataFrame(np.subtract(old_price_total, new_price_total), columns= ['total_diff'])

    #%% Output

    df = pd.concat([comp, price_diff, total_diff], axis = 1)

    return df
# %%
