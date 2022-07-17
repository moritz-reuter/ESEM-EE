#%%from http.client import TOO_MANY_REQUESTS
import json
from tracemalloc import start
import pvlib as pv
import numpy as np
import pandas as pd
import requests

#%% TMY Data (PVGIS)
def tmy_data(lat, lon):
    tmy_data_api = pv.iotools.get_pvgis_tmy(
        latitude= lat,
        longitude= lon,
        map_variables= True
    )
    tmy = tmy_data_api[0]
    
    return tmy

def sky_data(lat, lon, year):
    query = {
        'date' : str(year) + "-01-01",
        'last_date': str(year+1) + "-01-01",
        'lat': lat,
        'lon': lon
    }
    response_API = requests.get("https://api.brightsky.dev/weather", params=query)
    data = response_API.text
    sky_data_api =  json.loads(data)
    sky = pd.DataFrame.from_dict(sky_data_api["weather"][0:8760]) 

    return sky