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
import xlrd
import MyFunctions

# Prepare to time execution - get start time
start_time = time.time()

filePath = "../Database/"
filePrefix = "Libertarians"
fileSep = "-"
fileSuffix = ".db"

defaultDBfile = filePath + filePrefix + fileSuffix

# each db output file is named with a time component to avoid over-writing files
timeComponent = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

newDBFile = filePath+filePrefix+fileSep+timeComponent+fileSuffix


# check if preliminary database exists, end if it doesn't
# In the future, create the database if it isn't there.
if os.path.isfile(defaultDBfile):
    shutil.copyfile(defaultDBfile, newDBFile)
    print "Preliminary Database File copied to " + newDBFile
else:
    print "Preliminary Database File " + defaultDBfile + " Does Not Exist"
    sys.exit()


# Connect to the database
conn = sqlite3.connect(newDBFile)
cur = conn.cursor()


args = sys.argv

if len(args) < 2:
    print "ERROR - this file must be called with a valid & existing excel file"
    sys.exit(1)

if not os.path.isfile(args[1]):
    print "ERROR 1st argument must be a valid & existing excel file"
    sys.exit(1)a
else:
    print "Excel file found..."

book = xlrd.open_workbook(args[1])

for s in book.sheets():
    print 'Sheet:', s.name

    # Get column headers
    values = []
    for col in range(s.ncols):
        values.append(s.cell(0,col).value)
    print values

    if not MyFunctions.query_yes_no("Continue?"):
        sys.exit(0)

    sql = "CREATE TABLE IF NOT EXISTS national_dump"



conn.close()