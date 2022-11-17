# Error - Pivoted shape measure columns exist error

## When it occurs

There are meaasure columns defined in a pivoted shape cube. 

## How to fix

A pivoted shape cube can only have measures defined against an observation value column instead of in their own column. Remove measure columns from the pivoted shape cube and ensure that existing linked measures are correct.
   
For further guidance, please refer to the [shaping your data documentation](https://gss-cogs.github.io/csvcubed-docs/external/guides/shape-data/).
