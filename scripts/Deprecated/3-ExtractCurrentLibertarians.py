#!/usr/bin/env python

import csv, sqlite3, glob, datetime, sys, os, shutil, time

# Prepare to time execution - get start time
start_time = time.time()

# Set up variables needed later
numVotersParsed = 0
numLibertarians = 0
fieldsInLine = 91


FIRST_ELECTION_FIELD = 45
LAST_ELECTION_FIELD = 90

LAST_PRIMARY_FIELD = 89

filePath = "../Database/"
filePrefix = "Libertarians"
fileSep = "-"
fileSuffix = ".db"

#set up field numbers for easier reading of code
#Due to using these as array indices, these should be zero-based

SOS_VOTERID = 0
COUNTY_NUMBER = 1
PARTY_AFFILIATION = 9
LAST_NAME = 3
FIRST_NAME = 4
MIDDLE_NAME = 5
SUFFIX = 6
YEAR_OF_BIRTH = 7
RESIDENTIAL_ADDRESS1 = 10
RESIDENTIAL_SECONDARY_ADDR = 11
RESIDENTIAL_CITY = 12
RESIDENTIAL_STATE = 13
RESIDENTIAL_ZIP = 14
STATE_REPRESENTATIVE_DISTRICT = 40
STATE_SENATE_DISTRICT = 41
CONGRESSIONAL_DISTRICT = 30


#open CSV writer for output
writer = csv.writer(open('errors.csv', 'wb'), delimiter=',')

# each db output file is named with a time component to avoid over-writing files
timeComponent = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

prelimDB = filePath+filePrefix+fileSuffix

##print prelimDB

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
curs = conn.cursor()

curs.execute("CREATE TABLE IF NOT EXISTS Libertarians (SOS_VOTERID TEXT, COUNTY_NUMBER INTEGER, COUNTY_NAME TEXT, PARTY_AFFILIATION TEXT, LAST_NAME TEXT, FIRST_NAME TEXT, MIDDLE_NAME TEXT, SUFFIX TEXT, YEAR_OF_BIRTH INTEGER, RESIDENTIAL_ADDRESS1 TEXT, RESIDENTIAL_SECONDARY_ADDR TEXT, RESIDENTIAL_CITY TEXT, RESIDENTIAL_STATE TEXT, RESIDENTIAL_ZIP TEXT, STATE_REPRESENTATIVE_DISTRICT TEXT, STATE_SENATE_DISTRICT TEXT, CONGRESSIONAL_DISTRICT TEXT, PRIMARY_03_07_2000 TEXT, GENERAL_11_07_2000 TEXT, SPECIAL_05_08_2001 TEXT, GENERAL_11_06_2001 TEXT, PRIMARY_05_07_2002 TEXT, GENERAL_11_05_2002 TEXT, SPECIAL_05_06_2003 TEXT, GENERAL_11_04_2003 TEXT, PRIMARY_03_02_2004 TEXT, GENERAL_11_02_2004 TEXT, SPECIAL_02_08_2005 TEXT, PRIMARY_05_03_2005 TEXT, PRIMARY_09_13_2005 TEXT, GENERAL_11_08_2005 TEXT, SPECIAL_02_07_2006 TEXT, PRIMARY_05_02_2006 TEXT, GENERAL_11_07_2006 TEXT, PRIMARY_05_08_2007 TEXT, PRIMARY_09_11_2007 TEXT, GENERAL_11_06_2007 TEXT, PRIMARY_11_06_2007 TEXT, GENERAL_12_11_2007 TEXT, PRIMARY_03_04_2008 TEXT, PRIMARY_10_14_2008 TEXT, GENERAL_11_04_2008 TEXT, GENERAL_11_18_2008 TEXT, PRIMARY_05_05_2009 TEXT, PRIMARY_09_08_2009 TEXT, PRIMARY_09_15_2009 TEXT, PRIMARY_09_29_2009 TEXT, GENERAL_11_03_2009 TEXT, PRIMARY_05_04_2010 TEXT, PRIMARY_07_13_2010 TEXT, PRIMARY_09_07_2010 TEXT, GENERAL_11_02_2010 TEXT, PRIMARY_05_03_2011 TEXT, PRIMARY_09_13_2011 TEXT, GENERAL_11_08_2011 TEXT, PRIMARY_03_06_2012 TEXT, GENERAL_11_06_2012 TEXT, PRIMARY_05_07_2013 TEXT, PRIMARY_09_10_2013 TEXT, PRIMARY_10_01_2013 TEXT, GENERAL_11_05_2013 TEXT, PRIMARY_05_06_2014 TEXT);")

# find the county data files, put them in an array & sort them.
csvfiles = glob.glob('../TXT/*.TXT')
csvfiles.sort()

# parse the datafiles
for onefile in csvfiles:
	countyCount = 1
	reader = csv.reader(open(onefile, 'r'), delimiter=',')
	countyname = onefile[7:-4]
	for row in reader:
		if len(row) == fieldsInLine:
			numVotersParsed += 1
			if (row[PARTY_AFFILIATION] == 'L') or (row[LAST_PRIMARY_FIELD] == 'L') :
				numLibertarians += 1
				print numVotersParsed, numLibertarians, "::", countyname, countyCount, "::", row[LAST_NAME], row[FIRST_NAME], (row[PARTY_AFFILIATION] if row[PARTY_AFFILIATION] != "" else "-"),(row[LAST_PRIMARY_FIELD] if row[LAST_PRIMARY_FIELD] != "" else "-")
				to_db = [row[SOS_VOTERID],\
						 row[COUNTY_NUMBER], 
						 countyname, \
						 row[PARTY_AFFILIATION], \
						 row[LAST_NAME], \
						 row[FIRST_NAME], \
						 row[MIDDLE_NAME], \
						 row[SUFFIX], \
						 row[YEAR_OF_BIRTH], \
						 row[RESIDENTIAL_ADDRESS1], \
						 row[RESIDENTIAL_SECONDARY_ADDR], \
						 row[RESIDENTIAL_CITY], \
						 row[RESIDENTIAL_STATE], \
						 row[RESIDENTIAL_ZIP], \
						 row[STATE_REPRESENTATIVE_DISTRICT], \
						 row[STATE_SENATE_DISTRICT], \
						 row[CONGRESSIONAL_DISTRICT]]
				for field in range(FIRST_ELECTION_FIELD,LAST_ELECTION_FIELD + 1):  #Must add 1 to get full range
					to_db.append(row[field])

				questionmarks = "?, " * (len(to_db) - 1)
				questionmarks += "?"
				curs.execute("INSERT INTO Libertarians VALUES (" + questionmarks + ");", to_db)
				#conn.commit()
		else:
			print "----> LINE SKIPPED: " + str(len(row))+ " fields <----"
			writer.writerow(row)
		countyCount += 1
	conn.commit()

end_time = time.time()
total_time = end_time - start_time
votersPerSecond = numVotersParsed / total_time
print("--- %s seconds ---" % str(total_time))
print("--- %s voters parsed ---" % str(numVotersParsed))
print("--- %s voters per second ---" % str(votersPerSecond))
print("--- %s Libertarians ---" % str(numLibertarians))
