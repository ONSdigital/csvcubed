#!/bin/bash

# A bash script to cascade package updates between packages.
# i.e. if devtools has a new package installed, all dependent project's 
# `poetry.lock` files need to be updated. this script should do all of that
# `setup.py` should not be required, but we shall see. `pyproject.toml`

function poetry_update_setup_sync () {
    echo "====================== $1"
    cd $1
    poetry lock
    cd ..
}

# N.B. the order below here ensures that packages which are dependencies of other packages are updated first.
poetry_update_setup_sync "devtools"
poetry_update_setup_sync "sharedmodels"
poetry_update_setup_sync "pmd"
poetry_update_setup_sync "csvqb"
~