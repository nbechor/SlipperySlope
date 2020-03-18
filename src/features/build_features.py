''' Starting with Commonwealth_Connect_Service_Requests.csv, meaning
the tickets feature. See more info in notebook #2
'''
import pandas as pd
import numpy as np
from geopy.distance import geodesic

def find_nearest_building(df,latI,lonI):
    minDist = 4000
    flag = True
    for i in range(0,df.shape[0]):
        lat = df['lat'].iloc[i]
        lon = df['lon'].iloc[i]
        dist = geodesic([lat,lon],[latI,lonI]).meters
        if dist<minDist:
            minDist = dist
            nearestBuildingInDf = i
    if minDist==4000:
        flag=False
        nearestBuildingInDf = pd.DataFrame()
    return nearestBuildingInDf,flag

def fixLonLat(df,colName):

    # extracting the lat/lon info to answer the question of where they are located:
    extract = df[colName]

    extract = extract.apply(lambda x: x.split('(',1)[1])
    extract = extract.apply(lambda x: x.split(')',1)[0])

    df['lat'] = extract.apply(lambda x: x.split(',',1)[0])
    df['lon'] = extract.apply(lambda x: x.split(',',1)[1])

    print('Range of Latitudes for input coordinates:',df['lat'].min(),df['lat'].max())
    print('Range of Longitudes for input coordinates:',df['lon'].min(),df['lon'].max())

    df['lat'] = df['lat'].astype('float')
    df['lon'] = df['lon'].astype('float')

    return df

def minMaxCoords(lat,lon,dlat,dlon):
    minLat = lat-dlat
    maxLat = lat+dlat
    minLon = lon-dlon
    maxLon = lon+dlon
    return minLat,maxLat,minLon,maxLon

def findIdentifier(tickets,identifierLocation,dlat,dlon):
    # running over the tickets/complaints, cutting part of the identifierLocation DataaFrame close to each
    # ticket location, and finding the closest match building wise:

    tickets_feature = pd.DataFrame()
    tmp = pd.DataFrame()
    for i in range(0, tickets.shape[0]):
        lat = tickets['lat'].iloc[i]
        lon = tickets['lon'].iloc[i]
        minLat, maxLat, minLon, maxLon = minMaxCoords(lat, lon, dlat, dlon)
        df = identifierLocation[identifierLocation['lat'] < maxLat]
        df = df[df['lat'] > minLat]
        df = df[df['lon'] < maxLon]
        df = df[df['lon'] > minLon]
        # print(df.shape[0])
        # df now contains all the buildings withing the given lat/lon circle around the ticket location.
        # one of these buildings is the one that received the ticket:
        nearestBuildingIloc,flag = find_nearest_building(df, lat, lon)
        if flag:
            tmp = df.iloc[nearestBuildingIloc]
            tmp['date'] = tickets['date'].iloc[i]
            tmp['label'] = 1
            tickets_feature = tickets_feature.append(tmp)
        else:
            print('no closest bldg for record ',i)
    print(type(tickets_feature))
    print(tickets_feature.shape[0])
    return tickets_feature,flag

def fixDate(df,colName):
    df[colName] = pd.to_datetime(df[colName],infer_datetime_format=True)
    df['date'] = df[colName].dt.date
    print('Input dates:',min(df['date']),'to',max(df['date']))
    return df


identifierLocation = pd.read_csv('/Users/nbechor/Insight/SlipperySlope/data/processed/BldgID2WeatherIdentifier.csv')

## tickets labels:
tickets = pd.read_csv('/Users/nbechor/Insight/SlipperySlope/data/external/Snow_Ice_Sidewalk_Ordinance_Violations.csv')
tickets = fixDate(tickets,'OFFENSE DATE')
tickets = fixLonLat(tickets,'TICKET LOCATION')

lat_radius=abs(tickets['lat'].min()-tickets['lat'].max())/25
lon_radius = abs(tickets['lon'].min()-tickets['lon'].max())/25
#tickets_feature,flag = findIdentifier(tickets,identifierLocation,lat_radius,lon_radius)
#tickets_feature.to_csv('/Users/nbechor/Insight/SlipperySlope/data/interim/tickets_label.csv')

## Complaints dataset:
complaintsH = pd.read_csv('/Users/nbechor/Insight/SlipperySlope/data/external/Unshoveled_Icy_Sidewalk_Complaints.csv')
complaintsH = fixDate(complaintsH,'Date Submitted')
complaintsH = fixLonLat(complaintsH,'Address')
#complaintsH_feature,flag = findIdentifier(complaintsH,identifierLocation,lat_radius,lon_radius)
#complaintsH_feature.to_csv('/Users/nbechor/Insight/SlipperySlope/data/interim/historic_complaints_label.csv')


## 311 dataset:
complaints = pd.read_csv('/Users/nbechor/Insight/SlipperySlope/data/external/Commonwealth_Connect_Service_Requests.csv')
complaints = complaints[complaints['issue_type']=='Icy or Unshoveled Sidewalk']
complaints = fixDate(complaints,'ticket_created_date_time')
complaints['lat']= complaints['lat'].astype('float')
complaints['lon'] = complaints['lng'].astype('float')

lat_radius=abs(complaints['lat'].min()-complaints['lat'].max())/25
lon_radius = abs(complaints['lon'].min()-complaints['lon'].max())/25

complaints_feature,flag = findIdentifier(complaints,identifierLocation,lat_radius,lon_radius)
complaints_feature.to_csv('/Users/nbechor/Insight/SlipperySlope/data/interim/Complaints_label.csv')
