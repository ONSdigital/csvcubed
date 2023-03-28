# Error - reserved URI value

## When it occurs

A dimension column contains a value which clashes with an identifier that is reserved by csvcubed.

e.g. a *new dimension* column contains the term `Code List` which clashes with the reserved `code-list` identifier.

## How to fix

Avoid using values which would clash with any csvcubed reserved identifiers.

<!-- TODO: Link to somewhere which helps the user define new dimensions. -->
<!-- TODO: Link to somewhere which explains the uri_safe transformation which applies to values like these. -->