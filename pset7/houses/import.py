import sys
import csv
import cs50

if len(sys.argv) != 2:
    print("Error, provide one CSV file")
    sys.exit(1)
# open database for writing
db = cs50.SQL("sqlite:///students.db")
# open CSV for reading
with open(sys.argv[1], "r") as characters:
    # create reader
    reader = csv.DictReader(characters)
    for row in reader:
        # split nameto determine length
        name = row["name"].split()
        house = row["house"]
        # load student into database
        if len(name) == 2:
            db.execute("INSERT into students(first, middle, last, house, birth) VALUES (?, ?, ?, ?, ?)",
                       name[0], None, name[1], row["house"], row["birth"])
        else:
            db.execute("INSERT into students(first, middle, last, house, birth) VALUES (?, ?, ?, ?, ?)",
                       name[0], name[1], name[2], row["house"], row["birth"])