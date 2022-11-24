# Error - Duplicate measures error

## When it occurs

In the pivoted shape, two or more observation value columns cannot be represented by identical measures.    

An example cube structre which would result in this error looks like this:

| Dimension | Obs 1 (a measure linked) | Obs 2 (a measure linked) |
|---|---|---|
| A | 1 | 2 |

But the cube's config could take the following form:
```json
"columns": {
      "Obs 1 (a measure linked)": {
        "type": "observations",
        "measure": {
                "label": "A Measure",
                "from_existing": "http://example.com/measures/a-measure"
            },
      },
      "Obs 2 (a measure linked)": {
        "type": "observations",
        "measure": {
                "label": "Another Measure",
                "from_existing": "http://example.com/measures/a-measure"
            },
      }
    },
```

## How to fix

Ensure that each observation value column is linked to a unique measure. 

For further guidance, please refer to the [shaping your data documentation](https://gss-cogs.github.io/csvcubed-docs/external/guides/shape-data/).
