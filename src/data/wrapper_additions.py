import numpy as np
import pandas as pd
from forecastiopy import *
from datetime import datetime
from dateutil.relativedelta import relativedelta


# generating lat/lon grid

lon0 = -71.16
lone = -71.06
lat0 = 42.41
late = 42.35
nlon = 35
nlat = 27

lons = np.linspace(lon0, lone, num=nlon)
lats = np.linspace(lat0, late, num=nlat)

print(len(lons), len(lats))

# generating dates


year = 2007
month = "01"
ind = 0
day = 1

dates = pd.DataFrame(columns=["year", "month", "day", "record", "time"])

def append_rows(dates, year, month, days, ind):
    for k in range(0, len(days)):
        daystr = str(days[k]).zfill(2)
        t = str(year) + "-" + str(month) + "-" + daystr + "T00:00:00"
        dates = dates.append(
            {
                "year": [year],
                "month": [month],
                "day": days[k],
                "record": [ind],
                "time": t,
            },
            ignore_index=True,
        )
        ind += 1
    return dates, ind



months = ["12","01", "02", "03", "04"]
days2 = [31, 31, 29, 31, 5]
days1 = [31, 31, 28, 31, 5]

for year in [2007, 2008, 2009, 2010,2011]:
    if (year == 2008):
        days = days2
    else:
        days = days1

    for d in range(0, len(days)):
        dates, ind = append_rows(dates, year, months[d], range(1, days[d] + 1), ind)


# now supposed to have all days in the years 2012...2019.
# print(dates.shape[0])
# print(ind)
dates = dates.set_index("record")

times = dates["time"].to_list()
print(len(times))
key = "43b5a6b6b264933c0cac096ee0900db4"
df = pd.DataFrame()
for lat in range(4,8):
    for lon in range(0, len(lons)):
        for t in range(0, len(times)):
            OKflag = True
            try:
                forecast = ForecastIO.ForecastIO(
                    key,
                    latitude=lats[lat],
                    longitude=lons[lon],
                    time=times[t],
                    exclude=["currently", "hourly"],
                )
                daily = FIODaily.FIODaily(forecast)
                new_line_dict = daily.get()
            except:
                OKflag=False
            if OKflag:
                if df.empty:
                    df = pd.DataFrame.from_dict(new_line_dict["data"])
                    df["time"] = times[t][0:10]
                    df["lat"] = lats[lat]
                    df["lon"] = lons[lon]
                else:
                    df1 = pd.DataFrame.from_dict(new_line_dict["data"])
                    df1["time"] = times[t][0:10]
                    df1["lat"] = lats[lat]
                    df1["lon"] = lons[lon]
                    df = pd.concat([df, df1], sort=True)
        print(lon, "out of ", len(lons))
    print(lat,'out of ',len(lats))
    # if wants to run from scratch:
    df.to_csv('DarkSky.csv')
    #df.to_csv('DarkSky.csv',mode='a',header=False)
    # later can merge the different tables using the dates...
keys = df.keys()
# current = FIOCurrently.FIOCurrently(forecast)
# hourly = FIOHourly.FIOHourly(forecast)
# daily = FIODaily.FIODaily(forecast)
# df.to_csv('DarkSky.csv')
# print(hourly.get_hour(4))
# print(hourly.hours())
