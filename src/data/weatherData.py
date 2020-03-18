
class weatherData:
    '''Class to download DarkSky data for grid over city
    initiating the grid parameters and data time span for model training'''
    import numpy as np
    import pandas as pd
    from datetime import datetime
    from dateutil.relativedelta import relativedelta

    lon0 = -71.16
    lone = -71.06
    lat0 = 42.41
    late = 42.35
    nlons = 35
    nlats = 27

    grid_lons = np.linspace(lon0, lone, num=nlons)
    grid_lats = np.linspace(lat0, late, num=nlats)


    years = list(np.arange(2007, 2020))
    leap_years = [2008, 2012, 2016, 2020]
    winter_months = ["12", "01", "02", "03", "04"]
    leap_days = [31, 31, 29, 31, 5]
    days = [31, 31, 28, 31, 5]

    dates = pd.DataFrame(columns=["year", "month", "day", "record", "time"])
    identifier = []
    lats = np.zeros(nlats*nlons)
    lons = np.zeros(nlats*nlons)

    def __init__(self):
        inds = self.nlats*self.nlons
        self.identifier = [i for i in range(inds)]
        k = 0
        for i in range(0,self.nlons):
            for j in range(0,self.nlats):
                self.lons[k] = self.grid_lons[i]
                self.lats[k] = self.grid_lats[j]
                k += 1


    def __str__(self):
        return ["class object that holds weather grid, dates, and can be used to download data"]

    def append_rows(self, year, month, days):
        ind = self.ndates
        for k in range(0, len(days)):
            daystr = str(days[k]).zfill(2)
            t = str(year) + "-" + str(month) + "-" + daystr + "T00:00:00"
            self.dates = self.dates.append(
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
        self.ndates=ind
        return self

    def populate_dates(self):
        for year in self.years:
            if year in self.leap_years:
                days = self.leap_days
            else:
                days = self.days
            for d in range(0, len(days)):
                self = append_rows(self, year, self.months[d], range(1, days[d] + 1))

        self = self.set_index("record")
        return self

    def downloadData(self,nlat_start,nlat_end):
        '''downloadData(self,nlat_start,nlat_end)
        routine to download data by latitude grid point.
        nlat_start, nlat_end are the indexes of the desired
        latitude points (starting from 0 and ending in self.nlat)
        Done this way because takes a long time to download data, so
        in case some part of the data are missing, can add...
        saves downloaded data into DarkSky.csv'''
        import pandas as pd
        from forecastiopy import ForecastIO,FIODaily

        times = self.dates["time"].to_list()
        key = "43b5a6b6b264933c0cac096ee0900db4"
        df = pd.DataFrame()
        for lat in range(nlat_start,nlat_end):
            for lon in self.lons:
                for t in range(0, len(times)):
                    OKflag = True
                    try:
                        forecast = ForecastIO.ForecastIO(
                        key,
                        latitude=lat,
                        longitude=lon,
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
                            df["lat"] = lat
                            df["lon"] = lon
                        else:
                            df1 = pd.DataFrame.from_dict(new_line_dict["data"])
                            df1["time"] = times[t][0:10]
                            df1["lat"] = lat
                            df1["lon"] = lon
                            df = pd.concat([df, df1], sort=True)
                print(lon, "out of ", self.nlons)
            print(lat,'out of ',nlat_start,'-',nlat_end)
            # if wants to save from scratch each iteration (recommended..):
            df.to_csv('DarkSky.csv')
        # or can append to existing file:
        #df.to_csv('DarkSky.csv',mode='a',header=False)
        # later can merge the different tables using the dates...

