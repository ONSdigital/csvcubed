# How to Profile csvcubed

## packages required

```
brew install flamegraph
```
cProfile comes with standard python library

### step 1

Run a poetry install to make sure the shell is up to date (for the flameprof package) 

### step 2

import `cProfile` in the script you want to test. 

the script will generate a new csv file and then execute the build command.
Then it will measure the process of the build and stire the data in a prof file.

example:
```
cProfile.run(f"main(Path('{path to the csv file}'), Path('{path to the json file}'), Path('{path to the temporary file directory}'))", filename="name of file where to store results")
```
example:

 `cProfile.run(f"main(Path('{csv_path}'), Path('{qube_config_json_path}'), Path('{tmp_dir}'))", filename="csvcubed_build.prof")`

### step 3

to convert the file to a flame graph use the command 

```bash
python -m flameprof --format=log results.prof | flamegraph.pl > requests-flamegraph.svg 
```

### step 4

the command `open requests-flamegraph.svg`  will open the file in a web browser.


