# Error - CSV column URI template missing

## When it occurs

A column mapping reuses:

* existing measures,
* existing units,
* an existing dimension,
* an existing code-list,
* or an existing attribute.

**and** either:

* the value URI template has not been set
* or the correct value cannot be inferred by querying PMD.

## How to fix

Ensure that you have an active internet connection and can reach the PMD platform. Once there, ensure that the existing resource you are reusing is correctly defined.

If the above is not possible, ensure that the value URI template is correctly set in the column's mapping.

<!-- TODO: Link to somewhere which helps the user define CSV Column URI templates. -->

<!-- TODO: Link to some document discussing why we query PMD for certain information and where PMD lives. -->
