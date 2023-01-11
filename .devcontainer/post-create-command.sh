#!/bin/bash

# This runs as soon as the dev container has been created, but before the user has access to it.
# This is a great location to link the (bind-mounted) source code + container together.

pyenv local 3.11.1
pyenv exec pre-commit install
/csvcubed-venv/bin/poetry install
