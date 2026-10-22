#%% Packages
import functools
import pandas as pd
import requests

API_URL = 'https://api.energy-charts.info/price'

#%% Day-ahead spot prices (Energy-Charts, Bundesnetzagentur | SMARD.de, CC BY 4.0)
@functools.lru_cache(maxsize=8)
def _spot_raw(year):
    query = {'bzn': 'DE-LU', 'start': f'{year}-01-01', 'end': f'{year}-12-31'}
    response = requests.get(API_URL, params=query, timeout=30)
    response.raise_for_status()
    js = response.json()
    prices = pd.Series(
        js['price'],
        index = pd.to_datetime(js['unix_seconds'], unit='s', utc=True),
        dtype = float)
    return prices.dropna()

def spot_price_hourly(year, time_index):
    '''
    Hourly day-ahead price in ct/kWh aligned to time_index (local time, no leap day).
    Hours without published prices (e.g. the rest of the current year) are filled with the
    mean price of the same hour of day. Negative prices are set to 0 (no payment for surplus feed-in).
    Raises if the API is not reachable --> caller decides on fallback.
    '''
    raw = _spot_raw(year)                                           # EUR/MWh, 15 min (since 10/2025) or 1 h
    hourly = raw.resample('H').mean()
    hourly.index = hourly.index.tz_convert('Europe/Berlin').tz_localize(None)
    hourly = hourly.groupby(level=0).mean()                         # merge duplicated hour at DST change
    prices = hourly.reindex(time_index)

    hour_mean = prices.groupby(prices.index.hour).mean()
    prices = prices.fillna(pd.Series(prices.index.hour, index=prices.index).map(hour_mean))

    return (prices / 10).clip(lower=0)                              # EUR/MWh --> ct/kWh
