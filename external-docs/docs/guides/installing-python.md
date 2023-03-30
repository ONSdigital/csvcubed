# Installing Python

csvcubed requires python to function. It has been tested with versions:

* 3.9
* 3.10
* 3.11

If you do not have a favoured way of managing your python environment or packages, we recommend using [miniconda](https://docs.conda.io/en/latest/miniconda.html). You should not use your system installation of python especially on MacOS or Linux as this may impact other system-critical functions.

## miniconda installation

To install miniconda, go to [this link](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).

Once you have installed miniconda, you will need to configure an environment specifically for csvcubed:

```bash
# create a new environment using python 3.11
conda create -n csvcubed python='3.11' -y
```

If you are using miniconda, you must be inside your `csvcubed` environment before running any commands:

```bash
# enter the csvcubed python 3.11 environment
conda activate csvcubed
```

## Manual installation (advanced)

[Download and install](https://www.python.org/downloads/) your chosen version of python.
