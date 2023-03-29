# Error - Attribute has no cell URI template or attribute values

## When it occurs

If you configure an Existing Resource attribute, but do not specify a `cell_uri_template`, and the attribute column does not contain any values, this will raise an error.

For example, in the following cube:

| AREACD    | AREANM        | Variable Name                                                | Value | Observation Status |
|-----------|---------------|--------------------------------------------------------------|-------|--------------------|
| E06000047 | County Durham | 4G coverage provided by at least one mobile network provider | 94.86 |                    |
| E06000005 | Darlington    | 4G coverage provided by at least one mobile network provider | 99.99 |                    |
| E06000001 | Hartlepool    | 4G coverage provided by at least one mobile network provider | 99.97 |                    |

With the following [qube-config.json](../../configuration/qube-config.md) column mapping configuration:

```json
{
    "$schema": "https://purl.org/csv-cubed/qube-config/v1",
    "title": "title",
    "columns": {
        "AREACD": {
            "label": "Area Code",
            "type": "dimension"
        },
        "AREANM": {
            "label": "Area Name",
            "type": "dimension"
        },
        "Variable Name": {
            "type": "measures"
        },
        "Value": {
            "type": "observations",
            "data_type": "decimal",
            "unit": {
                "label": "number",
                "from_existing": "http://qudt.org/vocab/unit/NUM"
            }
        },
        "Observation Status": {
            "type": "attribute",
            "from_existing": "http://purl.org/linked-data/sdmx/2009/attribute#obsStatus",
            "label": "Observation Status"
        }
    }
}
```

## How to fix

Either provide values in the `Observation Status` column, or specify an appropriate `cell_uri_template`:

```json
{
    "Observation Status": {
        "type": "attribute",
        "from_existing": "http://purl.org/linked-data/sdmx/2009/attribute#obsStatus",
        "label": "Observation Status",
        "cell_uri_template": ""
    }
}
```
