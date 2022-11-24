# Error - Pivoted shape measure columns exist error

## When it occurs

There are measure columns defined in a pivoted shape cube.  

An example cube structre which would result in this error looks like this:

| Location  | Median Commute Distance / miles | Another Observed Value | Measure             | Unit    |
|-----------|---------------------------------|------------------------|---------------------|---------|
| Sheffield | 2.1                             | 15.3                   | Median commute time | Minutes |
| Aberdeen  | 13.4                            | 22.9                   | Median commute time | Minutes |

But the cube's config could take the following form:

With the following [qube-config.json](../../configuration/qube-config.md) column mapping configuration:

```json
"columns": {
  "Median Commute Distance / miles": {
    "type": "observations",
    "measure": {
      "label": "Median commute distance"
    },
    "unit": {
      "label": "Miles"
    }
  },
  "Median commute time / mins": {
    "type": "observations"
  },
  "Measure": {
    "type": "measures"
  },
  "Unit": {
    "type": "units",
    "describes_observations":  "Another Observed Value"
  }
},
```

## How to fix

A pivoted shape cube can only have measures defined against an observation value column. The measure column approach used in the standard shape is incompatible with the pivoted shape.

This error may be a sign that your data is too complex to be represented in the pivoted shape; you may need to represent your data in the standard shape. If you wish to continue with the pivoted shape approach then you must remove the `measures` column.

For further guidance, please refer to the [shaping your data documentation](../../shape-data.md).
