#%%
import mimetypes
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
heat_system_data    = helper_functions.sheet_xl(data, 'heat_system')
heat_system_options = heat_system_data['name'].to_list() #make flexible via 
co2_data            = helper_functions.sheet_xl(data, 'co2')
co2_price_options   = co2_data['name'].to_list()
heat_pump_options   = tech_data[tech_data.index.str.contains('HP_')]['name'].to_list()
# st_tech_options     = helper_functions.sheet_xl(data, 'soltherm_data')['name'].to_list()
soltherm_data       = helper_functions.sheet_xl(data, 'soltherm_data')
st_tech_options     = ['Vakuumröhrenkollektor', 'Flachkollektor']

#%%
#GUI
st.title('CO2-Kompensationstool')

with st.expander('Programmbeschreibung'):
    st.header('Informationen zum bedienen des Tools')
    st.write('''
                Viele deutsche Verbraucher*innen beschäftigt derzeit die Frage: "was würde passieren wenn ich meinen derzeitigen Wärme und Strombedarf ohne Gas decken müsste?" \n
                Obwohl dieses Tool nicht primär dafür entwickelt wurde, diese Frage zu beantworten, hat es dennoch manche hilfreiche Antworten parat.
                Der Sinn und Zweck dieses Tools besteht in aller erster Linie darin, manchen Verbraucher*innen zu veranschaulichen was für Potenziale es bei Ihnen zu Hause gibt, um erneuerbare Energien (EE) einzusetzen. 
                Diese Potenziale beziehen sich sowohl auf die CO2-Kompensation als auch auf die wirtschaftlichen Auswirkungen, die eine Einbindung von EE zur Folge haben könnten (auf maximal ein Jahr bezogen). \n
                Dieses Tool ist (noch) nicht ein Investitions-Tool: es kann niemandem sagen was die optimale Auslegung einer PV-Anlage wäre, ob sich Sole- oder Luft-Wärmepumpen besser eignen, oder ob ein Vakuumröhrenkollektor 
                besser ist als ein Flachkollektor bei dem ein oder anderen Standort. \n
                Das Tool wird für Sie, nach Eingabe der nötigen Simulationsvariablen, berehnen wie viel CO2 Sie dadurch kompensiert haben, dass Sie sowohl Photovoltaik zur Stromerzeugung als auch Solarthermie zur Wärmeerzeugung nutzen
                und ihren jährlichen Gasverbrauch *komplett* durch die Nutzung einer Wärmempumpe ersetzt haben. Hierzu werden auch Ersparnisse oder Mehrkosten berechnet, die sich auf Ihre Verbrauchsausgaben beziehen aber nicht die 
                nötigen Anschaffungskosten der einzelnen EE-Anlagen  miteinbeziehen können. \n
                Falls Sie mehr über die Programmierung des Tools erfahren möchten, steht Ihnen eine detaillierte "Programmbeschreibung" zur Verfügung (clicken Sie einfach auf den Button). 
                Dieser enthält auch Informationen zum Bedienen des Tools als auch dessen Annahmen und Empfehlungen für die Weiterentwicklung. Viel Spaß!
                ''')
    with open("Programmbeschreibung.pdf", "rb") as instruct_pdf:
        PDFbyte = instruct_pdf.read()
    st.download_button(label       = 'Programmbeschreibung', 
                        data        = PDFbyte,
                        file_name   = 'instruct.pdf')
                        
                    
                    
