#%%
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import datetime as dt

import helper_functions
import main_submit


###########################
data = 'data.xlsx'
###########################

#%%
# Options #######################################
tech_data           = helper_functions.sheet_xl(data, 'tech')
elec_slp_data       = helper_functions.sheet_xl(data, 'elec_slp')
elec_slp_options    = elec_slp_data['name'].to_list()
heat_slp_data       = helper_functions.sheet_xl(data, 'heat_slp')
heat_slp_options    = heat_slp_data['name'].to_list()

prov_data           = helper_functions.sheet_xl(data, 'provinces')
prov_options        = prov_data['value'].to_list()
elec_mix_options    = tech_data[tech_data.index.str.contains('G_')]['name'].to_list()
heat_tech_options   = tech_data[tech_data['energy'] == 'heat']['name'].to_list()
heat_system_options = ['Fußbodenheizung', 'Heizkörpersystem'] #make flexible via 
co2_data            = helper_functions.sheet_xl(data, 'co2')
co2_price_options   = co2_data['name'].to_list()
heat_pump_options   = tech_data[tech_data.index.str.contains('HP_')]['name'].to_list()
# st_tech_options     = helper_functions.sheet_xl(data, 'soltherm_data')['name'].to_list()
soltherm_data       = helper_functions.sheet_xl(data, 'soltherm_data')
st_tech_options     = ['Vakuumröhrenkollektor', 'Flachkollektor']
#%%
#GUI
with st.expander('Simulationsvariablen', expanded=True):
    with st.form('Submit'):
        tab1,tab2,tab3, tab4 = st.tabs(['Basis Info', 'Verbraucher Info', 'Aktuelle Tech.', 'Zukunfts-Tech'])
        
        with tab1:
            st.header('Basis Informationen')
            year                    = st.number_input(label='Jahr auswählen', step=1, min_value=2010, max_value=2022, value=2019, key='year')
            # number_household    = col1.number_input(label='Anzahl der Personen im Haushalt', step=1, min_value=1, max_value=10, value=2,key='occupants')     
            lat                     = st.number_input(label='Breitengrad', step=1., value=52.52, key='lat')
            # st.write('Der aktuelle Breitengrad ist: ', lat)
            lon                     = st.number_input(label='Längengrad', step=1., value=13.41, key='lon')
            # st.write('Der aktuelle Längengrad ist: ', lon)
            province                = st.selectbox(label='"Bundesland" (Abk.)', options = prov_options,key='province', index = 3)    #see list of provinces in XL
            location = pd.DataFrame(np.array([[float(lat), float(lon)]]), columns=['lat', 'lon'])
            loc = st.map(location)
        
        with tab2:
            st.header('Verbraucher Informationen')
            annual_elec_demand      = st.number_input(label='Stromnachfrage (jährlich, kWh)', step=100, min_value=1, max_value=100000, value=1500,key='annual_elec_demand')       
            annual_heat_demand      = st.number_input(label='Gas (Wärme) Nachfrage (jährlich, kWh)', step=100, min_value=1, max_value=100000, value=6000,key='annual_heat_demand')       
            slp_type_elec_st        = st.selectbox(label='Standardlastprofil Strom (i.e., privat or geschäftlich)', options = elec_slp_options, key='slp_type_elec', index = 7)   
            slp_type_heat_st        = st.selectbox(label='Standardlastprofil Gas (i.e., privat or geschäftlich)', options = heat_slp_options, key='slp_type_heat', index = 0)  
        
        with tab3:
            st.header('Aktuelle Heiz- und Stromtechnologien')
            elec_mix_old_st         = st.selectbox(label='Stromtarif - Aktuell', options = elec_mix_options, key='elec_mix_old', index = 1) 
            heat_tech_old_st        = st.selectbox(label='Heizungstechnnologie - Aktuell', options = heat_tech_options, key='heat_tech_old', index = 0) #'CHB' # read in from list of heat_techs
            heat_system_st          = st.selectbox(label='Heizungssystem (zur Berechnung der Heizungsvorlauftemperatur)', options = heat_system_options, key='heat_system', index = 0) #'HKS'
        
        with tab4:
            st.header('Zukunftsgerichtete Technologien und CO2-Preis-Szenarien')
            pv_area                 = st.number_input(label='PV-Anlagenfläche', step=1., value=10., key='pv_area') # 10 # m2
            heat_pump_st            = st.selectbox(label='Wärmepumpe', options = heat_pump_options, key='heat_pump',index = 0) #'HP_air' # HP_ground, HP_water
            st_collector_st         = st.selectbox(label='Solarthermie Technologie (Nicht-konzentriert)', options = st_tech_options, key='st_collector', index = 0) 
            st_area                 = st.number_input(label='Solarthermie-Anlagenfläche', step=1., value=10., key='st_area') # 10 # m2
            co2_price_sim_st        = st.selectbox(label='CO2-Reduktionspfad', options = co2_price_options, key='co2_price_sim', index = 0)# 'BAU' # €/tCO2 --> write function to determine price per kg for sim selection


        submit1 = st.form_submit_button('Log Input Variables')

