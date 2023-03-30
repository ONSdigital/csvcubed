# Attribute values configuration

This page discusses what attribute values are, where they should be used, and how they can be defined.

See the [Attributes page](./index.md) for general information about attribute columns, including when to use one,
and a discussion of the difference between [Resource](./attribute-resources.md) attributes and
[Literal](./attribute-literals.md) attributes.

> For a detailed look at attribute values configuration options, see the [Reference table](#reference) at the
bottom of this page.

## What are attribute values?

Attribute values are the cell values in the attribute column of your CSV file. csvcubed will automatically generate
RDF resources from the cell values if you specify the `values` field as `true`. However, it is also possible to
explicitly configure attribute values, as described below.

## When to use them

You should only configure the `values` field when using [Resource](./attribute-resources.md) attributes. Please note,
the `label` field format should match the format of the attribute cell value exactly.

## Basic configuration

!!! Important
    The format of the `label` field should match the cell values in your CSV exactly.

| **Year** | **Region** | **Value** |   **Status** |
|:---------|:-----------|:---------:|-------------:|
| 2020     | England    |   10.6    | confidential |
| 2021     | Scotland   |   13.8    |    estimated |
| 2022     | Wales      |   9.43    |     forecast |

To configure the values in your attribute column, specify the `type` of the column as `attribute`, and specify `values`
as a list of objects defining the attributes used in the column:

```json
{
    "$schema": "https://purl.org/csv-cubed/qube-config/v1",
    "title": "The title of the cube",
    "description": "A description of the contents of the cube",
    "columns": {
        "Status": {
            "type": "attribute",
            "values": [
                {
                    "label": "confidential"
                },
                {
                    "label": "estimated"
                },
                {
                    "label": "forecast"
                }
            ]
        }
    }
}
```

This minimal definition results in:

* the `label` being set as the specified value - remember, this must match the formatting of the cell values exactly.

## Description and definition

Additional details can be associated with the attribute values in your data set through the `description` and
`definition_uri` fields.

The `description` field can be used to provide a longer description of your attribute value. If you want to provide
information about your methodology, the `description` field is the preferred place for this.

```json
{ ...
    "columns": {
        "Status": {
            "type": "attribute",
            "values": [
                {
                    "label": "confidential",
                    "description": "This observation is suppressed as its disclosure would give away confidential information. For example, if you would be able to identify details about a single respondent from the data."
                },
                {
                    "label": "estimated",
                    "description": "This observation is an estimate. Where an entire data set is estimated this should be stated in the title or accompanying information rather than providing this observation status on every observation. Not to be confused with f = forecast."
                },
                {
                    "label": "forecast",
                    "description": "This observation is a calculated future value instead of an observed value. Not to be confused with e = estimated."
                }
            ]
        }
    }
}
```

The `definition_uri` fields allows you to refer to external resources that further define the attribute values:

``` json
{ ...
    "columns": {
        "Status": {
            "type": "attribute",
            "values": [
                {
                    "label": "confidential",
                    "definition_uri": "https://github.com/GSS-Cogs/reusable-rdf-resources/blob/main/rdf-definitions/attributes/analyst-function-obs-marker.csv"
                },
                {
                    "label": "estimated",
                    "definition_uri": "https://github.com/GSS-Cogs/reusable-rdf-resources/blob/main/rdf-definitions/attributes/analyst-function-obs-marker.csv"
                },
                {
                    "label": "forecast",
                    "definition_uri": "https://github.com/GSS-Cogs/reusable-rdf-resources/blob/main/rdf-definitions/attributes/analyst-function-obs-marker.csv"
                }
            ]
        }
    }
}
```

## Inheritance

To reuse or extend an existing attribute value, the `from_existing` field can be configured to link to a URI where the
value to be reused or extended is defined.

To reuse a parent attribute value without making any changes to it, set the `from_existing` field to the URI defining
the attribute to be reused.

```json
{ ...
    "columns": {
        "Status": {
            "type": "attribute",
            "values": [
                {
                    "label": "confidential",
                    "from_existing": "https://purl.org/csv-cubed/resources/attributes/af-obs-marker#c"
                },
                {
                    "label": "estimated",
                    "from_existing": "https://purl.org/csv-cubed/resources/attributes/af-obs-marker#e"
                },
                {
                    "label": "forecast",
                    "from_existing": "https://purl.org/csv-cubed/resources/attributes/af-obs-marker#f"
                }
            ]
        }
    }
}
```

To extend a parent attribute value and create a new value from it, set the `from_existing` field to the URI defining the
value to be reused, and set the `label` field to indicate that this is a new child attribute of the parent, ensuring
that the formatting of the `label` exactly matches the values in the attribute column:

```json
{ ...
    "columns": {
        "Status": {
            "type": "attribute",
            "values": [
                {
                    "label": "Confidential value",
                    "from_existing": "https://purl.org/csv-cubed/resources/attributes/af-obs-marker#c"
                },
                {
                    "label": "Estimated value",
                    "from_existing": "https://purl.org/csv-cubed/resources/attributes/af-obs-marker#e"
                },
                {
                    "label": "Forecast value",
                    "from_existing": "https://purl.org/csv-cubed/resources/attributes/af-obs-marker#f"
                }
            ]
        }
    }
}
```

## Reference

| **field name**   | **description**                                                             | **default value** |
|------------------|-----------------------------------------------------------------------------|-------------------|
| `label`          | The title of the attribute (Required)                                       | *none*            |
| `description`    | A description of the contents of the attribute (Optional)                   | *none*            |
| `from_existing`  | The URI of the resource for reuse/extension (Optional)                      | *none*            |
| `definition_uri` | A URI of a resource to show how the attribute is created/managed (Optional) | *none*            |
