#%%from http.client import TOO_MANY_REQUESTS
import json
from tracemalloc import start
import pvlib as pv
import numpy as np
import pandas as pd
import requests
from feedinlib import era5
import cdsapi
from feedinlib.open_FRED import Weather, defaultdb
from shapely.geometry import Point

#%%
# c = cdsapi.Client()
# c.retrieve("reanalysis-era5-pressure-levels",
# {
# "variable": "temperature",
# "pressure_level": "1000",
# "product_type": "reanalysis",
# "year": "2008",
# "month": "01",
# "day": "01",
# "time": "12:00",
# "format": "grib"
# }, "download.grib")

#%% TMY Data (PVGIS)
def tmy_data(lat, lon):
    tmy_data_api = pv.iotools.get_pvgis_tmy(
        latitude= lat,
        longitude= lon,
        map_variables= True
    )
    tmy = tmy_data_api[0]
    
    return tmy

def wind_weather_openfred(lat, lon, year, hub_height):
    start_date = str(year) + '-1-1'
    end_date = str(year+1) + '-1-1'
    location = Point(lon, lat)
    raw_data_wind = Weather(
        start=start_date,
        stop=end_date, 
        locations=[location],
        heights= [hub_height],
        variables = "windpowerlib",
        **defaultdb())
    return raw_data_wind


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

def era5_weather(lat, lon, year, variable):
    target_file = f'weather_era5_{variable}.nc'
    start_date, end_date = f'{year}-01-01', f'{year+1}-01-01'
    ds = era5.get_era5_data_from_datespan_and_position(
        variable=variable,
        start_date=start_date, end_date=end_date,
        latitude=lat, longitude=lon,
        target_file=target_file)

    return ds