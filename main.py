#%% Packages
from nose import collector
import pvlib as pv
import windpowerlib as wind
import oemof.thermal as therm
import pandas as pd
import numpy as np
# import demandlib as demand
import demand_fn
import weather_fn
import thermal_fn
import helper_functions
import feedin_fn
import calc


data = 'data.xlsx'

#%% Streamlit user info
year                    = 2019
number_household        = 2 # --> is this important?
annual_elec_demand      = 1500  # kWh
annual_heat_demand      = 15000 # kWh
slp_type_heat           = 'EFH' # MFH
slp_type_elec           = 'h0'  # --> write function to determine elec_slp based on heat_slp 
lat                     = 52.52
lon                     = 13.4050
co2_price               = 80 # €/tCO2
elec_mix                = 'G_DE'
heat_tech               = 'CHB' # read in from list of heat_techs
heat_system             = 'HKS'
co2_price               = 300 # €/tCO2
province                = 'SH' #see list of provinces in XL
pv_area                 = 10 # m2
heat_pump               = 'HP_air' # HP_ground, HP_water
st_collector            = 'tube'

#%% Weather
weather_hourly = weather_fn.tmy_data(lat, lon)


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
pv_elec_per_m2      = feedin_fn.pv_elec(weather_hourly, module, inverter, lat, lon)
pv_elec             = pd.DataFrame((pv_elec_per_m2*pv_area) / 1000).set_index(time_index_year)

### Wind [kWh] ###
wind_elec           = pd.DataFrame([0]*len(weather_hourly)).set_index(time_index_year)

##########      Heat        #################################
#%% Solar thermal - Heat feedin
soltherm_data = helper_functions.sheet_xl(data, 'soltherm_data')

st_feedin = thermal_fn.soltherm_heat(st_collector, lat, lon, soltherm_data, weather_hourly, time_index_year) / 1000

#%% Heat pump
'''
heat_pump_el returns the electrical demand kWh of a heat pump that satisfies the hourly heat demand given by the gas slp profile
'''

T_in, T_out, quality_grade_hp = thermal_fn.heating_params(heat_system, heat_pump, weather_hourly)

heat_demand_renewable = heat_demand_hourly - st_feedin['collectors_heat']

heat_pump_el, cop = thermal_fn.heat_pump_el(T_in, T_out, heat_demand_renewable, quality_grade_hp)

jaz = heat_demand_hourly.sum() / heat_pump_el.sum()


#%% ###### CO2 emissions ##############

co2_price_kg = co2_price/1000 # €/kgCO2

#%% Electricity
co2_old_elec = calc.co2_kwh(elec_mix, tech_data, elec_demand_hourly) /1000

####
new_elec_demand = heat_pump_el + elec_demand_hourly

renewable_feedin = [pv_elec['p_mp'], wind_elec[0]]

ren_tech_co2 = []
for ren_tech in renewable_elec:
    for j in range(len(renewable_feedin)):
        ren_tech_co2.append(calc.co2_kwh(ren_tech, tech_data, renewable_feedin[j]) /1000)


residual_load = new_elec_demand - sum(renewable_feedin)

co2_grid = calc.co2_kwh(elec_mix, tech_data, residual_load) / 1000

co2_sum_new = co2_grid + sum(ren_tech_co2)

co2_new_elec = pd.DataFrame(co2_sum_new).set_index(new_elec_demand.index)

##%% Gas 
co2_old_gas = calc.co2_kwh(heat_tech, tech_data, heat_demand_hourly) / 1000


#### --> adapt to necessary gas demand...
new_gas_demand = pd.DataFrame([0]*len(weather_hourly)).set_index(new_elec_demand.index)
####
co2_new_gas = pd.DataFrame([0]*len(weather_hourly)).set_index(new_elec_demand.index)

#%% ############## Compensation ##########
old_co2 = co2_old_gas + co2_old_elec
new_co2 = co2_new_elec[0] + co2_new_gas[0]

# If comp > 0 --> new_co2 is smaller than old_co2!
comp =  np.subtract(old_co2.values, new_co2.values)

#%%######### Savings ###########
#%% Without CO2-price ####
old_price_elec = calc.price_kwh(elec_mix,tech_data,elec_demand_hourly)
old_price_gas = calc.price_kwh(heat_tech, tech_data, heat_demand_hourly)

new_price_elec = calc.price_kwh(elec_mix, tech_data, new_elec_demand)
new_price_gas  = calc.price_kwh(heat_tech, tech_data, new_gas_demand[0])
old_price_energy = old_price_elec + old_price_gas
new_price_energy  = new_price_gas + new_price_elec

## Savings in €
price_diff = np.subtract(old_price_energy, new_price_energy) /100 # positive means savings! 

#%% With CO2-Price
old_price_co2 = old_co2 * co2_price_kg
old_price_total = old_price_co2 + old_price_energy/100

new_price_co2 = new_co2* co2_price_kg
new_price_total = new_price_co2 + new_price_energy/100

total_diff = np.subtract(old_price_total, new_price_total)


#%% 
