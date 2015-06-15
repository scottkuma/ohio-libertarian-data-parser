This set of scripts is designed to download and parse county voter files provided by
the Ohio Secretary of State.

These scripts are designed to be run from a LINUX or OSX box that has wget available. 
They MAY run on a windows box, if wget is available on that box.  The scripts are programmed
in the PYTHON programming language or BASH scripting language, so these would also need to be 
installed on any box in order for the scripts to run. 

NOTE:  DO NOT RUN THESE SCRIPTS FROM A FOLDER LOCATED ON DROPBOX WHILE DROPBOX IS ACTIVATED!  
       You'll kill your download speeds. Either run this on a local folder & upload to dropbox 
       later, or pause DropBox's sync and re-enable it after completing.

Scripts & Functions:  (run in this order, generally)
====================

1-DownloadVoterFiles.py: Download files from the Ohio SOS website & do minor checks for integrity
	Time to run: Highly dependent on your internet speeds

2-VerifyFilesAndDBStructure.py: Verifies existence of database file, confirms database structure & 
  checks all of the downloaded files to ensure that they are of the same database format.
	Time to run: Under a minute

3-ExtractLibertarians.py: Parse the files into a SQLite database  
	Time to run: ~ 10 minutes

4-Geolocate.py: Geolocates libertarian members based on street address
	Time to run: 5 minutes seconds per 1000 voters
	Usage: python 4-Geolocate.py path/to/databasefile

3-ExportCSV.sh:  A shell script to export a csv of the Libertarians table from the sqlite3 db 
created in the previous step.  
	Time to run: under 30 seconds
	Usage: ExportCSV.sh database_file output_file

OTHER INFORMATION:
==================

The .db file created by this process is an SQLite database, and can be viewed/manipulated by
various means, including SQLiteman (Linux), SQLiteBrowser (Windows), etc.
