#!/usr/bin/env python

import csv
import glob
import sqlite3
import sys
import os
import shutil
import time
import zipfile
import MyFunctions

zipDirectory = "../ZIP/"
databaseDirectory = "../Database/"

numCountiesExpected = 88
myZipFiles = glob.glob(zipDirectory + '*.zip')
myZipFiles.sort()

if len(myZipFiles) == numCountiesExpected:
    print numCountiesExpected, "counties found - OK!"
else:
    print numCountiesExpected, "counties expected"
    print len(myZipFiles), "counties found"

    numErrors = len(glob.glob(zipDirectory + '*.ERROR'))
    if numErrors > 0:
        print str(numErrors) + " error file(s) found"
    if not MyFunctions.query_yes_no("Proceed?"):
        print "Exiting due to user request: incorrect # of counties found!"
        sys.exit(0)

fields = []

# Scan and see if files are consistent

errors = []

for onefile in myZipFiles:
    # separate the filename
    filenameparts = onefile.split('/')

    # grab the actual filename
    filename = filenameparts[-1]

    # open the zip file
    try:
        zf = zipfile.ZipFile(zipDirectory + filename, 'r')
    except zipfile.BadZipfile:
        print "\n\nBad Zip File. Renaming to avoid later confusion"
        os.rename(zipDirectory + filename, zipDirectory + filename + ".ERROR")
    except:
        print "\n\nERROR! " + filename + " ", sys.exc_info()[0]
    else:
        # If we got here, we've got a good zip file

        # replace the suffix with .TXT
        txtfilename = filename[:-4] + '.TXT'

        # create a CSV reader with the suffix
        reader = csv.reader(zf.open(txtfilename), delimiter=',')
        row1 = next(reader)
        if not fields:
            fields = row1
        else:
            if row1 != fields:
                print "\n\n" + filename + " differs from those preceding..."
                errors.append(filename)
                if not MyFunctions.query_yes_no("Proceed?"):
                    print "\n\nExiting at user request..."
                    sys.exit(65)

# Ok - we've read the header lines of each of the files.

if errors:
    print "\n\n" + str(len(errors)) + " file header(s) are different..."
    print "(Large #s could indicate a problem with the first file: " + myZipFiles[0]
    for error in errors:
        print error
    if not MyFunctions.query_yes_no("Proceed?"):
        print "Aborting..."
        sys.exit(65)
    else:
        if MyFunctions.query_yes_no("Rename files to exclude from processing?"):
            for error in errors:
                print "Renaming " + zipDirectory + error + " to: " \
                    + zipDirectory + error + ".ERROR"
                os.rename(zipDirectory + error, zipDirectory + error + ".ERROR")
else:
    print "\nAll files have identical fields!"
    print "All files have " + str(len(fields)) + " fields.\n"

firstElectionField = MyFunctions.first_startswith(('PRIMARY', 'GENERAL', 'SPECIAL'), fields)

# does the database even exist?

# open the database file
db = sqlite3.connect(databaseDirectory + 'Libertarians.db')
cur = db.cursor()

cur.execute("PRAGMA table_info('libertarians')")
pragma = cur.fetchall()
# extract db field names from
dbfields = [str(x[1]) for x in pragma]

if dbfields == fields:
    print "DB matches file format"
else:
    print "DB does not match file format"
    print len(dbfields), "fields in database"
    print len(fields), "fields in files"

    if MyFunctions.query_yes_no("Replace db schema with file schema?", "no"):
        print "\nOk...."
        print "Dropping table: libertarians"
        db.execute('''DROP TABLE IF EXISTS libertarians''')
        db.commit()
        print "Recreating table: libertarians with new file format"
        sql = "CREATE TABLE libertarians ("
        fields_added = 0
        for afield in fields:
            if fields_added == 0:
                fieldname = ""
            else:
                fieldname = ", "
            print fieldname
            if afield == "SOS_VOTERID":
                optionText = " PRIMARY KEY"
            else:
                optionText = ""
            fieldname += "'" + afield + "' TEXT" + optionText
            sql += fieldname
            fields_added += 1
        sql += ")"
        print sql
        db.execute(sql)
        db.commit()

    else:
        print "\nLeaving database as is."
        print "You will NOT be able to parse or import records until the database fields match"
        print "Exiting at user request"
        sys.exit(65)

print "You have rectified data issues & database structures..."
print "You should be ready to import data using the command:  python 3-ExtractCurrentLibertariansFromZip.py"