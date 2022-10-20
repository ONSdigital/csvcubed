#!/bin/bash

trap "exit" INT TERM ERR
trap "kill 0" EXIT

timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

startAgent.sh &
# Gets the process that was started in the last command run
# and assigns it to the variable to later be killed.
P1=$!

jmeter -n -t buildcommandtest.jmx -Jrows=$1
jmeter -n -t inspectcommandtest.jmx -Jrows=$1

python metrics_converter.py buildmetrics.csv Build $timestamp
python metrics_converter.py inspectmetrics.csv Inpect $timestamp

kill $P1