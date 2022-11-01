#!/bin/bash

trap "exit" INT TERM ERR
trap "kill 0" EXIT

# Fail on errors (and other things)
set -euo pipefail

timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

1>/dev/null startAgent.sh &
# Gets the process that was started in the last command run
# and assigns it to the variable to later be killed.
P1=$!

echo "Now running build command"
1>/dev/null jmeter -n -t buildcommandtest.jmx -Jrows=$1 
echo "Processing metrics for build command"
python metrics_converter.py buildmetrics.csv Build $timestamp

echo "Now running inspect command"
1>/dev/null jmeter -n -t inspectcommandtest.jmx -Jrows=$1
echo "Killing server agent"
kill $P1 || true
echo "Processing metrics for inspect command"
python metrics_converter.py inspectmetrics.csv Inpect $timestamp

