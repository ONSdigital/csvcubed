# How to Profile csvcubed

## packages required

```
poetry add py-spy
```


### step 1

Run a poetry install to make sure the shell is up to date (for the py-spy package) 

### step 2


`python py-spy record --rate [add number to record samples per second(recommended 200)] --full-filenames[display full s
file path] --function[record by function call] --subprocesses[record sub calls] -- python [insert script name to measured]`
 
The script will generate a new csv file and then execute the build command.
The py-spy will reord the measures. This command has to be ran from local terminal with sudo.
The command does not function within the devcontainer.  

example:
```
sudo python py-spy record --rate 200 --full-filenames --function --subprocesses -- python csvcubed_build_process.py
```

### step 3

After the command executes it will produce a svg file.

open file with :

 `open [inserts svg file]`

 The file will be oepened in a web browser.

### step 4

The inspect command can be ran with the `csvcubed_inspect_process.py`. This command also requires the sudo command and can be ran from local terminal.

example:
`sudo python py-spy record --rate 200 --full-filenames --function --subprocesses -- python csvcubed_inspect_process.py`