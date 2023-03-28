# Error - Hybrid shape error

## When it occurs

There are multiple observation value columns defined and at least one measure column defined. This is an invalid hybrid between standard and pivoted shapes.

An example cube structure which would result in this error looks like this:

| Location  | First Value | First Measure           | First Unit | Second Value | Second Measure      | Second Unit |
|-----------|-------------|-------------------------|------------|--------------|---------------------|-------------|
| Sheffield | 2.1         | Median commute distance | Miles      | 15.3         | Median commute time | Minutes     |
| Aberdeen  | 13.4        | Median commute distance | Miles      | 22.9         | Median commute time | Minutes     |

## How to fix

The dataset **must** adhere to a single supported data shape: either the standard shape **or** the pivoted shape.

For further guidance, please refer to the [shaping your data documentation](../../shape-data/index.md).
