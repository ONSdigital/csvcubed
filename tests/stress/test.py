import csv
import sys

# this program will generate a csv file with a predefined number of colums and rows (preferabli each value unique)

# taking in a commandline argument to determine the number of rows
numb_rows = int(sys.argv[1])

# creating a csv file
with open("mytest.csv", "w", newline="") as f:
    thewriter = csv.writer(f)

    # creating arrays to temporarely hold the data that will be placed in the csv file
    collum_array = []
    rows_array = []
    unique_number = 0

    collum_array = [
        "Year",
        # "Dim2",
        # "Dim3",
        # "Dim4",
        # "Dim5",
        # "Dim6",
        # "Dim7",
        # "Dim8",
        # "Dim9",
        # "Dim10",
        "Attribute1",
        "Attribute2",
        "Attribute3",
        "Attribute4",
        "Attribute5",
        "Measure",
        "Unit",
    ]

    # this for loop will determine the number of colums in the file
    # for i in range(1, 18):
    #    colum_name = "colum" + str(i)
    #    collum_array.append(colum_name)

    thewriter.writerow(collum_array)

    # this for loop will append each rows maching the number of colums
    for x in range(1, numb_rows + 1):

        for i in range(1, len(collum_array)):
            unique_number += 1
            row_value = "value" + str(unique_number)
            rows_array.append(row_value)

        thewriter.writerow(rows_array)

        rows_array = []

"""
    "columns": {
        "dim1": {
            "type": "dimension"
        }
    }
"""
