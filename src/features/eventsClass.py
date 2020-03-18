

class eventsClass():
    """class to handle the events dataframe (includes both citations and complaints)
    events fields are: date, lat, lng, address, identifier, index
    """
    import pandas as pd

    def __init__(self,df):
        import pandas as pd
        self.df = df
        self.df['date']=pd.to_datetime(self.df['date'],infer_datetime_format=True)
        self.df['date']=self.df['date'].dt.date
        self.df['identifier'] = self.df['identifier'].astype('int')
        self.df['lat'] = self.df['lat'].astype('float')
        self.df['lon'] = self.df['lon'].astype('float')


    def __str__(self):
        return str(self.df.shape)

    def getEventsForWeatherPoint(self,ind):
        """gets the events that were marked as nearest to the identifier in ind"""
        new_pd = self.df[self.df['identifier']==ind]
        return new_pd


