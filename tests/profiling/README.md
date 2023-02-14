# How to Profile csvcubed

A profile is a set of statistics that describes how often and for how long various parts of the program executed.

## Flamegraph Profiling

Flamegraph allow to visualize relations between functions in a very compact and understandable manner
### step 1

Run a poetry install to make sure the shell is up to date (for the py-spy package, memory_profiler and matplotlib) 

### step 2


```
sudo py-spy record --rate [add number to record samples per second(recommended 200)] --full-filenames[display full s
file path] --function[record by function call] --subprocesses[record sub calls] -- python [insert script name to measured]
```
 
The script will generate a new csv file and then execute the build command.
The py-spy will reord the measures. This command has to be ran from local terminal with sudo.
The command does not function within the devcontainer.  

example:
```
sudo py-spy record --rate 200 --full-filenames --function --subprocesses -- python csvcubed_build_process.py
```

### step 3

After the command executes it will produce a svg file.

open file with :

 `open [inserts svg file]`

 The file will be oepened in a web browser.

### step 4

The inspect command can be ran with the `csvcubed_inspect_process.py`. This command also requires the sudo command and can be ran from local terminal.

example:
`sudo py-spy record --rate 200 --full-filenames --function --subprocesses -- python csvcubed_inspect_process.py`

## Memory Profiling

Memory Profiling is when the amount of RAM usage is measured and displayed, for optimization porpouses(either line-by-line or by function).
### Step 1

add `@profile` as a decorator, at the function you want to investigate.

### Step 2

run command `mprof run --python python [include script ]`

example: 
`mprof run --python python csvcubed_inspect_process.py`

this will run the memory profiler and output the results to the terminal.

### Step 3

run command to create and save graph as a png file.

`mprof plot --output [include filename]`

example: 
`mprof plot --output csvcubed_inpect_memory_profile.png`


