# Error - CSV column literal with URI template

## When it occurs

An attribute column's mapping has a value URI template *and* a datatype defined.

## How to fix

An attribute can have values which are *either* **literal** values or **resources** represented by URIs, but it cannot have both.

* If the attribute **values are literals** then the column's mapping should **not have a value URI template**.
* If the attribute **values are resources** then the column's mapping should **not have a datatype**.
