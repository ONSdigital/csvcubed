# Error - both measure types defined

## When it occurs

The population characteristic being measured is defined twice in the same cube.

## How to fix

It is possible to define measures in two ways:

* **against the observed value column definition**, when all values in the cube represent the same population characteristic.
* **as a measures column**, where the cube contains observed values measuring different population characteristics.

Choose one way to express the observation's measure in your cube's JSON configuration file.
