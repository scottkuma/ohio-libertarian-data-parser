#!/usr/bin/env python

import sqlite3
import requests
import sys
import os
import time
import MyFunctions
from subprocess import call

# Prepare to time execution - get start time
start_time = time.time()

filePath = "../Database/"
filePrefix = "Libertarians"
fileSep = "-"
fileSuffix = ".db"

csvPath = "../CSV/"

defaultDBfile = filePath + filePrefix + fileSuffix

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

for cd in range(1,17):

    sql =  "SELECT * FROM libertarianswithlocation "
    sql += "WHERE CONGRESSIONAL_DISTRICT = '{0:02d}' ".format(cd)
    sql += "ORDER BY LAST_NAME, FIRST_NAME "
    # sql += "LIMIT %s" % str(limit)

    print sql
    outCommand = "sqlite3 -header -csv {0} \"{1}\" > {3}WithLocation{2:02d}.csv".format(dbfile, sql, cd, csvPath)
    print outCommand
    call(outCommand, shell=True)