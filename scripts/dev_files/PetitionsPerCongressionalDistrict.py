#!/usr/bin/env python

import csv
import sqlite3
import glob
import datetime
import sys
import os
import shutil
import time
import zipfile
import MyFunctions


# Prepare to time execution - get start time
start_time = time.time()

# Simple object to hold number of libertarians & voters per district
class Area:
	def __init__(self):
		self.libertarians = 0
		self.voters = 0


# Set up a list of congressional Districts
congDists = []


# Populate list with objects
for i in range(16):
	congDists.append(Area())



zipFileDirectory = "../ZIP/"

filePath = "../Database/"
filePrefix = "Libertarians"
fileSep = "-"
fileSuffix = ".db"


#open CSV writer for output
errorFile = csv.writer(open('errors.csv', 'wb'), delimiter=',')
outFile = csv.writer(open('outCD.csv', 'wb'), delimiter=',')

prelimDB = filePath+filePrefix+fileSuffix

# Connect to the database
conn = sqlite3.connect(prelimDB)
cur = conn.cursor()

# get the list of fields from the database

cur.execute("PRAGMA table_info('libertarians')")
pragma = cur.fetchall()
# extract db field names from
dbfields = [str(x[1]) for x in pragma]


# Find some variables we'll need later
PARTY_AFFILIATION = MyFunctions.first_startswith('PARTY_AFFILIATION',dbfields)
LAST_PRIMARY_FIELD = MyFunctions.last_startswith('PRIMARY',dbfields)
CONGRESSIONAL_DISTRICT = MyFunctions.last_startswith('CONGRESSIONAL_DISTRICT',dbfields)

LAST_NAME = MyFunctions.first_startswith('LAST_NAME',dbfields)
FIRST_NAME = MyFunctions.first_startswith('FIRST_NAME',dbfields)
fieldsInLine = len(dbfields)

# find the county data files, put them in an array & sort them.
csvfiles = glob.glob('../ZIP/*.zip')
csvfiles.sort()

# parse the datafiles
for onefile in csvfiles:
    countyCount = 1
    # Set up variables needed later
    numVotersParsed = 0
    numLibertarians = 0

    try:
        zf = zipfile.ZipFile(onefile, 'r')
    except zipfile.BadZipfile:
        print "\n\nBad Zip File."
        print "Should probably do something here..."

    except:
        print "\n\nERROR! " + filename + " ", sys.exc_info()[0]
    else:
        txtfilename = onefile[7:-4] + '.TXT'
        # print txtfilename
        reader = csv.reader(zf.open(txtfilename), delimiter=',')
        countyname = onefile[7:-4]
        print countyname
        for row in reader:
            if len(row) == fieldsInLine and row[CONGRESSIONAL_DISTRICT] != "CONGRESSIONAL_DISTRICT":
                numVotersParsed += 1
                myCongDist = int(row[CONGRESSIONAL_DISTRICT])                                
                congDists[myCongDist - 1].voters += 1
                if (row[PARTY_AFFILIATION] == 'L') or (row[LAST_PRIMARY_FIELD] == 'L'):
                    numLibertarians += 1
                    congDists[myCongDist - 1].libertarians += 1
            else:
                errorFile.writerow(row)
            countyCount += 1
        #conn.commit()
outFile.writerow(["CD #", "# Libertarians", "# Voters"])
for i in range(16):
	# print i+1,congDists[i].libertarians, congDists[i].voters
	outFile.writerow([i+1, congDists[i].libertarians, congDists[i].voters])

end_time = time.time()
total_time = end_time - start_time
votersPerSecond = numVotersParsed / total_time
print("--- %s seconds ---" % str(total_time))
print("--- %s voters parsed ---" % str(numVotersParsed))
print("--- %s voters per second ---" % str(votersPerSecond))
print("--- %s Libertarians ---" % str(numLibertarians))
