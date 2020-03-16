import numpy as np
import pandas as pd
from weatherClass import   weatherClass
from IdentifierClass import   identifierClass
from eventsClass import   eventsClass
import datetime

### load some data:

#read the ticket+complaint data, combined for location:
# events fields: date, lat, lng, address, identifier, index
temp = pd.read_csv('/Users/nbechor/Insight/noslipwalk/noslipwalk/features/negative_labels_5_d_15_with_identifier.csv')
events = eventsClass(temp)


# read the identifier to weather data:
# this is the the result of the nearest neighbor for weather. Each
# key address has an identifier, that identifier is tied to the different
# lat longs of a given address, and to the closest weather data grid point
# fields: lat, lon, identifier as index
temp = pd.read_csv('/Users/nbechor/Insight/noslipwalk/noslipwalk/features/identifier2weatherloc.csv')
identifier2weatherloc = identifierClass(temp)


# weather_features fields:
# fields: time, lat, lon, frost indicator,thaw indicator, rain indicator,
# snow indicator, rain amount, snow amount
temp = pd.read_csv('/Users/nbechor/Insight/noslipwalk/noslipwalk/features/weather_features.csv')
weather_features = weatherClass(temp)
weather_features.df = weather_features.df.fillna(0)
print(weather_features.df)

newPointEvents = pd.DataFrame()  # we'll add to this in the loop (the main output)

# going over all identifiers, and events for each:
identifiers = events.df['identifier'].unique().astype('int').tolist()


new_events = pd.DataFrame()
for identifier in identifiers:
    pointEvents = events.df[events.df['identifier'] == identifier]
    lat,lon,errFlag = identifierClass.latLonFromRecord(identifier2weatherloc,identifier)
    if (~errFlag):
        pointWeather = weatherClass.weatherByLatLon(weather_features,lat,lon)

        # now need to go over events and get weather for each of them:
        for i in range(0,pointEvents.shape[0]):
            date = pointEvents['date'].iloc[i]
            time_struct = date.timetuple()
            year = time_struct.tm_year
            doy = time_struct.tm_yday
            weather = pointWeather[pointWeather['date']==date]
            if (~weather.empty):
                # switch the lat lon in the weather for the lat lon of the event:
                try:
                    weather['lat'] = pointEvents['lat'].iloc[i]
                    weather['lon'] = pointEvents['lng'].iloc[i]
                    weather['address'] = pointEvents['address'].iloc[i]
                    weather['label'] = 0
                    weather['year'] = year
                    weather['day of year'] = doy
                    weather['year + day of year'] = year+doy
                    new_events = new_events.append(weather)
                except:
                    print(weather.shape)
                    print('something off for date',date,'identifier',identifier)


print(new_events)
new_events.to_csv('/Users/nbechor/Insight/noslipwalk/noslipwalk/features/features_label0.csv')
