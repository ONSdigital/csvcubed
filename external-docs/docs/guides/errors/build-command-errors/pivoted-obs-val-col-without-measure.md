# Error - Pivoted observation value column without measure defined

## When it occurs

An observation value column has been defined without a measure linked within the column definition.

For example in the following cube:

| Location  | Median Commute Distance / miles | Median commute time / mins |
|-----------|---------------------------------|----------------------------|
| Sheffield | 2.1                             | 15.3                       |
| Aberdeen  | 13.4                            | 22.9                       |

With the following [qube-config.json](../../configuration/qube-config.md) column mapping configuration:

```json
"columns": {
  "Median Commute Distance / miles": {
    "type": "observations"
  },
  "Median commute time / mins": {
    "type": "observations",
    "measure": {
      "label": "Median commute time"
    },
    "unit": {
      "label": "Minutes"
    }
  }
},
```

Note that the `Median Commute Distance / miles` column does not have a measure defined against it.

## How to fix

In the pivoted shape an observation value column must have a measure linked directly against the column definition, e.g.

```json
{
  "Median Commute Distance / miles": {
    "type": "observations",
    "measure": {
      "label": "Median commute distance"
    },
    "unit": {
      "label": "Miles"
    }
  },
}
```

For further guidance, please refer to the [shaping your data documentation](../../shape-data/index.md).
