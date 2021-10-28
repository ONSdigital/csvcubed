#!/bin/bash

cd "csvcubed-devtools" || exit 1
poetry run sphinx-apidoc -F -M -a -P --tocfile index.rst -d 10 -E -o docs --implicit-namespaces -o docs csvcubeddevtools "setup*" || exit 1
poetry run sphinx-build -W -b html docs docs/_build/html || exit 1
cd ..

cd "csvcubed-models" || exit 1
poetry run sphinx-apidoc -F -M -a -P --tocfile index.rst -d 10 -E --implicit-namespaces -o docs csvcubedmodels "setup*" "csvcubedmodels/scripts" || exit 1
poetry run sphinx-build -W -b html docs docs/_build/html || exit 1
cd ..

cd "csvcubed-pmd" || exit 1
poetry run sphinx-apidoc -F -M -a -P --tocfile index.rst -d 10 -E --implicit-namespaces -o docs csvcubedpmd "setup*" || exit 1
poetry run sphinx-build -W -b html docs docs/_build/html || exit 1
cd ..

cd "csvcubed" || exit 1
poetry run sphinx-apidoc -F -M -a -P --tocfile index.rst -d 10 -E --implicit-namespaces -o docs csvcubed "setup*" || exit 1
poetry run sphinx-build -W -b html docs docs/_build/html || exit 1
cd ..
