#!/usr/bin/env python

import sqlite3
import requests
import sys
import os
import time
import MyFunctions

# Prepare to time execution - get start time
start_time = time.time()

filePath = "../Database/"
filePrefix = "Libertarians"
fileSep = "-"
fileSuffix = ".db"

defaultDBfile = filePath + filePrefix + fileSuffix

# geocoding credentials
APP_ID = "gxXh1Wb3tWJWAk9ZzE0p"
APP_CODE = "0h7KH3-TqhrxlOuXjjmO7w"

args = sys.argv

if len(args) < 2:
    print "ERROR - this file must be called with a valid & existing db file"

if not os.path.isfile(args[1]):
    print "ERROR 1st argument must be a valid & existing db file"
    sys.exit(1)
else:
    print "Database file found..."

dbfile = args[1]

try:
    db = sqlite3.connect(dbfile)
    db.row_factory = sqlite3.Row  # allows string index access to db rows (like PHP)
    cur = db.cursor()

except:
    print "ERROR opening database file: %s" % dbfile
    raise

print "Connected to database file..."

# limit = 10

sql =  "SELECT * FROM libertarians "
sql += "WHERE SOS_VOTERID NOT IN ( "
sql += "SELECT DISTINCT SOS_VOTERID FROM locations WHERE SOS_VOTERID != '' ) "
sql += "ORDER BY RANDOM() "
# sql += "LIMIT %s" % str(limit)

print sql

cur.execute(sql)

rowsProcessed = 0

for row in cur.fetchall():
    rowsProcessed += 1
    SEARCHTEXT = row['RESIDENTIAL_ADDRESS1'] + " " + \
                 row['RESIDENTIAL_CITY'] + " " + \
                 row['RESIDENTIAL_STATE'] + " " + \
                 row['RESIDENTIAL_ZIP']

    BASE_URL = "http://geocoder.api.here.com"
    URL_PATH = "/6.2"
    URL_RESOURCE = "/geocode.json"

    url = BASE_URL+URL_PATH+URL_RESOURCE

    parameters = {"app_code" : APP_CODE,
                  "app_id" : APP_ID,
                  "searchtext" : SEARCHTEXT}

    try:
        r = requests.get(url, params=parameters)

        # print r.url
        # print r.json()
        # sys.exit(1)


        if r.status_code == 200:
            rj = r.json()

            try:
                latitude = rj['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']['Latitude']
                longitude = rj['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']['Longitude']
                relevance = rj['Response']['View'][0]['Result'][0]['Relevance']
            except:
                latitude = ""
                longitude = ""
                relevance = -1.0

            insertSQL = "INSERT INTO locations ('SOS_VOTERID', 'LAT', 'LONG', 'RELEVANCE') VALUES "
            insertSQL += "('%s', '%s', '%s', %0.2f)" % (row['SOS_VOTERID'], latitude, longitude, relevance)
            cur.execute(insertSQL)
        else:
            insertSQL = " - "

        print rowsProcessed, ": ", r.status_code, ": ", insertSQL

        if rowsProcessed % 100 == 0:
            db.commit()  # Commit every 100 requests

    except:
        print "Uh oh!  Something went wrong!"
        print r.url
        print r.json()
        db.commit()
        db.close()
        raise

db.commit()  # Do final commit


#Parse National Entries

sql2 =  "SELECT * FROM national "
sql2 += "WHERE id NOT IN ( "
sql2 += "SELECT DISTINCT NATIONAL_ID FROM locations WHERE NATIONAL_ID != '' ) "
sql2 += "ORDER BY RANDOM() "


print sql2

cur.execute(sql2)

rowsProcessed = 0

for row in cur.fetchall():
    print rowsProcessed
    rowsProcessed += 1
    SEARCHTEXT = row['address1'] + " " + \
                 row['city'] + " " + \
                 row['state'] + " " + \
                 row['zip'][:5]

    # print SEARCHTEXT

    BASE_URL = "http://geocoder.api.here.com"
    URL_PATH = "/6.2"
    URL_RESOURCE = "/geocode.json"

    url = BASE_URL+URL_PATH+URL_RESOURCE


    parameters = {"app_code" : APP_CODE,
                  "app_id" : APP_ID,
                  "searchtext" : SEARCHTEXT}

    try:
        r = requests.get(url, params=parameters)
        # print r.url

        # print r.json()

        # sys.exit(1)


        if r.status_code == 200:
            rj = r.json()

            try:
                latitude = rj['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']['Latitude']
                longitude = rj['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']['Longitude']

                relevance = rj['Response']['View'][0]['Result'][0]['Relevance']
            except:
                latitude = ""
                longitude = ""
                relevance = -1.0

            insertSQL = "INSERT INTO locations ('NATIONAL_ID', 'LAT', 'LONG', 'RELEVANCE') VALUES "
            insertSQL += "('%s', '%s', '%s', %0.2f)" % (row['id'], latitude, longitude, relevance)
            cur.execute(insertSQL)
        else:
            insertSQL = " - "

        print rowsProcessed, ": ", r.status_code, ": ", insertSQL

        if rowsProcessed % 100 == 0:
            db.commit()  # Commit every 100 requests

    except:
        print "Uh oh!  Something went wrong!"
        print r.url
        print r.json()
        db.commit()
        db.close()
        raise



db.commit()  # Do final commit

db.close()

if MyFunctions.query_yes_no("Copy geolocations into default database for later use?"):
    src_conn = MyFunctions.open_db(dbfile)
    dest_conn = MyFunctions.open_db(defaultDBfile)

    MyFunctions.copy_table('locations',src_conn,dest_conn)



end_time = time.time()
print("\n<--- Execution time: %s seconds --->" % (end_time - start_time))
