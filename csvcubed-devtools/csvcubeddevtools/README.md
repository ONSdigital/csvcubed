# csvcubed - devtools

> Shared test functionality & dev dependencies which are commonly required.

The *devtools* package contains common packages necessary for development of *csvcubed* such as:

* behave - for behaviour testing / BDD
* docker - to execute docker containers, used to transform and test csvcubed outputs.
* black - auto-formatter to ensure consistent code formatting/style.

It also contains shared functionality to support testing, e.g. common *behave* test steps like checking that files exist, using temporary directories when testing as well as tools to copy test files to & from docker containers.

## Installation

This package should be installed as a [dev dependency](https://python-poetry.org/docs/cli#options-3) to ensure that end-users of *csvcubed* are not required to install development tools such as docker.



## API Documentation

The latest API Documentation for the package can be found [here](https://ci.floop.org.uk/job/GSS_data/job/csvcubed/job/main/lastSuccessfulBuild/artifact/devtools/docs/_build/html/index.html).

TODO: #217 Update API documentation location in csvcubed-devtools