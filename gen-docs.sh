#!/bin/bash

cd "devtools"
pipenv run sphinx-apidoc -F -M -a -P --tocfile index.rst -d 10 -E -o docs --implicit-namespaces -o docs devtools "setup*"
pipenv run sphinx-build -W -b html docs docs/_build/html
cd ..

cd "sharedmodels"
pipenv run sphinx-apidoc -F -M -a -P --tocfile index.rst -d 10 -E --implicit-namespaces -o docs sharedmodels "setup*" "sharedmodels/scripts" "sharedmodels/tests"
pipenv run sphinx-build -W -b html docs docs/_build/html
cd ..

cd "pmd"
pipenv run sphinx-apidoc -F -M -a -P --tocfile index.rst -d 10 -E --implicit-namespaces -o docs  pmd "setup*" "pmd/tests"
pipenv run sphinx-build -W -b html docs docs/_build/html
cd ..

cd "csvqb"
pipenv run sphinx-apidoc -F -M -a -P --tocfile index.rst -d 10 -E --implicit-namespaces -o docs csvqb "setup*" "csvqb/tests"
pipenv run sphinx-build -W -b html docs docs/_build/html
cd ..
