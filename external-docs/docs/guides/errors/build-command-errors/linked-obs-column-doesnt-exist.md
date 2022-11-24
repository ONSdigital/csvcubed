# Error - Linked observation column doesn't exist error

## When it occurs

A unit or attribute column is linked to an observation value column that doesn't appear to exist.   

An example cube structre which would result in this error looks like this:

| Dimension | Attribute | Obs 1  | Obs 2  |
|---|---|---|---|
| A | X | 1 | 2 |

But the cube's attribute (or unit) columns could have been configured like the following:
```json
"columns": {
      "Attribute": {
        "type": "attribute",
        "describes_observations": "Obs 3 (doesn't exist)"
      }
    },
```

## How to fix

Ensure that the linked observation value column has the correct name corresponding to a existing observation value column in the cube.    

For further guidance, please refer to the [shaping your data documentation](https://gss-cogs.github.io/csvcubed-docs/external/guides/shape-data/).
