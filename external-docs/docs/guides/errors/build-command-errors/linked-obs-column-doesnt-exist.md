# Error - Linked observations column doesn't exist error

## When it occurs

A units or attribute column is linked to an observation value column that doesn't exist in the CSV file.

For example in the following cube:

| Location  | Median Commute Distance / miles | Median commute time / mins | Commute Time Notes                                        |
|-----------|---------------------------------|----------------------------|-----------------------------------------------------------|
| Sheffield | 2.1                             | 15.3                       | Excludes individuals teleporting to work.                 |
| Aberdeen  | 13.4                            | 22.9                       | Includes oil rig workers commuting to offshore platforms. |

With the following [qube-config.json](../../configuration/qube-config/index.md) column mapping configuration:

```json
{
  "Commute Time Notes": {
    "type": "attribute",
    "data_type": "string",
    "describes_observations": "Mean income / GBP"
  }
},
```

Note that the `Mean income / GBP` column does not exist in the CSV file.

## How to fix

Ensure that the linked observation value column has the correct name corresponding to an existing observed values column in the CSV.

For further guidance, please refer to the [shaping your data documentation](../../shape-data/index.md).
