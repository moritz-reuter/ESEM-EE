#%% Packages
import pvlib as pv
import windpowerlib as wind
import oemof.thermal as therm
import demandlib as demand



#%% Streamlit user info
year                = 2019
number_household    = 2
annual_elec_demand  = 1500 #kWh
slp_type            = 'EFH'
lat                 = 52.52
lon                 = 13.4050
elec_mix            = 'DE-Mix'
heat_tech           = 'Boiler'
co2_price           = 300


#%% 