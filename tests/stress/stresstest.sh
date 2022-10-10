#! /bin/bash

build = `sh jmeter -n -t buildcommandstest.jmx -l buildlogs.jtl`
echo $build

inspect = `sh jmeter -n -t inspectcommandstest.jmx -l inspectlogs.jtl`
echo $inspect
