import csv
import sys
import tempfile
import os
from pathlib import Path
# this program will generate a csv file with a predefined number of colums and rows (preferabli each value unique)

# taking in a commandline argument to determine the number of rows
numb_rows = int(sys.argv[1])


#creating a temp file 
temp_dir = Path("temp_dir")
temp_dir.mkdir()


#filling up the csv file with random unique data for testing 
with open(temp_dir / "inspectmetrics.csv", "w+", newline="") as f:
    thewriter = csv.writer(f)

    # creating arrays to temporarely hold the data that will be placed in the csv file
    collum_array = []
    rows_array = []
    unique_number = 0
    measure_number = 0

    collum_array = [
        "Dim1",
        "Dim2",
        "Dim3",
        "Dim4",
        "Dim5",
        "Dim6",
        "Dim7",
        "Dim8",
        "Dim9",
        "Dim10",
        "Attribute1",
        "Attribute2",
        "Attribute3",
        "Attribute4",
        "obs",
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

        for i in range(0, len(collum_array)):
            unique_number += 1
            if i < 10:
                row_value = "A Dimension" + str(unique_number)
                rows_array.append(row_value)
            elif i == 14:
                row_value = unique_number * 2
                rows_array.append(row_value)
            elif i == 15:
                measure_number += 1
                row_value = "A measure" + str(measure_number)
                rows_array.append(row_value)
                if measure_number > 19:
                    measure_number = 0
            elif i == 16:
                row_value = "some Unit" + str(unique_number)
                rows_array.append(row_value)
            else:
                row_value = "value" + str(unique_number)
                rows_array.append(row_value)

        thewriter.writerow(rows_array)

        rows_array = []


# Run the build command using the created stress.csv in the temp_dir
os.chdir(temp_dir)
os.system("csvcubed build stress.csv -c ../test-qube-config.json")

