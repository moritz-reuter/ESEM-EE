#%% Packages
import pvlib as pv
import windpowerlib as wind

from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
from feedinlib import Photovoltaic
from feedinlib import get_power_plant_data
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
            mode = 'dc' # mode is default 'ac' but can be set to 'dc' --> dc circumvents inverter losses!
            ).reset_index(level=None,drop=True)

    
    return pv_feedin

# %%

# %%
