# Error - Pivoted shape measure columns exist error

## When it occurs

There are measure columns defined in a pivoted shape cube.  

An example cube structre which would result in this error looks like this:

| Dimension | Some Measure | Obs 1 (a measure linked) | Obs 2 (another measure linked) |
|---|---|---|---|
| A | X | 1 | 2 |

But the cube's config could take the following form:
```json
"columns": {
    "Some Measure": {
        "Type": "measure"
    },
      "Obs 1 (a measure linked)": {
        "type": "observations",
        "measure": {
                "label": "A Measure",
                "from_existing": "http://example.com/measures/a-measure"
            },
      },
      "Obs 2 (another measure linked)": {
        "type": "observations",
        "measure": {
                "label": "Another Measure",
                "from_existing": "http://example.com/measures/another-measure"
            },
      }
    },
```

## How to fix

A pivoted shape cube can only have measures defined against an observation value column instead of in their own column. Remove measure columns from the pivoted shape cube and ensure that existing linked measures are correct.
   
For further guidance, please refer to the [shaping your data documentation](https://gss-cogs.github.io/csvcubed-docs/external/guides/shape-data/).
