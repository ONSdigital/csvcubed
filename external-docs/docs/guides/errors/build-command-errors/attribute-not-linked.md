# Error - Attribute not linked

## When it occurs

A units or attribute column is defined but it is not linked to any observation value column.    

An example cube structre which would result in this error looks like this:

| Dimension | Attribute | Obs 1 | Obs 2 |
|---|---|---|---|
| A | X | 1 | 2 |

But the cube's attribute (or unit) columns could have been configured like the following:
```json
"columns": {
      "Attribute": {
        "type": "attribute",
      },
      "Obs 1": {
        "type": "observations",
        "measure": {
                "label": "Measure",
                "from_existing": "http://example.com/measures/some-measure"
            },
      },
      "Obs 2": {
        "type": "observations",
        "measure": {
                "label": "Another Measure",
                "from_existing": "http://example.com/measures/another-measure"
            },
      }
    },
```

## How to fix

In the pivoted shape a unit or attribute column must be directly linked to a observation column.   
 
For further guidance, please refer to the [shaping your data documentation](https://gss-cogs.github.io/csvcubed-docs/external/guides/shape-data/).
