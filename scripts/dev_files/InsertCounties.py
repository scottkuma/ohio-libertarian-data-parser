import csv, sqlite3, glob
conn = sqlite3.connect("Libertarians.sl3")
curs = conn.cursor()

curs.execute("CREATE TABLE IF NOT EXISTS Counties (id INTEGER PRIMARY KEY, COUNTY_NAME TEXT);")

infile = 'counties.txt'

reader = csv.reader(open(infile, 'r'), delimiter=',')
x = 1
for row in reader:
    to_db = [x, row[0]]
    print to_db, len(to_db)
    curs.execute("INSERT OR IGNORE INTO Counties VALUES (?, ?);", to_db)
    conn.commit()
    x += 1
