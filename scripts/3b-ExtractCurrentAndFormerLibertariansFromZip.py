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

# Set up variables needed later
numVotersParsed = 0
numLibertarians = 0



zipFileDirectory = "../ZIP/"

filePath = "../Database/"
prelimPrefix = "Libertarians"
filePrefix = "CurrentAndFormerLibertarians"
fileSep = "-"
fileSuffix = ".db"


#open CSV writer for output
errorFile = csv.writer(open('errors.csv', 'wb'), delimiter=',')

# each db output file is named with a time component to avoid over-writing files
timeComponent = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

prelimDB = filePath+prelimPrefix+fileSuffix

newDB = filePath+filePrefix+fileSep+timeComponent+fileSuffix

# check if preliminary database exists, end if it doesn't
# In the future, create the database if it isn't there.
if os.path.isfile(prelimDB):
    shutil.copyfile(prelimDB, newDB)
else:
    print "Preliminary Database File " + prelimDB + " Does Not Exist"
    sys.exit()

# Connect to the database
conn = sqlite3.connect(newDB)
cur = conn.cursor()

# get the list of fields from the database

cur.execute("PRAGMA table_info('libertarians')")
pragma = cur.fetchall()
# extract db field names from
dbfields = [str(x[1]) for x in pragma]


# Find some variables we'll need later
PARTY_AFFILIATION = MyFunctions.first_startswith('PARTY_AFFILIATION',dbfields)
FIRST_PRIMARY_FIELD = MyFunctions.first_startswith('PRIMARY',dbfields)
LAST_PRIMARY_FIELD = MyFunctions.last_startswith('PRIMARY',dbfields)
LAST_NAME = MyFunctions.first_startswith('LAST_NAME',dbfields)
FIRST_NAME = MyFunctions.first_startswith('FIRST_NAME',dbfields)
fieldsInLine = len(dbfields)

# find the county data files, put them in an array & sort them.
csvfiles = glob.glob('../ZIP/*.zip')
csvfiles.sort()

# parse the datafiles
for onefile in csvfiles:
    countyCount = 1

    try:
        zf = zipfile.ZipFile(onefile, 'r')
    except zipfile.BadZipfile:
        print "\n\nBad Zip File."
        print "Should probably do something here..."

    except:
        print "\n\nERROR! " + filename + " ", sys.exc_info()[0]
    else:

        txtfilename = onefile[7:-4] + '.TXT'
        print txtfilename
        reader = csv.reader(zf.open(txtfilename), delimiter=',')
        countyname = onefile[7:-4]
        print countyname
        for row in reader:
            if len(row) == fieldsInLine:
                numVotersParsed += 1
                # make list of elections
                electionsRange = -1 * (LAST_PRIMARY_FIELD - FIRST_PRIMARY_FIELD)
                elections = row[electionsRange : ]

                if (row[PARTY_AFFILIATION] == 'L') or (elections.count('L') > 0):
                    numLibertarians += 1
                    print numVotersParsed, numLibertarians, "::", countyname, countyCount, "::", row[LAST_NAME], row[FIRST_NAME], (row[PARTY_AFFILIATION] if row[PARTY_AFFILIATION] != "" else "-"),(row[LAST_PRIMARY_FIELD] if row[LAST_PRIMARY_FIELD] != "" else "-")
                    questionmarks = "?, " * (len(row) - 1)
                    questionmarks += "?"
                    cur.execute("INSERT INTO Libertarians VALUES (" + questionmarks + ");", row)
                    #conn.commit()
            else:
                print "----> LINE SKIPPED: " + str(len(row))+ " fields <----"
                errorFile.writerow(row)
            countyCount += 1
        conn.commit()

end_time = time.time()
total_time = end_time - start_time
votersPerSecond = numVotersParsed / total_time
print("--- %s seconds ---" % str(total_time))
print("--- %s voters parsed ---" % str(numVotersParsed))
print("--- %s voters per second ---" % str(votersPerSecond))
print("--- %s Libertarians ---" % str(numLibertarians))
