# Error - Pivoted observation value column without measure defined

## When it occurs

An observation value column has been defined without a measure linked within the column definition. 

An example cube structre which would result in this error looks like this:

| Dimension | Attribute | Obs 1 (measure linked) | Obs 2 (no measure linked) |
|---|---|---|---|
| A  | X | 1 | 2 |

But the cube's observation value columns could have been configured like the following:
```json
"columns": {
      "Obs 1 (measure linked)": {
        "type": "observations",
        "measure": {
                "label": "Measure",
                "from_existing": "http://example.com/measures/some-measure"
            },
      },
      "Obs 2 (no measure linked)": {
        "type": "observations",
      }
    },
```

## How to fix

In the pivoted shape an observation value column must have a measure linked directly from within the column definition.   
 
For further guidance, please refer to the [shaping your data documentation](https://gss-cogs.github.io/csvcubed-docs/external/guides/shape-data/).
