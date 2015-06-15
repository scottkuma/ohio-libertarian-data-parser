#!/usr/bin/env python

import csv
import glob
import sqlite3
import sys
import os
import shutil
import time
import xlrd
import MyFunctions

databaseDirectory = "../Database/"

nationalDirectory = "../NationalDataDump/"
nationalFileDate = "2015-05-"
nationalFileSuffix = "OH_Fulldump.XLS"



# read first line out of National Data Dump file
workbook = xlrd.open_workbook(nationalDirectory + nationalFileDate + nationalFileSuffix)
worksheet = workbook.sheet_by_index(0)

numRows = worksheet.nrows - 1
numCols = worksheet.ncols - 1

first_row = worksheet.row(0)
fields = []

curr_row = 0
curr_cell = -1

while curr_cell < numCols:
    curr_cell += 1
    append_val = 2
    cellVal = worksheet.cell_value(curr_row, curr_cell)
    if cellVal in fields:
        while (cellVal + str(append_val)) in fields:
            append_val += 1
        fields.append(cellVal + str(append_val))
    else:
        fields.append(worksheet.cell_value(curr_row, curr_cell))

# does the database even exist?

# open the database file
db = sqlite3.connect(databaseDirectory + 'Libertarians.db')
cur = db.cursor()

cur.execute("PRAGMA table_info('national')")
pragma = cur.fetchall()

# extract db field names from national
dbfields = [str(x[1]) for x in pragma]

if dbfields == fields:
    print "DB matches file format"
else:
    print "DB does not match file format"
    print len(dbfields), "fields in database"
    print len(fields), "fields in files"

    if MyFunctions.query_yes_no("Replace db schema with file schema?", "no"):
        print "\nOk...."
        print "Dropping table: national"
        db.execute('''DROP TABLE IF EXISTS national''')
        db.commit()
        print "Recreating table: national with new file format"
        sql = "CREATE TABLE national ("
        fields_added = 0
        for afield in fields:
            if fields_added == 0:
                fieldname = ""
            else:
                fieldname = ", "
            print fieldname
            if afield == "id":
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
