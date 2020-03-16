import pandas as pd
import numpy as np
import datetime
class weatherClass():
    """
    holds weather initial features DataFrame and provides operations on it
    fields: time, lat, lon, frost indicator,thaw indicator, rain indicator,
    snow indicator, rain amount, snow amount. initializeTime returns time as datetime64
    and date as dt.date
    instance includes at least data, which is initialized w a filename (can be with path)
    """
    import pandas as pd
    import numpy as np

    def __init__(self,df):
        self.df = df
        self.df['time']=pd.to_datetime(self.df['time'])
        self.df['date']=self.df['time'].dt.date

    def __str__(self):
        return self.df.shape

    def initializeTime(self):
        self.df['time']=pd.to_datetime(self.df['time'])
        self.df['date'] = self.df['time'].dt.date
        return self

    def eventCheck(df,weatherEvent):
        """for weather event ('snow', 'ice', 'rain', 'frost', 'thaw),
        returns relevant parameters: last date, accumulated amount, and a flag
        eventFlag=True if event happened in the data segment"""
        rain = 'rain'
        frost = 'frost'
        snow = 'snow'
        thaw = 'thaw'
        sleet='sleet'
        minDate = datetime.date(1800,1,1)
        eventFlag = False
        eventDate = minDate
        eventWeight = 0
        eventFlag=False

        if ((weatherEvent in snow) or (weatherEvent in rain) or (weatherEvent in sleet)):
            event_str = weatherEvent + ' indicator'
            inds = df[df[event_str] == 1]
            if ~(inds.empty):
                amount_str = weatherEvent + ' amount'
                eventWeight = inds[amount_str].sum()
                if (inds.shape[0]>0):
                    eventDate = inds['date'].iloc[-1]
                else:
                    eventDate = inds['date']
                eventFlag = True

        elif ((weatherEvent in thaw) | (weatherEvent in frost)):
            event_str = weatherEvent + ' indicator'
            inds = df[df[event_str]==1]
            if ~(inds.empty):
                eventFlag = True
                if (inds.shape[0]>1):
                    eventDate = inds['date'].iloc[inds.shape[0]]
                elif (inds.shape[0]==1):
                    eventDate=inds['date'].values
                eventWeight = inds.shape[0]+1
        else:
            print('Unknown weather event:',weatherEvent)

        return eventFlag, eventDate, eventWeight

    def getWeatherSegment(date0, j,df):
        """get the weather from date0 to thdate at iloc j"""
        eventDate = df['date'].iloc[j]
        weatherSegment = df[df['date'] <= eventDate]
        print('date0 in function:',date0)
        print('weatherSegment:')
        print(weatherSegment)
        weatherSegment = weatherSegment[weatherSegment['date'] >= date0]
        return weatherSegment

    def weatherByLatLon(self,Lat,Lon):
        """gets all the weather for a given lat lon point in the weather grid"""
        weatherOut = self.df[self.df['lat']==Lat]
        weatherOut = weatherOut[weatherOut['lon']==Lon]
        return weatherOut


    def predictFrost(df):
        N = df.shape[0]
        ThawFreeze = np.zeros(N)
        freezeIndicatorInt = pd.DataFrame()
        freezeIndicatorInt['time'] = df['time']
        freezeIndicatorInt['lat'] = df['lat']
        freezeIndicatorInt['lon'] = df['lon']
        freezeIndicatorInt['frost indicator'] = pd.Series(np.zeros(N))
        try:
            lastFreezeTime = df['sunriseTime'].iloc[0]
        except:
            lastFreezeTime = df['sunriseTime'].values
        freezeIndicator = False
        try:
            tempMinYesterday = df.temperatureLow.iloc[0]
        except:
            tempMinYesterday = df.temperatureLow.values
        for i in range(0,N):
       # initializing if beginning of year:
        # Getting the freeze/thaw indicators for today
        # If it wasn't freezing conditions yesterday..:
            freezeIndicatorYesterday = freezeIndicator
            thawIndicatorYesterday = thawIndicator

            tempMinToday = df.temperatureLow.iloc[i]  ## want overnight low
            tempMaxToday = df.temperatureMax.iloc[i]
            if ~freezeIndicator:
            # did it freeze today?
                tempMinTime = df.temperatureLowTime.iloc[i]
                if (tempMinToday<=32.0) & (tempMaxToday>32.0):
                    tempMaxTime = df.temperatureMaxTime.iloc[i]
                    if (tempMaxTime<tempMinTime):
                        freezeIndicator = True
                        thawIndicator = False
                        lastThawTime = tempMaxTime
                    else:
                        freezeIndicator=False
                        thawIndicator=True
                        lastFreezeTime=tempMinTime
                # did it freeze since yesterday?
                if (tempMinYesterday>32.0) & (tempMaxToday<=32.0):
                    freezeIndicator = True
                    thawIndicator=False
                    lastFreezeTime = tempMaxTime
                elif (tempMinYesterday>32.0) & (tempMinToday<=32.0): ## oribably redundent..
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
            if (tempMaxToday < 32) & (freezeIndicatorYesterday):
                thawIndicator = False
                freezeIndicator = True
            # we kind of want to know if there was snow on the ground..?
            # want: how much snow fell since last thaw..? (accumulated)

            # Now we have what we need for feature engineering...:
            if freezeIndicator:
                freezeIndicatorInt['frost indicator'].iloc[i]=1
            else:
                freezeIndicatorInt['frost indicator'].iloc[i] = 0
            tempMinYesterday = tempMinToday

        return freezeIndicatorInt



