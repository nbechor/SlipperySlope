import pandas as pd

class identifierClass():
    """ Handles the identifier2weatherloc dataframe. 
    identifier2weatherloc includes identifier as index, and the weather
    grid lat,lon for that identifier (pre-sorted from Complaints_feature.ipynb)
    This is for the combined complaints + tickets features. for the negative labels,
    uses weather lat/lon directly instead..."""

    def __init__(self, df):
        self.df = df


    def __str__(self):
        return self.df.shape

    def latLonFromRecord(self,identifier):
        """ lat,lon=latLonFromRecord(identifier2weatherloc,identifier)"""
        #print(identifier)
        errFlag = False
        try:
            temp = self.df.loc[identifier]
            lat = temp['lat']
            lon = temp['lon']
        except:
            errFlag = True
            lat=0
            lon=0

        return lat, lon, errFlag
