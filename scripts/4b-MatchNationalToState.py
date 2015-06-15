#!/usr/bin/env python

import sqlite3
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

sql =  "SELECT libertarians.SOS_VOTERID, LAST_NAME, FIRST_NAME, lat, long FROM libertarians "
sql += "LEFT JOIN locations on libertarians.SOS_VOTERID = locations.SOS_VOTERID "
sql += "WHERE libertarians.SOS_VOTERID NOT IN ( "
sql += "SELECT DISTINCT libertarian_id FROM libertarians_national WHERE libertarian_id != '' ) "
sql += "ORDER BY LAST_NAME, FIRST_NAME "
# sql += "LIMIT %s" % str(limit)

#print sql

cur.execute(sql)

numberProcessed = 0
matches = 0
for row in cur.fetchall():
    numberProcessed += 1

    #print row

    namesql =  "SELECT national.id, last, first, lat, long  FROM national "
    namesql += "LEFT JOIN locations on national.id = locations.national_id "
    namesql += "WHERE last LIKE \"" + row['LAST_NAME'] + "\" "
    namesql += "AND first LIKE \"" + row['FIRST_NAME'] + "\" "


    # print namesql
    cur.execute(namesql)

    for nameMatch in cur.fetchall():
        # print " -- ", nameMatch['id'], nameMatch['last'], nameMatch['first'], nameMatch['lat'], nameMatch['long']
        if row['lat'] == nameMatch['lat'] and row['long'] == nameMatch['long']:
            matches += 1
            print "MATCH FOUND! -- ", matches, nameMatch['first'], nameMatch['last']

            insertmatchsql = "insert into libertarians_national (national_id, libertarian_id) values ('" + nameMatch['id'] + "', '" + row['SOS_VOTERID'] + "')"

            # print insertmatchsql
            cur.execute(insertmatchsql)
            db.commit()

print "Number Processed: ", numberProcessed
print "Matches: ", matches




db.close()


if MyFunctions.query_yes_no("Copy libertarians_national table into default database for later use?"):
    src_conn = MyFunctions.open_db(dbfile)
    dest_conn = MyFunctions.open_db(defaultDBfile)

    MyFunctions.copy_table('libertarians_national',src_conn,dest_conn)



end_time = time.time()
print("\n<--- Execution time: %s seconds --->" % (end_time - start_time))
