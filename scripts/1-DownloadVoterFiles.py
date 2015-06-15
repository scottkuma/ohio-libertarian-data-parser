#!/usr/bin/env python

import sys
import os
import shutil
import time
import subprocess
import zipfile
import MyFunctions

start_time = time.time()

ZIPFILEDIRECTORY = "../ZIP/"
errors = []                     # list of lists, each sublist defined as [filename, error message to display]
countiesfile = 'counties.txt'   # text file containing list of counties to download (one per line)


if os.listdir(ZIPFILEDIRECTORY):
    if not MyFunctions.query_yes_no("Directory " + ZIPFILEDIRECTORY +
                                    "is not empty. Proceed? \n(Will fill missing files, will not overwrite) -->",
                                    "no"):
        print "\nOk - exiting at user request"
        sys.exit(0)

# open counties file
f = open(countiesfile, 'r')

# get the whole shebang
counties = f.readlines()

# standardize each line (remove trailing spaces, make all uppercase)
counties = [x.strip() for x in counties]
counties = [x.upper() for x in counties]

# cycle through counties in the list
for county in counties:

    zfilename = county + ".zip"
    # filename = county + ".TXT"

    if not os.path.isfile(ZIPFILEDIRECTORY + zfilename):

        print "** Getting ZIP file for " + county + " county"
        cmd = "wget --no-passive-ftp ftp://server6.sos.state.oh.us/free/Voter/" + zfilename
        subprocess.call(cmd, shell=True)

        print "** Checking " + county + ".zip"
        try:
            zf = zipfile.ZipFile(zfilename, 'r')
        except zipfile.BadZipfile:
            print "Error opening " + zfilename
            print "Tagging with ERROR suffix and moving to ZIP directory for later review"
            print "(This file will not affect import of other, well-formed files)"
            if os.path.isfile(county + ".zip"):
                    try:
                        shutil.move(county + ".zip", ZIPFILEDIRECTORY + county + ".zip.ERROR")
                    except shutil.Error:
                        print "Could not move file " + county + ".zip"
                        print sys.exc_info()[0]
                    else:
                        errors.append([county + ".zip", "Bad Zip File?"])

        else:
            zippedfiles = zf.namelist()
            if (len(zippedfiles) != 1) and (zippedfiles[0] != county + ".TXT"):
                print "Error with structure of " + zfilename + ":"
                print "File does not contain expected filename " + county + ".TXT"
                print "File contains the following zipped files:", zippedfiles
                if not MyFunctions.query_yes_no("\nTag file with .ERROR suffix and proceed?"):
                    print "\nOK - exiting at user request"
                    sys.exit(65)
                else:
                    os.rename(zfilename, zfilename + ".ERROR")
                    errors.append([county + ".zip", "Zip File Structure Error"])

            print "** Moving " + county + ".zip"
            if os.path.isfile(county + ".zip"):
                try:
                    shutil.move(county + ".zip", ZIPFILEDIRECTORY)
                except shutil.Error:
                    print "Could not move file " + county + ".zip"
                    print sys.exc_info()[0]

    else:
        print "Skipping " + county + ": zip file already exists"
        errors.append([county + ".zip", "File Already Exists"])

if len(errors) > 0:
    print "\n----------------------------------------------------------------------------------"
    print "WARNING!! --> Errors were found with the following files: (" + str(len(errors)) + " total errors found)"
    for e in errors:
        print e[0] + ": " + e[1]
    print "----------------------------------------------------------------------------------"

end_time = time.time()
print("\n<--- Execution time: %s seconds --->" % (end_time - start_time))
print("<--- %s errors noted -->" % str(len(errors)))
