# Error - Hybrid Shape Error

## When it occurs

There are mutliple observation value columns defined without measures linked and at least one measure column defined.
But there are also observation value column(s) with linked measures.
This is an erroneous hybrid between standard and pivoted shape. 

## How to fix

The dataset must adhere to one of the accepted shapes of data (standard or pivoted).
Please see this documentation page for further information: https://gss-cogs.github.io/csvcubed-docs/external/guides/shape-data/

<!-- TODO: Link to somewhere which helps the user define measures. -->