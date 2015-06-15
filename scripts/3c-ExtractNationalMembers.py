#!/usr/bin/env python

import csv
import xlrd
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

filePath = "../National Data Dump/"
fileSuffix = "OH_Fulldump"
fileSep = "-"
fileType = ".XLS"

dbPath = "../Database/"
dbFile = "CurrentAndFormerLibertarians-2015-06-05-12-42-21.db"

conn = sqlite3.connect(dbPath + dbFile)
cur = conn.cursor()

workbook = xlrd.open_workbook(filePath + "2015-05-" + fileSuffix + fileType)
worksheet = workbook.sheet_by_index(0)

numRows = worksheet.nrows - 1
numCols = worksheet.ncols - 1

print numRows
print numCols

first_row = worksheet.row(0)
colNames = []

curr_row = 0
curr_cell = -1

while curr_cell < numCols:
    curr_cell += 1
    colNames.append(worksheet.cell_value(curr_row, curr_cell))

libertarians = []

curr_row = 0
while curr_row < numRows:
    curr_row += 1
    row = worksheet.row(curr_row)
    curr_cell = -1
    thisRow = []
    while curr_cell < numCols:
        curr_cell += 1

        try:
            cell = worksheet.cell(curr_row, curr_cell)
            # print cell.ctype
            if cell.ctype == xlrd.XL_CELL_DATE:
                #print "DATE!"
                date = datetime.datetime(1899,12,30)
                get_ = datetime.timedelta(int(worksheet.cell_value(curr_row, curr_cell)))
                get_col2 = str(date + get_)[:10]
                #print get_col2
                thisRow.append(get_col2)
            else:
                thisRow.append(worksheet.cell_value(curr_row, curr_cell))
        except:
            thisRow.append(worksheet.cell_value(curr_row, curr_cell))

    libertarians.append(thisRow)

print len(libertarians)


for row in libertarians:
    questionmarks = "?, " * (len(row) - 1)
    questionmarks += "?"
    cur.execute("INSERT OR REPLACE INTO national VALUES (" + questionmarks + ");", row)
    #conn.commit()
conn.commit()



end_time = time.time()
total_time = end_time - start_time
votersPerSecond = numVotersParsed / total_time
print("--- %s seconds ---" % str(total_time))
print("--- %s voters parsed ---" % str(numVotersParsed))
print("--- %s voters per second ---" % str(votersPerSecond))
print("--- %s Libertarians ---" % str(numLibertarians))
