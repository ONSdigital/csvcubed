# Error - both unit types defined

## When it occurs

The unit of measure is defined twice in the same cube.

## How to fix

It is possible to define units in two ways:

* **against the observed value column definition**, when all values in the cube are measured in the same unit.
* **as a units column**, where the cube contains observed values measured in different units.

Choose one way to express the units in your cube's JSON configuration file.
