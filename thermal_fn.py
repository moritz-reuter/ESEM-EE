#%% Packages
from statistics import mode
import oemof.thermal as therm
import pandas as pd
import numpy as np

#%% Heating system - temperatures
def heating_params(heat_system, heat_pump, weather):

    T_i = []
    T_o = []
    quality_grd = 0

    ###############################################

    if heat_system == 'HKS':
        T_o = [60]
    else: 
        T_o = [40]

    ##############################################

    if heat_pump == 'HP_air':
        T_i = pd.Series(weather['temp_air'].values)
        quality_grd = 0.4
        
    elif heat_pump == 'HP_ground':
        T_i = pd.Series([12]*len(weather))
        quality_grd = 0.55

    elif heat_pump == 'HP_water':
        T_i = pd.Series([10]*len(weather))
        quality_grd = 0.5


    return T_i, T_o, quality_grd # temp_threshold_icing

# %% Heatpump - Electricity demand via COP
# def heat_pump_el(T_source, T_sink, heat_demand, quality_grade): # set temp_threshold_icing as exogenous!

#     cop = therm.compression_heatpumps_and_chillers.calc_cops(
#                         mode = "heat_pump",
#                         temp_high = T_sink,
#                         temp_low = T_source,
#                         quality_grade = quality_grade
#                         #   temp_threshold_icing = 2, # assumption!
#                         #   factor_icing = 0.95 #assumption
#                         )
                        
#     cop = [x if x > 0 else 5 for x in cop]
#     cop = [x if x < 5 else 5 for x in cop]
    
#     el_hp = heat_demand / cop #--make sure both are arrays!
#     return el_hp, np.array(cop)

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
