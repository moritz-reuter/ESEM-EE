#%% Packages
from statistics import mode
import oemof.thermal as therm
import pandas as pd
import numpy as np

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


#%% Heating system - temperatures
def heating_params(heat_system, heat_pump, weather):

    T_i = []
    T_o = []
    quality_grd = 0

    ###############################################

    if heat_system == 'HKS':
        T_o = [60]*len(weather)
    else: 
        T_o = [40]*len(weather)

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
def calc_cops(mode, temp_high, temp_low, quality_grade):

    r"""
    Calculates the Coefficient of Performance (COP) of heat pumps and chillers
    based on the Carnot efficiency (ideal process) and a scale-down factor.
    Note
    ----
    Applications of air-source heat pumps should consider icing
    at the heat exchanger at air-temperatures around :math:`2^\circ C` .
    Icing causes a reduction of the efficiency.
    .. calc_cops-equations:
        mode='heat_pump'
        :math:`COP = \eta \cdot \frac{T_\mathrm{high}}{T_\mathrm{high}
        - T_\mathrm{low}}`
        :math:`COP = f_\mathrm{icing} \cdot\eta
        \cdot\frac{T_\mathrm{high}}{T_\mathrm{high} - T_\mathrm{low}}`
        mode='chiller'
        :math:`COP = \eta \cdot \frac{T_\mathrm{low}}{T_\mathrm{high}
        - T_\mathrm{low}}`
    Parameters
    ----------
    temp_high : list or pandas.Series of numerical values
        Temperature of the high temperature reservoir in :math:`^\circ C`
    temp_low : list or pandas.Series of numerical values
        Temperature of the low temperature reservoir in :math:`^\circ C`
    quality_grade : numerical value
        Factor that scales down the efficiency of the real heat pump
        (or chiller) process from the ideal process (Carnot efficiency), where
         a factor of 1 means teh real process is equal to the ideal one.
    factor_icing: numerical value
        Sets the relative COP drop caused by icing, where 1 stands for no
        efficiency-drop.
    mode : string
        Two possible modes: "heat_pump" or "chiller" (default 'None')
    t_threshold:
        Temperature in :math:`^\circ C` below which icing at heat exchanger
        occurs (default 2)
    Returns
    -------
    cops : list of numerical values
        List of Coefficients of Performance (COPs)
    """
    # Check if input arguments have proper type and length
    # if not isinstance(temp_low, (list, pd.Series)):
    #     raise TypeError("Argument 'temp_low' is not of type list or pd.Series!")

    # if not isinstance(temp_high, (list, pd.Series)):
    #     raise TypeError("Argument 'temp_high' is not of "
    #                     "type list or pd.Series!")

    # if len(temp_high) != len(temp_low):
    #     if (len(temp_high) != 1) and ((len(temp_low) != 1)):
    #         raise IndexError("Arguments 'temp_low' and 'temp_high' "
    #                          "have to be of same length or one has "
    #                          "to be of length 1 !")

    # Make temp_low and temp_high have the same length and
    # convert unit to Kelvin.
    list_temp_high_K = []
    list_temp_low_K = []
    cops = []
    
    # length = max([len(temp_high), len(temp_low)])

    # if len(temp_high) == 1:
    #     list_temp_high_K = [temp_high[0] + 273.15] * length
    # elif len(temp_high) == length:
    #     list_temp_high_K = [t + 273.15 for t in temp_high]
    # if len(temp_low) == 1:
    #     list_temp_low_K = [temp_low[0] + 273.15] * length
    # elif len(temp_low) == length:
    #     list_temp_low_K = [t + 273.15 for t in temp_low]
    list_temp_high_K = [t + 273.15 for t in temp_high]
    list_temp_low_K = [t + 273.15 for t in temp_low]

    # Calculate COPs depending on selected mode (without icing).
    
    cops = [quality_grade * t_h / (t_h - t_l) for
            t_h, t_l in zip(list_temp_high_K, list_temp_low_K)]
    
    # Calculate COPs of a heat pump and lower COP when icing occurs.
    
    return cops

# def heat_pump_el(T_source, T_sink, heat_demand, quality_grade): # set temp_threshold_icing as exogenous!


#     cop = therm.compression_heatpumps_and_chillers.calc_cops(
#                         mode = "heat_pump",
#                         temp_high = T_sink,
#                         temp_low = T_source,
#                         quality_grade = quality_grade
#                         #   temp_threshold_icing = 2, # assumption!
#                         #   factor_icing = 0.95 #assumption
#                         )
    
#     el_hp = heat_demand / cop #--make sure both are arrays!
#     return el_hp



# %% Solar thermal collector - concentrated (Heat Feed-in)
