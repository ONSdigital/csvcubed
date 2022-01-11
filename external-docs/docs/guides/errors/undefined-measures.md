# Error - undefined measures

## When it occurs

Some of the measures referenced by a measure dimension column's values are not defined.

This error only arises where new measures are defined in the measure dimension's column JSON mapping. Existing measures are not currently validated by csvcubed.

## How to fix

Ensure that all of the values in your measure dimension column have measures which defined in the column mapping.

<!-- TODO: Link to somewhere which helps the user define measures. -->