#!/bin/bash

# A bash script to cascade package updates between packages.
# i.e. is devtools has a new package installed, the `setup.py` file needs to be updated and all dependent projects' `pipfile.lock` files need to be updated.
# this script should do all of that for you.

function pipenv_update_setup_sync () {
    echo "====================== $1"
    cd $1
    pipenv update --pre --dev
    pipenv run pipenv-setup sync --pipfile
    cd ..
}

# N.B. the order below here ensures that packages which are dependencies of other packages are updated first.
pipenv_update_setup_sync "devtools"
pipenv_update_setup_sync "sharedmodels"
pipenv_update_setup_sync "pmd"
pipenv_update_setup_sync "csvqb"
