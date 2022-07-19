#%% Packages
import pvlib as pv
import windpowerlib as wind
import oemof.thermal as therm
# import demandlib as demand
import demand_fn
import weather_fn
import helper_functions
import feedin_fn

data = 'data.xlsx'

#%% Streamlit user info
year                = 2017
number_household    = 2
annual_elec_demand  = 1500  #kWh
annual_heat_demand  = 15000 #kWh
slp_type_heat       = 'EFH'
slp_type_elec       = 'h0'  # --> write function to determine elec_slp based on heat_slp 
lat                 = 52.52
lon                 = 13.4050
elec_mix            = 'DE-Mix'
heat_tech           = 'Boiler'
co2_price           = 300
province            = 'SH'
pv_area             = 10

#%% Weather
weather_hourly = weather_fn.tmy_data(lat, lon)

#%% Technology Data
tech_data   = helper_functions.sheet_xl(data, "tech")

#%% Feed-in

### PV ###
module              = "Silevo_Triex_U300_Black__2014_"
inverter            = "ABB__MICRO_0_3_I_OUTD_US_240__240V_"
pv_elec_per_m2      = feedin_fn.pv_elec(weather_hourly, module, inverter, lat, lon)
pv_elec             = pv_elec_per_m2*pv_area

### Wind ###


#%% Demand

### Electrical load profile ###
elec_demand_hourly = demand_fn.elec_slp(year,province, sector = slp_type_elec, ann_demand= annual_elec_demand)

### Heat load profile ###
heat_demand_hourly = demand_fn.heat_slp(year, province, slp_type_heat, annual_heat_demand, weather = weather_hourly)
#%% CO2 - Factors

