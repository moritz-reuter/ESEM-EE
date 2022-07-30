#%% Packages
import pvlib as pv
import windpowerlib as wind

from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
from feedinlib import Photovoltaic, get_power_plant_data, WindPowerPlant
from windpowerlib.wind_turbine import WindTurbine
import helper_functions
#%% PV-Feedin

def pv_elec(weather, module, inverter, lat, lon):

    azimuth = 180
    tilt = 37.5
    albedo = 0.2
    scaling  = "area"
    mode = "ac"

    temperature_model_parameters = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

    sys_data = {
            'module_name': module,       # module name as in database
            'inverter_name': inverter,   # inverter name as in database
            'azimuth': azimuth,              # Azimuth angle of the module surface (South=180).
            'tilt': tilt,                  # Surface tilt angle in decimal degrees. The tilt angle is defined as degrees from horizontal
            'albedo': albedo,
            'temperature_model_parameters': temperature_model_parameters}               # The ground albedo.

    pv_system = Photovoltaic(**sys_data)

    pv_feedin = pv_system.feedin(
            weather=weather,
            location=(lat, lon),
            scaling= scaling, # can be scaled by 'area' or 'peak_power'
            mode = mode # mode is default 'ac' but can be set to 'dc' --> dc circumvents inverter losses!
            ).reset_index(level=None,drop=True)

    
    return pv_feedin

# %% Wind Feed-in
def wind_elec(weather, hub_height, data, lat, lon):
        '''
        hub_height: Set to house height + rotor_diameter and saftey gap!
        '''
        #%% Wind - Turbine feed-in timeseries
        wind_data = helper_functions.sheet_xl(data, 'wind').reset_index().rename({'index': 'wind_speed'}, axis = 1)
        power_curve = wind_data[['wind_speed', 'power']].rename(columns = {'power': 'value'})
        power_coefficient_curve = wind_data[['wind_speed', 'power_coefficient']].rename(columns = {'power_coefficient': 'value'})

        turbine_data = {
        'hub_height': hub_height, 
        'nominal_power': 400, # Watt
        'power_curve': power_curve, 
        'power_coefficient_curve': power_coefficient_curve, 
        'rotor_diameter': 2, # in meters
        'turbine_type': None, # None unless calling from windturbine database!
        }
        # turbine = WindTurbine(**turbine_data)

        turbine_solo = WindPowerPlant(**turbine_data)

        wind_feedin = turbine_solo.feedin(
        weather= weather,
        # scaling = "nominal_power"    #normalize to capacity (Leistung)
        ).reset_index(level=None,drop=True)

        return wind_feedin


# %%
