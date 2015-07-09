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
import pprint


class ZipCode:
    def __init__(self):
        self.voters = 0
        self.parties = {}

    def __repr__(self):
        outString =  "{} voters [".format(self.voters)
        for key in self.parties:
            outString += "{}:{}  ".format(key, self.parties[key])
        outString += "]"
        return outString

    def addVoter(self):
        self.voters += 1

    def addAffiliatedVoter(self, affiliation):
        if affiliation not in self.parties:
            self.parties[affiliation] = 1
        else:
            self.parties[affiliation] += 1

    def getNumberOfVoters(self, affiliation=None):
        if affiliation is None:
            return self.voters
        elif affiliation in self.parties:
            return self.parties[affiliation]
        else:
            return 0


# Prepare to time execution - get start time
start_time = time.time()

# Set up variables needed later
numVotersParsed = 0
affiliations = []
zipCodes = {}
counties = {}

zipFileDirectory = "../ZIP/"
filePath = "../Database/"
filePrefix = "Libertarians"
fileSep = "-"
fileSuffix = ".db"

pp = pprint.PrettyPrinter(indent=4)

# each db output file is named with a time component to avoid over-writing files
timeComponent = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
prelimDB = filePath+filePrefix+fileSuffix
newDB = filePath+filePrefix+fileSep+timeComponent+fileSuffix

# open CSV writer(s) for output
outFileName = "OhioVoterAffiliationsByZipCode" + timeComponent + ".csv"
outFile = open(outFileName, 'wb')
outCSV = csv.writer(outFile, delimiter=',')

errorFile = open('errors.csv', 'wb')
errorCSV = csv.writer(errorFile, delimiter=',')


# check if preliminary database exists, end if it doesn't
# In the future, create the database if it isn't there.
if os.path.isfile(prelimDB):
    conn = sqlite3.connect(prelimDB)
    cur = conn.cursor()
else:
    print "Preliminary Database File " + prelimDB + " Does Not Exist"
    sys.exit()


# get the list of fields from the database
cur.execute("PRAGMA table_info('libertarians')")
pragma = cur.fetchall()
# extract db field names from
dbfields = [str(x[1]) for x in pragma]


# Find some variables we'll need later
PARTY_AFFILIATION = MyFunctions.first_startswith('PARTY_AFFILIATION',dbfields)
LAST_PRIMARY_FIELD = MyFunctions.last_startswith('PRIMARY',dbfields)
LAST_NAME = MyFunctions.first_startswith('LAST_NAME',dbfields)
FIRST_NAME = MyFunctions.first_startswith('FIRST_NAME',dbfields)
ZIP = MyFunctions.first_startswith('RESIDENTIAL_ZIP', dbfields)
fieldsInLine = len(dbfields)

# find the county data files, put them in an array & sort them.
csvfiles = glob.glob('../ZIP/*.zip')
csvfiles.sort()

# parse the datafiles
for onefile in csvfiles:
    countyAffiliations = {}

    try:
        # open the zip file for reading
        zf = zipfile.ZipFile(onefile, 'r')
    except zipfile.BadZipfile:
        print "\n\nBad Zip File."
        print "Should probably do something here..."

    except:
        # Yes, catch-all exceptions are bad...
        print "\n\nERROR! " + filename + " ", sys.exc_info()[0]
    else:
        txtfilename = onefile[7:-4] + '.TXT'

        # open the CSV file from within the ZIP file for reading
        countyFile = zf.open(txtfilename)
        reader = csv.reader(countyFile, delimiter=',')

        # extract the county name from the filename string (remove the path & suffix)
        countyname = onefile[7:-4]
        print countyname

        for row in reader:
            # SANITY CHECK: Are there the correct # of fields in the record?
            # If there aren't, then discard the line (writing it to an error file for later review)
            if len(row) == fieldsInLine:
                # increment the # of voters parsed
                numVotersParsed += 1
                # find the voter affiliation
                voterAffiliation = row[PARTY_AFFILIATION]
                # "None" is more descriptive than *blank*
                if voterAffiliation == '':
                    voterAffiliation = "None"

                # record zip code

                if row[ZIP] != "RESIDENTIAL_ZIP":
                    voterZip = row[ZIP]
                    if voterZip not in zipCodes:
                        zipCodes[voterZip] = ZipCode()

                    zipCodes[voterZip].addVoter()
                    zipCodes[voterZip].addAffiliatedVoter(voterAffiliation)

                    # Does this voter affiliation exist in the state?
                    # (We use the state affiliation list to ensure CSV consistency for counties without all affiliations.)
                    if voterAffiliation not in affiliations and voterAffiliation != "PARTY_AFFILIATION":
                        affiliations.append(voterAffiliation)

            else:
                # Incorrect # of fields in the record, write the record out to the error file.
                errorCSV.writerow(row)

        # Close the county file!
        countyFile.close()

        pp.pprint(zipCodes)



# pp.pprint(affiliations)

# Prepare output file header row
h_row = ['ZIP_CODE', 'NUMBER_OF_VOTERS']
for a in affiliations:
    h_row.append(a)

# Write the header row to the output file.
outCSV.writerow(h_row)

# Cycle through counties to output into header row.
# NOTE: dictionaries are inherently un-ordered, so this will not output in alphabetical order
# (This is easily-enough sorted in your database/spreadsheet program of choice.)
for zipcode, zcInfo in zipCodes.iteritems():
    # Prepare an empty  list for the row
    c_row = []
    c_row.append(zipcode)
    c_row.append(zcInfo.getNumberOfVoters())
    for a in affiliations:
        c_row.append(zcInfo.getNumberOfVoters(a))
    #Write the row to the CSV file
    outCSV.writerow(c_row)


#close files opened for writing
errorFile.close()
outFile.close()



end_time = time.time()
total_time = end_time - start_time
votersPerSecond = numVotersParsed / total_time
print("--- %s seconds ---" % str(total_time))
print("--- %s voters parsed ---" % str(numVotersParsed))
print("--- %s voters per second ---" % str(votersPerSecond))
