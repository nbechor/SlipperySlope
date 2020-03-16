# Building thaw/freeze events from the weather
# and a snow/rain feature (how much snow/rain and when
# but probably best... is the snow cover imaging data...

import pandas as pd
import numpy as np
import math

daily = pd.read_csv('/Users/nbechor/Insight/noslipwalk/notebooks/DarkSky_2007_to_2019_Full.csv')

# relevant fields: lat, lon, precipAccumulation,humidity,dewPoint,
# apparentTemperatureMin, Max, MinTime, MaxTime same for Temperature
# cloudCover, windGust winGustTime, windSpeed, precipIntensityMaxTime,time

# For now, first step: thaw/freeze indicator. Make 2, one from apparentTemp and one from Temp

def predictFrost():
    '''function to tag drops in temperature below 32F as freeze events,
    warming up above 32F as thawing events, with time'''
    N = df.shape[0]
    ThawFreeze = np.zeros(N)
    freezeIndicatorInt = pd.DataFrame()
    freezeIndicatorInt['time'] = df['time']
    freezeIndicatorInt['lat'] = df['lat']
    freezeIndicatorInt['lon'] = df['lon']
    freezeIndicatorInt['frost indicator'] = pd.Series(np.zeros(N))
    freezeIndicatorInt['thaw indicator'] = pd.Series(np.zeros(N))
    freezeIndicatorInt['rain indicator'] = pd.Series(np.zeros(N))
    freezeIndicatorInt['snow indicator'] = pd.Series(np.zeros(N))
    freezeIndicatorInt['rain amount'] = pd.Series(np.zeros(N))
    freezeIndicatorInt['snow amount'] = pd.Series(np.zeros(N))
    freezeIndicatorInt['snow so far'] = pd.Series(np.zeros(N))
    freezeIndicatorInt['thaw so far'] = pd.Series(np.zeros(N))
    freezeIndicatorInt['last snow amount'] = pd.Series(np.zeros(N))
    freezeIndicatorInt['time since last freeze'] = pd.Series(np.zeros(N))
    freezeIndicatorInt['time since last snow'] = pd.Series(np.zeros(N))

    lastFreezeTime = df['sunriseTime'].iloc[0]
    freezeIndicator = False
    tempMinYesterday = df.temperatureLow.iloc[0]
    freezeIndicator = False
    thawIndicator = False
    lastSnowTime = df['sunriseTime'].iloc[0]-365*24*60*60
    snowAmount = 0
    tempMinTime=df['temperatureLowTime'].iloc[0]
    cumuSnow=0
    cumuThaw = 0

    for i in range(0,N):
    # initializing if beginning of year:
    # Getting the freeze/thaw indicators for today
        yesterdayTime = tempMinTime
        freezeIndicatorYesterday = freezeIndicator
        thawIndicatorYesterday = thawIndicator
        freezeIndicator= False
        thawIndicator = False
        tempMinToday = df.temperatureLow.iloc[i]  ## want overnight low
        tempMaxToday = df.temperatureMax.iloc[i]
        # did it freeze or thaw today?
        tempMinTime = df.temperatureLowTime.iloc[i]
        if (tempMinTime-yesterdayTime>4*30*24*60*60):
            # means that we started a new winter and need to zero cumulative features
            cumuSnow = 0
            cumuThaw = 0

        if (tempMinToday<=32.0) & (tempMaxToday>32.0):
            tempMaxTime = df.temperatureMaxTime.iloc[i]
            if (tempMaxTime<tempMinTime):
                freezeIndicator = True
                thawIndicator = False
                lastThawTime = tempMaxTime
            else:
                # maybe it was cold first, then warmed up:
                freezeIndicator=False
                thawIndicator=True
                lastFreezeTime=tempMinTime
        # did it freeze since yesterday?
        if (tempMinYesterday>32.0) & (tempMaxToday<=32.0):
            freezeIndicator = True
            thawIndicator=False
            lastFreezeTime = tempMaxTime
        elif (tempMinYesterday>32.0) & (tempMinToday<=32.0): ## poribably redundent..
            freezeIndicator = True
            thawIndicator=False
            lastFreezeTime = tempMinTime
        # maybe it was freezing yesterday, but warmed up today:
        if (tempMinYesterday<=32.0) & (tempMinToday>32.0):
            thawIndicator = True
            freezeIndicator=False
            lastThawTime = tempMinTime
        elif (tempMinYesterday<=32) & (tempMaxToday>32):
            thawIndicator = True
            freezeIndicator=False
            LastThawTime = tempMaxTime
        # could be that there was a thaw-freeze cycle yesterday, and now remained frozen:
        if (tempMaxToday<32)&(freezeIndicatorYesterday):
            thawIndicator = False
            freezeIndicator = True
        if thawIndicator:
            cumuThaw += 1
        # Now we have what we need for feature engineering...:
        if freezeIndicator:
            freezeIndicatorInt['frost indicator'].iloc[i]=1
        else:
            freezeIndicatorInt['frost indicator'].iloc[i] = 0
        if thawIndicator:
            freezeIndicatorInt['thaw indicator'].iloc[i] = 1
        else:
            freezeIndicatorInt['thaw indicator'].iloc[i] = 0

        # keeping today's value for tomorrow:
        tempMinYesterday = tempMinToday

        # while we're at it, did it rain today?
        precipIndicator = df['precipIntensity'].iloc[i]
        if (precipIndicator>0):
            precipType = df['precipType'].iloc[i]
            if (precipType=='rain'):
                rainAmount = df['precipAccumulation'].iloc[i]
                if math.isnan(rainAmount):
                    freezeIndicatorInt['rain amount'].iloc[i] = 0
                else:
                    freezeIndicatorInt['rain amount'].iloc[i] = rainAmount
                    freezeIndicatorInt['rain indicator'].iloc[i] = 1
                if i<N-1 & ~math.isnan(rainAmount):
                    # taking into account potential residual moisture into tomorrow
                    precipTime = df['precipIntensityMaxTime'].iloc[i]
                    sunsetTime = df['sunsetTime'].iloc[i]
                    if (precipTime>sunsetTime):
                        freezeIndicatorInt['rain indicator'].iloc[i+1] =0.5
            else:  # putting sleet etc with the snow category
                snowAmount = df['precipAccumulation'].iloc[i]
                if math.isnan(snowAmount):
                    snowAmount = 0
                else:
                    cumuSnow += snowAmount
                    lastSnowTime = df['precipIntensityMaxTime'].iloc[i]
                    freezeIndicatorInt['snow amount'].iloc[i] = df['precipAccumulation'].iloc[i]
                    freezeIndicatorInt['snow indicator'].iloc[i] = 1
                #print('lastSnowTime:',lastSnowTime,type(lastSnowTime))
        else:
            snowAmount =0
            freezeIndicatorInt['rain indicator'].iloc[i] = 0
            freezeIndicatorInt['rain amount'].iloc[i] = 0
            freezeIndicatorInt['snow indicator'].iloc[i] = 0
        freezeIndicatorInt['time since last snow'].iloc[i] = ((-lastSnowTime+tempMinTime)/60/60/24)
        freezeIndicatorInt['time since last freeze'].iloc[i] = ((-lastFreezeTime+tempMinTime)/60/60/24)
        freezeIndicatorInt['last snow amount'].iloc[i] = snowAmount
        freezeIndicatorInt['snow so far'].iloc[i] = cumuSnow
        freezeIndicatorInt['thaw so far'].iloc[i] = cumuThaw
        freezeIndicatorInt = freezeIndicatorInt.fillna(0)
    return freezeIndicatorInt

lats = daily['lat'].unique()
lons = daily['lon'].unique()

## main loop over longitudes and latitudes. Each location
# has its own weather...
frost_feature = pd.DataFrame()
for lat in lats:
    for lon in lons:
        df = daily[daily['lat']==lat]
        df = df[df['lon']==lon]
        df['time'] = pd.to_datetime(df['time'])
        df = df.sort_values(by=['time'])
        if not df.empty:
        # now have all dates for a location
            new_df = predictFrost()
            frost_feature = frost_feature.append(new_df)

frost_feature.to_csv('weather_features.csv')





