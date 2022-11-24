# Error - Hybrid shape error

## When it occurs

There are mutliple observation value columns defined without measures linked and at least one measure column defined. This is an erroneous hybrid between standard and pivoted shape.    

An example cube structre which would result in this error looks like this:

| Dimension | Obs 1 | Obs 2 | Measure 1 | Measure 2 |
|---|---|---|---|---|
| A | 1 | 2 | X | Y |

## How to fix

The dataset must adhere to one of the accepted shapes of data (standard or pivoted). 
   
For further guidance, please refer to the [shaping your data documentation](https://gss-cogs.github.io/csvcubed-docs/external/guides/shape-data/).
