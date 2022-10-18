import csv
import sys
from pathlib import Path
# this program will generate a csv file with a predefined number of colums and rows (preferabli each value unique)

def _generate_maximally_complex_csv(numb_rows: int, temp_dir: Path = Path("temp_dir"), max_num_measures: int = 20):
   #creating a temp file 
    temp_dir.mkdir()

    #filling up the csv file with random unique data for testing 
    with open(temp_dir / "stress.csv", "w+", newline="") as f:
        thewriter = csv.writer(f)

        # creating arrays to temporarely hold the data that will be placed in the csv file
        column_array = []
        rows_array = []
        unique_number = 0
        measure_number = 0

        column_array = [
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

        thewriter.writerow(column_array)

        # this for loop will append each rows maching the number of colums
        for x in range(1, numb_rows + 1):

            for i in range(0, len(column_array)):
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
                    if measure_number > (max_num_measures-1):
                        measure_number = 0
                elif i == 16:
                    row_value = "some Unit" + str(unique_number)
                    rows_array.append(row_value)
                else:
                    row_value = "value" + str(unique_number)
                    rows_array.append(row_value)

            thewriter.writerow(rows_array)

            rows_array = []

if __name__ == "__main__":
    # taking in a commandline argument to determine the number of rows
    numb_rows = int(sys.argv[1])

    _generate_maximally_complex_csv(numb_rows)