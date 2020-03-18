import pandas as pd

class identifierClass():
    """ Handles the identifier2weatherloc dataframe. 
    identifier2weatherloc includes identifier, Building ID, and
    grid lat,lon for that identifier"""

    def __init__(self, df):
        self.df = df
        self.df['lat'] = self.df['lat'].astype('float')
        self.df['lon'] = self.df['lon'].astype('float')
        self.df['identifier'] = self.df['identifier'].astype('int')


    def __str__(self):
        return self.df.shape

    def latLonFromRecord(self,identifier):
        """ lat,lon=latLonFromRecord(identifier2weatherloc,identifier)"""
        #print(identifier)
        errFlag = False
        try:
            temp = self.df[self.df['identifier']==identifier]
            lat = temp['lat'].iloc[0].astype('float')
            lon = temp['lon'].iloc[0].astype('float')
        except:
            errFlag = True
            lat=0
            lon=0

        return lat, lon, errFlag
