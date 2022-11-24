# Error - Linked to non-observation column error

## When it occurs

A units or attribute column is linked to an observation value column that isn't actually an observation value column.

For example in the following cube:

| Location  | Median Commute Distance / miles | Median commute time / mins | Commute Time Notes                                        |
|-----------|---------------------------------|----------------------------|-----------------------------------------------------------|
| Sheffield | 2.1                             | 15.3                       | Excludes individuals teleporting to work.                 |
| Aberdeen  | 13.4                            | 22.9                       | Includes oil rig workers commuting to offshore platforms. |

With the following [qube-config.json](../../configuration/qube-config.md) column mapping configuration:

```json
{
  "Commute Time Notes": {
    "type": "attribute",
    "data_type": "string",
    "describes_observations": "Location"
  }
},
```

In this cube, the `Location` column represents a [dimension](../../../glossary/index.md#dimension) and not [observed values](../../../glossary/index.md#observation--observed-value).

## How to fix

Ensure that the linked column is a column containing [observed values](../../../glossary/index.md#observation--observed-value).

For further guidance, please refer to the [shaping your data documentation](https://gss-cogs.github.io/csvcubed-docs/external/guides/shape-data/).
