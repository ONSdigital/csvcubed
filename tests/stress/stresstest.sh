#! /bin/bash

trap "exit" INT TERM ERR
trap "kill 0" EXIT

startAgent.sh &
# Gets the process that was started in the last command run
# and assigns it to the variable to later be killed.
P1=$!

jmeter -n -t buildcommandtest.jmx -Jrows=$1
jmeter -n -t inspectcommandtest.jmx -Jrows=$1

python metrics_converter.py buildmetrics.csv Build
python metrics_converter.py inspectmetrics.csv Inpect

kill $P1