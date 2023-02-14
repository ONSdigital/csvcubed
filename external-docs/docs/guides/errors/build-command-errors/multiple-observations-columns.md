# Error - multiple observations columns defined (Deprecated)

## Deprecation warning

This validation error will no longer be raised from csvcubed v0.1.18. This is because from v0.1.18, csvcubed supports pivoted multi-measure data sets which have more than one observations columns defined.

Please update your csvcubed version using `pip install csvcubed --upgrade` (for PyPI) or `conda update csvcubed` (for Anaconda).

## When it occurs

Multiple observed value columns are defined in the same cube.

## How to fix

Ensure that only one column represents observed values in your cube. See [shaping your data](../../shape-data/index.md) for more information on the shapes of data accepted by csvcubed.
