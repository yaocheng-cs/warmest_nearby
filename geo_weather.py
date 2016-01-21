'''
Created on Feb 20, 2013

@author: yaocheng
'''

import time
from datetime import date
from collections import defaultdict
import json
from lxml import etree
from web_service import GeoNames, WeatherBug

GEONAMES_SERVER = 'ws.geonames.net'
GEONAMES_USERNAME = 'ms_test201302'

WEATHERBUG_SERVER = 'i.wxbug.net'
#WEATHERBUG_KEY = 'rpjv5wkg9q465bkuzrhdrqbg'
WEATHERBUG_KEY = 'xev798p793526ysbp869mn7x'
WEEKLY_FORCAST = 'REST/Direct/GetForecast.ashx'

ERROR_RADIUS = 0.5 # in km
NEARBY_RADIUS = 48.28032 # in km (30 miles)
NUM_DAYS = 7
NUM_CANDIDATE = 10
NUM_RESULT = 5

def get_coordinate(name_code, err=0.5): # Error radius is 0.5 km
    geo = GeoNames(GEONAMES_SERVER, GEONAMES_USERNAME)
    try:
        int(name_code)
        response = geo.request('findNearbyPostalCodes', style='short', country='US', radius=err, postalcode=name_code)
    except ValueError:
        response = geo.request('findNearbyPostalCodes', style='short', country='US', radius=err, placename=name_code)
    if response:
        res = etree.parse(response)
        lats = [float(elmt.text) for elmt in res.xpath('/geonames/code/lat')]
        lngs = [float(elmt.text) for elmt in res.xpath('/geonames/code/lng')]
        if lats == [] or lngs == []:
            return 'No place can be found for the search term'
        return zip(lats, lngs)
    else:
        return 'No response from GeoNames'
        
def get_postalcode(placename, err=0.5): # Error radius is 0.5 km
    geo = GeoNames(GEONAMES_SERVER, GEONAMES_USERNAME)
    response = geo.request('findNearbyPostalCodes', style='short', country='US', radius=err, placename=placename)
    if response:
        res = etree.parse(response)
        postals = [elmt.text for elmt in res.xpath('/geonames/code/postalcode')]
        if postals == []:
            return 'No postal code can be found for a place'
        return postals
    else:
        return 'No response from GeoNames'
        
def get_place_nearby(lat, lng, radius, num_rslt=10):
    geo = GeoNames(GEONAMES_SERVER, GEONAMES_USERNAME)
    response = geo.request('findNearbyPlaceName', style='short', lat=lat, lng=lng, maxRows=num_rslt, radius=radius)
    if response:
        res = etree.parse(response)
        placenames = [elmt.text for elmt in res.xpath('/geonames/geoname/toponymName')]
        if placenames == []:
            return 'No nearby place can be found for the search term'
        return placenames
    else:
        return 'No response from GeoNames'
        
def get_weekly_weather(postalcode, days=7):
    if days > 7:
        days = 7
    weather = WeatherBug(WEATHERBUG_SERVER, WEATHERBUG_KEY)
    response = weather.request(WEEKLY_FORCAST, nf=days, l='en', c='US', zip=postalcode)
    if response:
        try:
            res = json.loads(response.read())
            week = res['forecastList']
            return week
        except ValueError:
            return 'No weather information can be found for a place'
    else:
        return 'No response from WeatherBug'

def get_warmest_nearby(name_code, err=ERROR_RADIUS, radius=NEARBY_RADIUS, num_day=NUM_DAYS, num_candid=NUM_CANDIDATE, num_rslt=NUM_RESULT):
    coords = get_coordinate(name_code, err)
    if isinstance(coords, str):
        return coords
    lat, lng = coords[0]
    names = get_place_nearby(lat, lng, radius, num_candid)
    if isinstance(names, str):
        return names
    current = int(time.time())
    max_miss = num_candid - num_rslt
    num_miss = 0
    #stamps = []
    all_forcast = []
    for name in names:
        #print name
        time.sleep(0.1)
        #weekly_forcast = []
        postal = get_postalcode(name, err)
        if isinstance(postal, str):
            num_miss += 1
            if num_miss < max_miss:
                continue
            else:
                return 'Too much information not retrievable. Retrieved is not enough to generate result. Could be WeatherBug api key over limited'
        week = get_weekly_weather(postal[0], num_day)
        if isinstance(week, str):
            num_miss += 1
            if num_miss < max_miss:
                continue
            else:
                return 'Too much information not retrievable. Retrieved is not enough to generate result. Could be WeatherBug api key over limited'
        for day in week:
            stamp = int(day['dateTime']) / 1000 + 86400
            if stamp + 86400 < current: # "forcast" for yesterday
                continue
            cal = date.fromtimestamp(stamp).strftime('%B %d, %Y')
            wkd = str(day['dayTitle'])
            if day['high']:
                high = int(day['high'])
            else:
                high = day['high']
            if day['low']:
                low = int(day['low'])
            else:
                low = day['low']
            if week.index(day) == 0:
                avg = low
            elif week.index(day) == len(week) - 1:
                avg = high
            else:
                avg = (high + low) / 2.0
            #print (stamp, cal, wkd, name, high, low, avg)
            #if stamp not in stamps:
            #    stamps.append(stamp)
            #weekly_forcast.append((stamp, cal, wkd, name, high, low, avg))
            all_forcast.append((stamp, cal, wkd, name, high, low, avg))
    s2f = defaultdict(list)
    for f in all_forcast:
        s2f[f[0]].append(f)
    sorted_days = sorted(s2f.values(), key=lambda x: x[0][0])
    for day in sorted_days:
        if len(day) < num_rslt:
            sorted_days.remove(day)
    ranked_weather = [sorted(day, key=lambda x: x[-1], reverse=True)[:num_rslt] for day in sorted_days]
    return ranked_weather

def main():
    print get_warmest_nearby('Boston')

if __name__ == '__main__':
    main()