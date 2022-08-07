#%%
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

import helper_functions
import main_submit
from thermal_fn import soltherm_heat

###########################
data = 'data.xlsx'
###########################


#%% Options #######################################
tech_data           = helper_functions.sheet_xl(data, 'tech')
elec_slp_options    = helper_functions.sheet_xl(data, 'heat_slp')['name']
prov_options        = helper_functions.sheet_xl(data, 'provinces')['value']
elec_mix_options    = tech_data[tech_data.index.str.contains('G_')].index.to_list()
heat_tech_options   = tech_data[tech_data['energy'] == 'heat'].index.to_list()
heat_system_options = ['FBH', 'HKS'] #make flexible via 
co2_price_options   = helper_functions.sheet_xl(data, 'co2').index.to_list()
heat_pump_options   = tech_data[tech_data.index.str.contains('HP_')].index.to_list()
st_tech_options     = helper_functions.sheet_xl(data, 'soltherm_data').index.to_list()

#%% GUI
try:
    with st.form('Submit'):
        col1, col2, col3 = st.columns(3)
        year                = col1.number_input(label='Jahr auswählen', step=1, min_value=2010, max_value=2021, value=2019, key='year')
        number_household    = col1.number_input(label='Anzahl der Personen im Haushalt', step=1, min_value=1, max_value=10, value=2,key='occupants')     
        
        annual_elec_demand  = col1.number_input(label='Stromnachfrage (jährlich, kWh)', step=100, min_value=1, max_value=100000, value=1500,key='annual_elec_demand')       
        annual_heat_demand  = col1.number_input(label='Gas (Wärme) Nachfrage (jährlich, kWh)', step=100, min_value=1, max_value=100000, value=15000,key='annual_heat_demand')       
        slp_type_heat       = col1.selectbox(label='Standardlastprofil (i.e., privat or geschäftlich)', options = elec_slp_options,key='slp_type_elec')   
        
        lat                 = col1.number_input(label='Latitude', step=1., value=52.52, key='lat')
        st.write('Der aktuelle Breitengrad ist: ', lat)
        lon                 = col1.number_input(label='Longitude', step=1., value=13.41, key='lon')
        st.write('Der aktuelle Längengrad ist: ', lon)
        province            = col1.selectbox(label='"Bundesland" (abbv)', options = prov_options,key='province')    #see list of provinces in XL

        elec_mix_old        = col1.selectbox(label='Stromtarif - Aktuell', options = elec_mix_options,key='elec_mix_old') 
        heat_tech           = col1.selectbox(label='Heizungstechnnologie - Aktuell', options = heat_tech_options,key='heat_tech_old') #'CHB' # read in from list of heat_techs
        heat_system         = col1.selectbox(label='Heizungssystem (zur Berechnung der Heizungsvorlauftemperatur)', options = heat_system_options,key='heat_system') #'HKS'
        co2_price_sim       = col1.selectbox(label='CO2-Reduktionspfad', options = co2_price_options,key='co2_price_sim')# 'BAU' # €/tCO2 --> write function to determine price per kg for sim selection

        pv_area             = col1.number_input(label='PV-Anlagenfläche', step=1., value=10., key='pv_area') # 10 # m2
        heat_pump           = col1.selectbox(label='CO2-Reduktionspfad', options = heat_pump_options,key='co2_price_sim') #'HP_air' # HP_ground, HP_water
        st_collector        = col1.selectbox(label='Solarthermie Technologie (Nicht-konzentriert)', options = st_tech_options,key='st_collector') 
        st_area             = col1.number_input(label='Solarthermie-Anlagenfläche', step=1., value=10., key='st_area') # 10 # m2
        hub_height          = col1.number_input(label='Windkraftanlage - Nabenhöhe', step=1., value=15., key='hub_height') # 10 # m2
        # col3, col4 = st.columns(2)


        submit1 = st.form_submit_button('Log Input Variables')

    GUI1 = st.checkbox('Visualisation')

    if GUI1:
        submission = {
            'year': year,
            'number_household':number_household,
            'annual_elec_demand':annual_elec_demand,
            'annual_heat_demand':annual_heat_demand,
            'slp_type_heat':slp_type_heat,
            'lat':lat,
            'lon':lon,
            'province':province,
            'elec_mix_old':elec_mix_old,
            'heat_tech':heat_tech,
            'heat_system':heat_system,
            'co2_price_sim':co2_price_sim,
            'pv_area':pv_area,
            'heat_pump':heat_pump,
            'st_collector':st_collector,
            'st_area':st_area,
            'hub_height': hub_height
        }

        #st.write(submission)
        df = main_submit.submit(submission)
        # --> main.submit function for running simulation with given user variables
        # --> if main.submit returns df --> makes plot easy!


        ''' Plotting'''
        # with st.form('Show Results of Visualisation'):
        #     df = df.reset_index()
        #     df_plot = df.iloc[:, [0,1]]
        #     fig = px.line(
        #     df_plot,        #Data Frame
        #         x=df_plot.iloc[:, 0],     #Columns from the data frame
        #         y=df_plot.iloc[:, 1],
        #         title="NAME")

        #     fig.update_traces(line_color="maroon")
        #     st.plotly_chart(fig)
        #     submit2 = st.form_submit_button('')

except NameError:
    st.error("Error! Not all input statements were chosen.")

# %%
