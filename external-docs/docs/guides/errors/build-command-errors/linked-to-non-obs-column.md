# Error - Linked to non-observation column error

## When it occurs

A units or attribute column is linked to an observation value column that isn't actually an observation value column. E.g. linked to a dimension column.    

An example cube structre which would result in this error looks like this:

| Dimension | Attribute | Obs 1  | Obs 2  |
|---|---|---|---|
| A  | X | 1 | 2 |

But the cube's attribute (or unit) columns could have been configured like the following:
```json
"columns": {
      "Attribute": {
        "type": "attribute",
        "describes_observations": "Dimension"
      }
    },
```

## How to fix

Ensure that the linked column is an actual observation value column.
    
For further guidance, please refer to the [shaping your data documentation](https://gss-cogs.github.io/csvcubed-docs/external/guides/shape-data/).
