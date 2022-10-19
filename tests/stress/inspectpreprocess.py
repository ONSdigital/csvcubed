import csv
import sys
import os
from pathlib import Path
from buildpreprocess import _generate_maximally_complex_csv

# this program will generate a csv file with a predefined number of colums and rows (preferabli each value unique)

if __name__ == "__main__":
    # taking in a commandline argument to determine the number of rows
    numb_rows = int(sys.argv[1])

    _generate_maximally_complex_csv(numb_rows)

    #creating a temp file 
    temp_dir = Path("temp_dir")

    # Run the build command using the created stress.csv in the temp_dir
    os.chdir(temp_dir)
    os.system("csvcubed build stress.csv -c ../test-qube-config.json")