GUI1 = st.checkbox('Start Simulation')

if GUI1:
    slp_type_elec   = slp_type_elec_st
    slp_type_heat   = slp_type_heat_st
    elec_mix_old    = elec_mix_old_st
    heat_tech_old   = heat_tech_old_st
    heat_system     = heat_system_st
    co2_price_sim   = co2_price_sim_st
    heat_pump       = heat_pump_st
    st_collector    = st_collector_st
        
    submission = [year, annual_elec_demand, annual_heat_demand, 
                    slp_type_elec, slp_type_heat, lat, lon, province,
                    elec_mix_old, heat_tech_old, heat_system, co2_price_sim,
                    pv_area, heat_pump, st_collector, st_area]

    # submission = {
    #     'year': year,
    #     'annual_elec_demand':annual_elec_demand,
    #     'annual_heat_demand':annual_heat_demand,
    #     'slp_type_heat':slp_type_heat,
    #     'slp_type_elec': slp_type_elec,
    #     'lat':lat,
    #     'lon':lon,
    #     'province':province,
    #     'elec_mix_old':elec_mix_old,
    #     'heat_tech_old':heat_tech_old,
    #     'heat_system':heat_system,
    #     'co2_price_sim':co2_price_sim,
    #     'pv_area':pv_area,
    #     'heat_pump':heat_pump,
    #     'st_collector':st_collector,
    #     'st_area':st_area,
    # }
        
    #st.write(submission)
    df = main_submit.submit(submission)
    df = df.reset_index()
    df['index'] = df['index'].astype(str, errors='raise')
    df['index'] = df['index'].apply(lambda x: dt.datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
    # --> main.submit function for running simulation with given user variables
    # --> if main.submit returns df --> makes plot easy!
    
    ''' Plotting'''
    with st.expander('Visualisation Settings', expanded = True):
       with st.form('Form2'):
            col1, col2 = st.columns(2)
            start_date = col1.date_input('Start Datum', df.iat[0, 0], min_value=df.iat[0, 0], max_value=df.iat[-1, 0])
            start_time = col1.slider('Start Uhrzeit', step=1, min_value=0, max_value=23, value=0)
            end_date = col2.date_input('End Datum', df.iat[-1, 0], min_value=df.iat[0, 0], max_value=df.iat[-1, 0])
            end_time = col2.slider('End Uhrzeit', step=1, min_value=0, max_value=23, value=23)

            submit2 = st.form_submit_button('Log Visualisation Settings')

    if submit2:
        start_time = str(start_time)+':00:00'
        start_time = dt.datetime.strptime(start_time, '%H:%M:%S')
        start_time = start_time.replace(year=start_date.year, month=start_date.month, day=start_date.day)

        end_time = str(end_time) + ':00:00'
        end_time = dt.datetime.strptime(end_time, '%H:%M:%S')
        end_time = end_time.replace(year=end_date.year, month=end_date.month, day=end_date.day)

        mask = (df['index'] >= start_time) & (df['index'] <= end_time)
        df = df[mask]
        
        with st.container():
            with st.expander('Visualisierung: Kompensation', expanded=False):
                fig = go.Figure(data=[go.Scatter(
                    x=df['index'], y=df['comp'], mode='lines')])
                fig.update_layout(
                    xaxis=dict(
                        rangeselector=dict(
                            buttons=list([
                                dict(count=1,
                                     step="day",
                                     stepmode="backward"),
                            ])
                        ),
                        rangeslider=dict(
                            visible=True
                        ),
                    )
                )
                st.plotly_chart(fig)

            with st.expander('Visualisierung: Preise (Differenz)', expanded=False):
                fig = go.Figure(data=[go.Scatter(
                    x=df['index'], y=df['price_diff'], mode='lines')])
                fig.update_layout(
                    xaxis=dict(
                        rangeselector=dict(
                            buttons=list([
                                dict(count=1,
                                     step="day",
                                     stepmode="backward"),
                            ])
                        ),
                        rangeslider=dict(
                            visible=True
                        ),
                    )
                )
                st.plotly_chart(fig)

            with st.expander('Visualisierung: Preise (Differenz inkl. CO2-Preis)', expanded=False):
                fig = go.Figure(data=[go.Scatter(
                    x=df['index'], y=df['total_diff'], mode='lines', name='total_diff')])
                fig.update_layout(
                    xaxis=dict(
                        rangeselector=dict(
                            buttons=list([
                                dict(count=1,
                                     step="day",
                                     stepmode="backward"),
                            ])
                        ),
                        rangeslider=dict(
                            visible=True
                        ),
                    )
                )
                st.plotly_chart(fig)
# %%
