''' This code gives an index for each of the lat/lon weather grid points. It
uses nearest neighbor to assign each address in Cambridge's master_address
the index for the closest weather grid point.
Doing this once and ahead of time (offline) makes the model and ingesting new
data (such as complaints and tickets) run faster
More info in the notebook ConnectingAddress2WeatherGrid.ipynb'''

import pandas as pd
import numpy as np

def find_nearest_weather_point(latI, lonI):
    from geopy.distance import geodesic
    minDist = 4000
    for i in range(0, N):
        lat = weather_info.lats[i]
        lon = weather_info.lons[i]
        dist = geodesic([lat, lon], [latI, lonI]).meters
        if dist < minDist:
            minDist = dist
            nearestIdentifier = weather_info.identifier[i]
    return nearestIdentifier


# loading city addresses:
masterAddress = pd.read_csv('/Users/nbechor/Insight/SlipperySlope/data/external//Master_Addresses_List.csv')

# Reading the weather grid:
import sys
sys.path.insert(0, '/Users/nbechor/Insight/SlipperySlope/src/data')

from weatherData import weatherData

# weather_info includes the fields lats, lons, which are the weather data grid coordinates
# and their identifiers:
weather_info = weatherData()
identifierLocation = pd.DataFrame()
identifierLocation['Building ID'] = masterAddress['Building ID'].unique()

identifierLocation['lat'] = masterAddress['Latitude']
identifierLocation['lon'] = masterAddress['Longitude']
identifierLocation['identifier'] = np.zeros(identifierLocation.shape[0]).astype('int')

N = len(weather_info.identifier)
for i in range(0, identifierLocation.shape[0]):
    identifierLocation['identifier'].iloc[i] = find_nearest_weather_point(identifierLocation['lat'].iloc[i],
                                                                          identifierLocation['lon'].iloc[i])
    if (i/100==round(i/100)):
        print(i)

identifierLocation.to_csv('/Users/nbechor/Insight/SlipperySlope/data/processed/BldgID2WeatherIdentifier.csv')