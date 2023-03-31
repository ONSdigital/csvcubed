#!/bin/bash

# You must have installed the spellchecker node package first:
# (sudo) npm install --global spellchecker-cli

spellchecker \
    --files "**/*.md" \
    --dictionaries docs/dict_manual_definitions.txt \
    --language en-GB \
    --ignore \
        'v[0-9]+(\.[0-9])*' \
        '[0-9]+[A-Za-z]' \
        '[0-9]{4}-[0-9]{2}-[0-9]{2}(T[^\s]+)?' \
        '[0-9]{4}-[QWH][0-9]{1,2}' \
        '[QWH][0-9]{1,2}' \
        '(P([0-9]+[YMD])+|T([0-9]+[HMS])+|P([0-9]+[YMD])+T([0-9]+[HMS])+)' \
        '[ESWNK][0-9]{8}'


# Ignore definitions in order:
#
# Ignore `v1.x`, etc. versions.
# Ignore numbers with units, e.g. `100m`
# Ignore date-time definitions.
# Ignore reference.data.gov.uk half/quarter/week definitions, e.g. `2002-H1`, `2020-Q4`, `2021-W32`
# Ignore reference.data.gov.uk half/quarter/week definitions, e.g. `H1`, `Q4`, `W32`
# Ignore ISO 8601 durations.
# Ignore things that look like ONS geography codes.