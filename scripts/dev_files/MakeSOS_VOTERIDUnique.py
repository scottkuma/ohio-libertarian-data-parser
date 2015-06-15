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
fileSuffix = ".db"

dbfile = filePath + filePrefix + fileSuffix



try:
    db = sqlite3.connect(dbfile)
    db.row_factory = sqlite3.Row  # allows string index access to db rows (like PHP)
    cur = db.cursor()

except:
    print "ERROR opening database file: %s" % dbfile
    raise

print "Connected to database file..."

dt_sql = "DROP TABLE IF EXISTS locations2"
cur.execute(dt_sql)

# Create new table
ct_sql = """CREATE TABLE IF NOT EXISTS locations2 (
"ID" INTEGER PRIMARY KEY,
"SOS_VOTERID" TEXT UNIQUE ON CONFLICT REPLACE,
"NATFILE_ID" TEXT UNIQUE ON CONFLICT REPLACE,
"LAT" TEXT,
"LONG" TEXT,
"RELEVANCE" REAL,
"TIMESTAMP" DATETIME DEFAULT CURRENT_TIMESTAMP)"""""

print ct_sql


cur.execute(ct_sql)
db.commit()

# limit = 10

sql =  "SELECT * FROM locations "

cur.execute(sql)

rowsProcessed = 0

for row in cur.fetchall():
    rowsProcessed += 1
    ins_sql = "INSERT OR REPLACE INTO locations2 ('SOS_VOTERID', 'LAT', 'LONG', 'RELEVANCE') VALUES "
    ins_sql += "('%s', '%s', '%s', '%s')" % (row['SOS_VOTERID'], row['LAT'], row['LONG'], row['RELEVANCE'])

    print ins_sql
    cur.execute(ins_sql)

db.commit()
db.close()

end_time = time.time()
print("\n<--- Execution time: %s seconds --->" % (end_time - start_time))