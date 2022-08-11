#%% Packages
from statistics import mode
import oemof.thermal as therm
import pandas as pd
import numpy as np

#%% Heating system - temperatures
def heating_params(heat_system, heat_pump, weather):
    if heat_system == 'HKS':
        T_out = [60]*len(weather)
    else: 
        T_out = [40]*len(weather)

    if heat_pump == 'HP_air':
        T_in = weather['temp_air']
        quality_grade = 0.4
        # temp_threshold_icing = 2
    elif heat_pump == 'HP_ground':
        T_in = [12]*len(weather)
        quality_grade = 0.55
    elif heat_pump == 'HP_water':
        T_in = [10]*len(weather)
        quality_grade = 0.5

    return T_in, T_out, quality_grade # temp_threshold_icing

# %% Heatpump - Electricity demand via COP
def heat_pump_el(T_in, T_out, heat_demand, quality_grade): # set temp_threshold_icing as exogenous!

    cop = therm.compression_heatpumps_and_chillers.calc_cops(mode = 'heat_pump',
                          temp_high = T_out,
                          temp_low = T_in,
                          quality_grade = quality_grade,
                          temp_threshold_icing = 2, # assumption!
                          factor_icing = 0.95 #assumption
                            )
    el_hp = heat_demand / cop #--make sure both are arrays!
    return el_hp, np.array(cop)

# %% Solar thermal collector - not concentrated (Heat Feed-in)

def soltherm_heat(collector, lat, lon, stconfig_df, weather, timeindex):
    
    # collectors = stconfig_df.index

    # soltherm_feedin = dict.fromkeys(collectors)

    #%% Fill
    # for i in collectors:
    i = collector
    soltherm_feedin = therm.solar_thermal_collector.flat_plate_precalc(
            lat,
            lon,
            collector_tilt = stconfig_df.loc[i]['collector_tilt'],
            collector_azimuth = stconfig_df.loc[i]['collector_azimuth'],
            eta_0 = stconfig_df.loc[i]['eta_0'],
            a_1 = stconfig_df.loc[i]['a_1'],
            a_2 = stconfig_df.loc[i]['a_2'],
            temp_collector_inlet = stconfig_df.loc[i]['temp_collector_inlet'],
            delta_temp_n  = stconfig_df.loc[i]['delta_temp_n'],
            irradiance_global = weather['ghi'],
            irradiance_diffuse = weather['dhi'],
            temp_amb = weather['temp_air']
        ).reset_index(level=None,drop=True)

    col_heat = pd.DataFrame(soltherm_feedin["collectors_heat"]).set_index(timeindex)

    return col_heat


# %% Solar thermal collector - concentrated (Heat Feed-in)
