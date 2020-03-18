import numpy as np
import pandas as pd
from weatherClass import weatherClass
from identifierClass import identifierClass
from eventsClass import eventsClass
import datetime
import sys
sys.path.insert(0, '/Users/nbechor/Insight/SlipperySlope/src/data')
from weatherData import weatherData


def initFlags():
    isFrost = False
    wasFrost = False
    isThaw = False
    wasThaw = False
    return isFrost,wasFrost,isThaw,wasThaw

def getFlags(weather,dow):
    if (weather['frost indicator'].iloc[0]==1):
        isFrost=True
    else:
        isFrost=False
    if (weather['thaw indicator'].iloc[0]==1):
        isThaw=True
    else:
        isThaw=False
    if (dow<5):
        notWeekend=True
    else:
        notWeekend=False
    return isFrost, isThaw, notWeekend

def checkDates(pointEvents,date,window):
    import pandas as pd
    import datetime
    window = datetime.timedelta(days=window)

    inds = pointEvents[pointEvents['date']<date+window]
    inds = inds[inds['date']>date-window]
    if len(inds)>0:
        withinDates=True
    else:
        withinDates=False
    return withinDates

def drawSample(pointEvents,weather,year,doy):
    ind = np.random.randint(0,(pointEvents.shape[0]-1))
    tmpLabel = weather
    tmpLabel['lon'].iloc[0] = pointEvents['lon'].iloc[ind]
    tmpLabel['lat'].iloc[0] = pointEvents['lat'].iloc[ind]
    tmpLabel['Building ID'] = pointEvents['Building ID'].iloc[ind]
    tmpLabel['label'] = 0
    tmpLabel['year'] = year
    tmpLabel['day of year']= doy
    tmpLabel['year + day of year'] = year + doy/365
    return tmpLabel

### load some data:

#read the ticket+complaint data, combined for location:
# events fields: date, lat, lon, address, identifier, index
tickets_feature=pd.read_csv('/Users/nbechor/Insight/SlipperySlope/data/interim/tickets_label.csv')
#complaintsH = pd.read_csv('/Users/nbechor/Insight/SlipperySlope/data/interim/historic_complaints_label.csv')
#complaints = pd.read_csv('/Users/nbechor/Insight/SlipperySlope/data/interim/Complaints_label.csv')
fields = ['Unnamed: 0','Unnamed: 0.1']
#complaints=complaints.drop(columns=fields)
tickets = tickets_feature.drop(columns=fields)
#complaintsH = complaintsH.drop(columns=fields)
events = eventsClass(tickets)


# read the identifier to weather data:
# this is the the result of the nearest neighbor for weather. Each
# key address has an identifier, that identifier is tied to the different
# lat longs of a given address, and to the closest weather data grid point
# fields: lat, lon, identifier as index
temp = pd.read_csv('/Users/nbechor/Insight/SlipperySlope/data/processed/BldgID2WeatherIdentifier.csv')
identifier2weatherloc = identifierClass(temp)


# weather_features fields:
# fields: time, lat, lon, frost indicator,thaw indicator, rain indicator,
# snow indicator, rain amount, snow amount
temp = pd.read_csv('/Users/nbechor/Insight/SlipperySlope/data/interim/weather_features.csv')
weather_features = weatherClass(temp)
weather_features.df = weather_features.df.fillna(0)

weather_info = weatherData()
weather_lats = weather_features.df['lat'].unique()
weather_lons = weather_features.df['lon'].unique()

newPointEvents = pd.DataFrame()  # we'll add to this in the loop (the main output)

# going over all identifiers, and events for each:
identifiers = events.df['identifier'].unique().astype('int').tolist()

# window in time with which to cluster ticket/comlaint dates:
window = 5

# locations to sample when there is frost but no complaints in window:
labelsPerFrost = 1

# between 1 and 10, how many of the days without frost to randomly throw out
# originally, there are 144K days without frost in the dataset. (rand>7=>keep)
cutNoFrostValue=7
# locations to sample when there is no frost and no complaints in window:
labelsPerNoFrost = 1

count_is_frost = 0
count_is_not_frost = 0
count_problem = 0
new_events = pd.DataFrame()
for identifier in identifiers:
    pointEvents = events.df[events.df['identifier'] == identifier]
    # weather_features already sorted by time
    if (pointEvents.shape[0]>0):
        lat,lon,errFlag = identifierClass.latLonFromRecord(identifier2weatherloc,identifier)
        if (~errFlag):
            pointWeather = weatherClass.weatherByLatLon(weather_features.df, weather_lats, weather_lons, lat, lon)
            # building the lat/lons database for this location:
            # now need to go over weather:
            isFrost, wasFrost, isThaw, wasThaw = initFlags()
            lastYear=2007
            # running over time for the current location's weather:
            for i in range(0,pointWeather.shape[0]):
                date = pointWeather['date'].iloc[i]
                time_struct = date.timetuple()
                year = time_struct.tm_year
                doy = time_struct.tm_yday
                dow = time_struct.tm_wday  # monday is 0
                # are we in a new winter season?
                if (year-lastYear>0.5):
                    isFrost, wasFrost, isThaw, wasThaw = initFlags()
                    lastYear=year
                weather = pointWeather[pointWeather['date']==date]
                if (~weather.empty):
                    try:
                        #print(weather.keys())
                        isFrost,isThaw,notWeekend = getFlags(weather,dow)
                    except:
                        print(' in getFlags')
                    if notWeekend:
                        try:
                            withinDates = checkDates(pointEvents, date, window)
                        except:
                            print('in checkDates')
                        if ~withinDates & isFrost:
                            for i in range(0,labelsPerFrost):
                                try:
                                    tmpLabel = drawSample(pointEvents, weather,year,doy)
                                    new_events = new_events.append(tmpLabel)
                                    count_is_frost += labelsPerFrost
                                except:
                                    print('in drawSample, with frost, date=',date,'identifier=',identifier)
                        elif  ~withinDates & ~isFrost:
                            removeMe = np.random.randint(1,10)
                            if (removeMe>cutNoFrostValue):
                                for i in range(0, labelsPerNoFrost):
                                    try:
                                        tmpLabel = drawSample(pointEvents, weather, year, doy)
                                        new_events = new_events.append(tmpLabel)
                                        count_is_not_frost += 1
                                    except:
                                        print('in drawSample, no frost, date=',date,'identifier=',identifier)
print(new_events)
print('number of labels for days with frost:',count_is_frost)
print('this is with labelsPerFrost =',labelsPerFrost)
print('number of labels for days without frost:',count_is_not_frost)
print('this is with labelsPerNotFrost =',labelsPerNoFrost)

new_events.to_csv('/Users/nbechor/Insight/SlipperySlope/data/processed/features_label0.csv')
