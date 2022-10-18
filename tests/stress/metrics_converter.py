import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass


import pandas as pd


def check_path(path):
    if not os.path.exists(path):
        new = Path(path)
        new.mkdir()

@dataclass
class RunMetrics:
    start_time: str
    end_time: str
    average_time: float
    total_test_time: timedelta
    max_value_cpu: float
    max_value_memory: float
    average_value_cpu: float
    average_value_memory: float


def get_metrics(path_to_csvfile: Path, run_type: str, run_identifier: str, n_runs: int = 5) -> RunMetrics:
    #taking in the fliepath
    data = pd.read_csv(path_to_csvfile)

    df2 = data.pivot(index="timeStamp",columns="label",values="elapsed")
    df2.index = df2.index.map(lambda v: datetime.utcfromtimestamp(v / 1000).strftime('%Y-%m-%d %H:%M:%S.%f'))
    creation_date = df2.index[0]
    # Remove date information from time value : > 11th char
    df2.index = df2.index.str.slice(start=11)
    df2["localhost Memory"] = df2["localhost Memory"] / 1000.0
    df2["localhost CPU"] = df2["localhost CPU"] / 1000.0

    temp_array = []

    for x in range(0,len(df2.index)):
        temp = df2.index[x]
        temp_array.append(temp)

    #print(temp_array)
    for x in range(1, len(temp_array)):
        a = datetime.strptime(temp_array[0],'%H:%M:%S.%f')
        b = datetime.strptime(temp_array[x],'%H:%M:%S.%f')
        temp_array[x] = (b-a).total_seconds()

    #saving the max values of the CPU and Memmory usage, and the start/end time of the test
    start_time = df2.index[0]
    end_time = df2.index[len(df2.index) - 1]
    average_time = temp_array[len(temp_array) - 1] / n_runs
    average_time_dateform = timedelta(seconds=average_time)
    total_test_time = timedelta(seconds=temp_array[len(temp_array) -1])


    max_value_cpu = df2["localhost CPU"].max()
    max_value_memory = df2["localhost Memory"].max()
    average_value_cpu = df2["localhost CPU"].mean()
    average_value_memory = df2["localhost Memory"].mean()

    #setting the first index to 0 
    temp_array[0] = 0
    df2.index = temp_array

    #giving a name to the index
    df2.index.name = "Timestamp"
    creation_date = creation_date[0:19]

    #creating the csv file where the results will be saved
    check_path("metrics")
    check_path(f"metrics/{run_identifier}")

    result_file = run_type + "metrics-" + str(creation_date) + ".csv"

    open(f"metrics/{run_identifier}/" + result_file, 'w+')

    #getting the path to the generated file
    path_to_metrics = Path(f"metrics/{run_identifier}/" + result_file)
    df2.to_csv(path_to_metrics, encoding='utf-8')
    os.remove(path_to_csvfile)
    log_path = Path("jmeter.log")
    if os.path.isfile(log_path) == True:
        os.rename(log_path, f"metrics/{run_identifier}/jmeter.log")

    return RunMetrics(
        start_time=start_time, 
        end_time=end_time, 
        average_time=average_time, 
        total_test_time=total_test_time,
        max_value_cpu=max_value_cpu, 
        max_value_memory=max_value_memory, 
        average_value_cpu=average_value_cpu, 
        average_value_memory=average_value_memory
    )

if __name__ == "__main__":
    #getting for the csv file name
    csv_file_path = Path(sys.argv[1])
    run_type = sys.argv[2]
    run_identifier = sys.argv[3]

    metrics = get_metrics(csv_file_path, run_type, run_identifier)

    #printing to the terminal 
    print("<=========================================>\n")
    print("The results are from a " + run_type + " command\n")
    print("Starting time : " + metrics.start_time + "      " + "Finishing time : " + metrics.end_time)
    print("Avarage run time :{:0>8} ".format(str(timedelta(seconds=metrics.average_time))) + " Total test time :{:0>8}".format(str(metrics.total_test_time)))
    print("\nMax CPU Usage % : " + str(metrics.max_value_cpu))
    print("\nMax Memory Usage % : " + str(metrics.max_value_memory))
    print("\nAvarage CPU Usage % : " + str(metrics.average_value_cpu))
    print("\nAvarage Memory Usage % : " + str(metrics.average_value_memory))
    print("\n<=========================================>")


