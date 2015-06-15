#!/usr/bin/env python

import requests
import sys
import os
import time
import MyFunctions

# Prepare to time execution - get start time
start_time = time.time()

# geocoding credentials
APP_ID = "j46b9iXmuhlhbX5a9sb4"
APP_CODE = "_8TxyrSNrjuzF42PGAWUGA"


BASE_URL = "http://reverse.geocoder.api.here.com"
URL_PATH = "/6.2"
URL_RESOURCE = "/reversegeocode.json"

url = BASE_URL+URL_PATH+URL_RESOURCE
lat = 39.183334
long = -84.346885
radius = 10000

parameters = {"app_code" : APP_CODE,
              "app_id" : APP_ID,
              "prox" : str(lat) + "," + str(long) + "," + str(radius),
              "mode" : "retrieveAddresses",
              "gen" : 8}

try:
    r = requests.get(url, params=parameters)


    if r.status_code == 200:
        rj = r.json()
        #print rj
        #print r.url

    else:
        print "Weird Error Code: ", r.status_code
        print r.url


except:
    print "Uh oh!  Something went wrong!"

streets = []

results = rj['Response']['View'][0]['Result']

for result in results:
    address = result['Location']['Address']
    if 'Street' in address.keys():
        streets.append(result['Location']['Address']['Street'])

streets = list(set(streets))
streets.sort()
print streets

end_time = time.time()
print("\n<--- Execution time: %s seconds --->" % (end_time - start_time))