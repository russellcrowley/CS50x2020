import sys
import csv
import cs50

# check command line arguments
if len(sys.argv) != 2:
    print("Error, provide one house")
    sys.exit(1)
query = sys.argv[1]
# open database for writing
db = cs50.SQL("sqlite:///students.db")
# get list of stdents in house from database
houses = db.execute('SELECT * FROM students WHERE house = (?) ORDER BY last, first;', query)
# print results
for row in houses:
    if row['middle'] == None:
        print(row['first'], row['last'], 'born ', row['birth'])
    else:
        print(row['first'], row['middle'], row['last'], 'born ', row['birth'])