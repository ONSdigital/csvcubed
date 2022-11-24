# Error - Attribute not linked to observed value column

## When it occurs

In a multi-unit pivoted data set, each units or attribute column must be linked to an observation values column.

For example in the following cube:

| Location  | Median Commute Distance / miles | Median commute time / mins | Commute Time Notes                                        |
|-----------|---------------------------------|----------------------------|-----------------------------------------------------------|
| Sheffield | 2.1                             | 15.3                       | Excludes individuals teleporting to work.                 |
| Aberdeen  | 13.4                            | 22.9                       | Includes oil rig workers commuting to offshore platforms. |

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
    "type": "observations",
    "measure": {
      "label": "Median commute time"
    },
    "unit": {
      "label": "Minutes"
    }
  },
  "Commute Time Notes": {
    "type": "attribute",
    "data_type": "string"
  }
},
```

## How to fix

Specify the observed values colummn which the units or attribute column describes, e.g.

```json
{
  "Commute Time Notes": {
    "type": "attribute",
    "data_type": "string",
    "describes_observations": "Median commute time / mins"
  }
}
```

For further guidance, please refer to the [shaping your data documentation](https://gss-cogs.github.io/csvcubed-docs/external/guides/shape-data/).