with st.expander('Simulationsvariablen', expanded=True):
    with st.form('Submit'):
        tab1,tab2,tab3, tab4 = st.tabs(['Basis Info', 'Verbraucher Info', 'Aktuelle Tech.', 'Zukunfts Tech.'])
        
        with tab1:
            st.header('Basis Informationen')
            year                    = st.number_input(label='(Simulations-)Jahr', step=1, min_value=2010, max_value=2022, value=2022, key='year')
            # number_household    = col1.number_input(label='Anzahl der Personen im Haushalt', step=1, min_value=1, max_value=10, value=2,key='occupants')     
            lat                     = st.number_input(label='Breitengrad', step=1., value=52.52, key='lat')
            # st.write('Der aktuelle Breitengrad ist: ', lat)
            lon                     = st.number_input(label='Längengrad', step=1., value=13.41, key='lon')
            # st.write('Der aktuelle Längengrad ist: ', lon)
            province_st             = st.selectbox(label='Bundesland', options = prov_options,key='province', index = 3)    #see list of provinces in XL
            st.info('Nutzen Sie die Karte, um zu prüfen ob Ihre Koordinaten Eingabe richtig war!', icon="ℹ️")
            location = pd.DataFrame(np.array([[float(lat), float(lon)]]), columns=['lat', 'lon'])
            loc = st.map(location)
        
        with tab2:
            st.header('Verbraucher Informationen')
            annual_elec_demand      = st.number_input(label='Stromverbrauch (jährlich, kWh)', step=100, min_value=1, max_value=100000, value=1500,key='annual_elec_demand')       
            annual_heat_demand      = st.number_input(label='Gasverbrauch (Raumwärme, Warmwasser) (jährlich, kWh)', step=100, min_value=1, max_value=100000, value=6000,key='annual_heat_demand')       
            slp_type_elec_st        = st.selectbox(label='Standardlastprofil Strom (i.e., privat or geschäftlich)', options = elec_slp_options, key='slp_type_elec', index = 7)   
            slp_type_heat_st        = st.selectbox(label='Standardlastprofil Gas (i.e., privat or geschäftlich)', options = heat_slp_options, key='slp_type_heat', index = 0)  
        
        with tab3:
            st.header('Aktuelle Heiz- und Stromtechnologien')
            elec_mix_old_st         = st.selectbox(label='Stromtarif - Aktuell', options = elec_mix_options, key='elec_mix_old', index = 1) 
            heat_tech_old_st        = st.selectbox(label='Heizungstechnnologie - Aktuell', options = heat_tech_options, key='heat_tech_old', index = 0) #'CHB' # read in from list of heat_techs
            heat_system_st          = st.selectbox(label='Heizungssystem (zur Berechnung der Heizungsvorlauftemperatur)', options = heat_system_options, key='heat_system', index = 0) #'HKS'
        
        with tab4:
            st.header('Zukunftsgerichtete Technologien und CO2-Preis-Szenarien')
            st.info('Nutzen Sie gerne unsere Infos zu den unterschiedlichen EE auf unserer Website, um mehr über die technischen und wirtschaftliche Hintergründe der einzelnen Technologien zu erfahren', icon="ℹ️")
            pv_area                 = st.number_input(label='PV-Anlagenfläche', step=1., value=10., key='pv_area') # 10 # m2
            heat_pump_st            = st.selectbox(label='Wärmepumpe', options = heat_pump_options, key='heat_pump',index = 0) #'HP_air' # HP_ground, HP_water
            st_collector_st         = st.selectbox(label='Solarthermie Technologie (Nicht-konzentriert)', options = st_tech_options, key='st_collector', index = 0) 
            st_area                 = st.number_input(label='Solarthermie-Anlagenfläche', step=1., value=10., key='st_area') # 10 # m2
            co2_price_sim_st        = st.selectbox(label='CO2-Reduktionspfad', options = co2_price_options, key='co2_price_sim', index = 0)# 'BAU' # €/tCO2 --> write function to determine price per kg for sim selection
            st.info('''Die einzelnen Reduktionspfade setzen einen bestimmten CO2-Preis voraus (in Euro je Tonne CO2-Äquivalente). 
                        Dieser liegt bei dem Business-As-Usual Szenario bei ca. 35 €/tCO2.
                        Ein CO2-Preis, der (laut manchen Simulationen) das erfüllen der Ziele des Pariserklimaabkommens zur Folge haben könnt, 
                        nämlich die Erderwärmung unter 1.5 °C bzw. 2 °C zu halten, würde bei ca. 275 €/tCO2 bzw. 75 €/tCO2 liegen.
                        Ein CO2-Preis, der (laut manchen Simulationen) Deutschland bis 2045 Klimaneutral machen könnte, wird bei 505.13 €/tCO2 festgelegt.
                         ''', icon="ℹ️")

        
        submit1 = st.form_submit_button('Eingabe speichern')

GUI1 = st.checkbox('Simulation beginnnen')

if GUI1:
    slp_type_elec   = elec_slp_data.index[elec_slp_data['name'] == slp_type_elec_st][0]
    slp_type_heat   = heat_slp_data.index[heat_slp_data['name'] == slp_type_heat_st][0]
    elec_mix_old    = tech_data.index[tech_data['name'] == elec_mix_old_st][0]
    heat_tech_old   = tech_data.index[tech_data['name'] == heat_tech_old_st][0]
    heat_system     = heat_system_data.index[heat_system_data['name'] == heat_system_st][0]
    co2_price_sim   = co2_data.index[co2_data['name'] == co2_price_sim_st][0]
    heat_pump       = tech_data.index[tech_data['name'] == heat_pump_st][0]
    st_collector    = soltherm_data.index[soltherm_data['name'] == st_collector_st][0]
    province        = prov_data.index[prov_data['value'] == province_st][0]
        
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
    
    #Plotting#
    st.header('Ergebnisse')
    with st.expander('Visualisation Settings', expanded = True):
       with st.form('Form2'):
            col1, col2 = st.columns(2)
            start_date = col1.date_input('Start Datum', df.iat[0, 0], min_value=df.iat[0, 0], max_value=df.iat[-1, 0])
            start_time = col1.slider('Start Uhrzeit', step=1, min_value=0, max_value=23, value=0)
            end_date = col2.date_input('End Datum', df.iat[-1, 0], min_value=df.iat[0, 0], max_value=df.iat[-1, 0])
            end_time = col2.slider('End Uhrzeit', step=1, min_value=0, max_value=23, value=23)

            submit2 = st.form_submit_button('Visualisierung beginnen')

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
                    ),
                    yaxis_title = "Kompensiertes CO2 (in kg)",
                    xaxis_title = "Zeit"
                )
                st.plotly_chart(fig)

            with st.expander('Visualisierung: Kosten', expanded=False):
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
                    ),
                    yaxis_title = "Eingesparte Kosten (pos.) oder Mehrkosten (neg.) (in €)",
                    xaxis_title = "Zeit"
                )
                st.plotly_chart(fig)

            with st.expander('Visualisierung: Kosten (inkl. CO2-Preis)', expanded=False):
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
                    ),
                    yaxis_title = "Eingesparte Kosten (pos.) oder Mehrkosten (neg.) (in €)",
                    xaxis_title = "Zeit"
                )
                st.plotly_chart(fig)
                # st.info('''Vielleicht wundern Sie sich warum ihre Ersparnisse so gering ausfallen, selbst bei Einbezug der CO2-Kompensation.
                #             ''')
            
            with st.expander('Ergebnisse: Zusammenfassung (für den gewählten Zeitraum)', expanded = False):
                df.columns = ['index','Kompensation (in kg CO2)', 'Ersparnisse (in €)', 'Ersparnisse (in € inkl. CO2-Preis)']

                df_results = df.sum()
                df_results.columns = ['Summierte Werte (für den ausgewählten Zeitraum)']
                st.table(df_results)
# %%
