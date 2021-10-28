#!/bin/bash

cd "csvcubed-devtools"
pipenv run sphinx-apidoc -F -M -a -P --tocfile index.rst -d 10 -E -o docs --implicit-namespaces -o docs csvcubeddevtools "setup*"
pipenv run sphinx-build -W -b html docs docs/_build/html
cd ..

cd "csvcubed-models"
pipenv run sphinx-apidoc -F -M -a -P --tocfile index.rst -d 10 -E --implicit-namespaces -o docs csvcubedmodels "setup*" "csvcubedmodels/scripts"
pipenv run sphinx-build -W -b html docs docs/_build/html
cd ..

cd "csvcubed-pmd"
pipenv run sphinx-apidoc -F -M -a -P --tocfile index.rst -d 10 -E --implicit-namespaces -o docs csvcubedpmd "setup*"
pipenv run sphinx-build -W -b html docs docs/_build/html
cd ..

cd "csvcubed"
pipenv run sphinx-apidoc -F -M -a -P --tocfile index.rst -d 10 -E --implicit-namespaces -o docs csvcubed "setup*"
pipenv run sphinx-build -W -b html docs docs/_build/html
cd ..
