# How to Profile csvcubed

## packages required

```
brew install flamegraph
```
cProfile comes with standard python library

### step 1

Run a poetry install to make sure the shell is up to date (for the flameprof package) 

### step 2

use the command in the terminal:

```
python -m cProfile -o [inster file where to save the data] [instert filename that needs to be measured]
```
example: `python -m cProfile -o output.2.txt cpfolife_test.py`

### step 3

to convert the file to a flame graph use the command 

```bash
python -m flameprof --format=log output.2.txt | flamegraph.pl > requests-flamegraph.svg 
```

### step 4

the command `open requests-flamegraph.svg`  will open the file in a web browser.


