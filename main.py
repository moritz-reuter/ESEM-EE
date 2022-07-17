#%% Packages
import pvlib as pv
import windpowerlib as wind
import oemof.thermal as therm
import demandlib as demand
import demand_fn


#%% Streamlit user info
year                = 2017
number_household    = 2
annual_elec_demand  = 1500 #kWh
annual_heat_demand  = 15000 #kWh
slp_type            = 'EFH'
lat                 = 52.52
lon                 = 13.4050
elec_mix            = 'DE-Mix'
heat_tech           = 'Boiler'
co2_price           = 300
province            = 'SH'

#%% Demand

### Electrical load profile ###
elec_demand_hourly = demand_fn.elec_slp(year,province, slp_type, annual_elec_demand)

heat_demand_hourly = demand_fn.heat_slp(year, province, slp_type, annual_heat_demand)
# %%
