# Literal attributes

This page discusses how a Literal attribute column can be defined.

See the [Attributes page](./attributes.md) for general information about attribute columns, including when to use one,
and a discussion of the difference between [Resource](./attribute-resources.md) attributes and Literal attributes.

> For a detailed look at a Literal attribute column's configuration options, see the [Reference table](#reference) at
the bottom of this page.

## Basic configuration

| Year | Location | Value |                Measure |         Unit | **95% CI (lower bound)** | **95% CI (upper bound)** |
|:-----|:---------|------:|-----------------------:|-------------:|-------------------------:|-------------------------:|
| 2022 | London   |  7.85 | Average customer spend | GBP Sterling |                 **6.54** |                 **8.06** |
| 2021 | Cardiff  |  6.98 | Average customer spend | GBP Sterling |                 **6.03** |                 **7.52** |

To configure a column as a Literal attribute, specify the `type` field as `attribute` and include the `data_type` field
in the column configuration details:

```json
{
   "title": "The title of the cube",
   "description": "A description of the contents of the cube",
   "summary": "A summary of the data set",
   "columns": {
      "95% CI (lower bound)": {
         "type": "attribute",
         "data_type": "decimal"
      },
      "95% CI (upper bound)": {
         "type": "attribute",
         "data_type": "decimal"
      }
   }
}
```

This minimal definition results in:

* the `label` field defaulting to the column titles (`95% CI (lower bound)` and `95% CI (upper bound)` in this example);
* the `required` field defaulting to `false` - this means that csvcubed will accept a CSV file with empty cells in the
`95% CI (lower bound)` and `95% CI (upper bound)` columns;
* the `data_type` being set as `decimal`. This indicates that the values of `95% CI (lower bound)` and
`95% CI (upper bound)` should be decimals. Built-in data types are available in the
[CSV-W standard](https://www.w3.org/TR/2015/REC-tabular-metadata-20151217/#h-built-in-datatypes) for a range of
numeric, text, date/time and other values.

If all cells in the `95% CI (lower bound)` and `95% CI (upper bound)` columns should be populated, set the `required` field to `true`. Doing so will prompt csvcubed to flag to the user if there are any blank cells in these columns:

```json
{
   "title": "The title of the cube",
   "description": "A description of the contents of the cube",
   "summary": "A summary of the data set",
   "columns": {
      "95% CI (lower bound)": {
         "type": "attribute",
         "data_type": "decimal",
         "required": true
      },
      "95% CI (upper bound)": {
         "type": "attribute",
         "data_type": "decimal",
         "required": true
      }
   }
}
```

## Label, description and definition

Additional details can be associated with the attributes in your data set through the `label`, `description` and
`definition_uri` fields.

As mentioned above, the `label` field will default to the column title unless explicitly configured in the
`qube-config.json` file. In the example below, the `95% CI (lower bound)` label is amended to `95% confidence interval (lower bound)`:

```json
{ ...
   "columns": {
      "95% CI (lower bound)": {
         "type": "attribute",
         "data_type": "decimal",
         "label": "95% confidence interval (lower bound)"
      }
   }
}
```

The `description` field can be used to provide a longer description of your attribute. If you want to provide
information about your methodology, the `description` field is the preferred place for this. It also supports the
markdown format.

```json
{ ...
   "columns": {
      "95% CI (lower bound)": {
         "type": "attribute",
         "data_type": "decimal",
         "description": "The lower bound of the 95% confidence interval for the observed value",
      }
   }
}
```

The `definition_uri` fields allows you to refer to external resources that further define an attribute's values:

```json
{ ...
   "columns": {
      "95% CI (lower bound)": {
         "type": "attribute",
         "data_type": "decimal",
         "definition_uri": "https://en.wikipedia.org/wiki/Confidence_interval"
      }
   }
}
```

## Inheritance

To reuse or extend an existing attribute, the `from_existing` field can be configured to link to a URI where the
attribute to be reused or extended is defined.

To reuse a parent attribute without making any changes to it, set the `from_existing` field to the URI defining the
attribute to be reused. For example, suppose a new attribute column was added to the table above to record a comment against the `Average customer spend` value:

| Year | Location | Value |                Measure |         Unit | 95% CI (lower bound) | 95% CI (upper bound) |                                                Comment |
|:-----|:---------|------:|-----------------------:|-------------:|---------------------:|---------------------:|-------------------------------------------------------:|
| 2022 | London   |  7.85 | Average customer spend | GBP Sterling |                 6.54 |                 8.06 | **Store closed for renovations 01/05/2022-14/05/2022** |
| 2021 | Cardiff  |  6.98 | Average customer spend | GBP Sterling |                 6.03 |                 7.52 |                                                        |

```json
{ ...
   "columns": {
      "Comment": {
         "type": "attribute",
         "data_type": "string",
         "from_existing": "http://purl.org/linked-data/sdmx/2009/attribute#comment"
      }
   }
}
```

To extend a parent attribute and create a new attribute from it, set the `from_existing` field to the URI defining the
attribute to be reused, and set the `label` field to indicate that this is a new child attribute of `http://purl.org/linked-data/sdmx/2009/attribute#comment`:

```json
{ ...
   "columns": {
      "Comment": {
         "type": "attribute",
         "data_type": "string",
         "from_existing": "http://purl.org/linked-data/sdmx/2009/attribute#comment",
         "label": "Additional comments"
      }
   }
}
```

## Reference

This table shows a list of the possible fields that can be entered when configuring a Literal attribute column.

| **field name**           | **description**                                                                                                                                                                                                                                                                                                            | **default value**                                                                |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| `type`                   | The type of the column; to configure an attribute column use the value `attribute` (Required)                                                                                                                                                                                                                              | *dimension*                                                                      |
| `data_type`              | The [xml data type](https://www.w3.org/TR/xmlschema-2/#built-in-datatypes) of the contents of the column. If this is provided it becomes a Literal attribute column (Optional)                                                                                                                                             | *none*                                                                           |
| `label`                  | The title of the column (Optional)                                                                                                                                                                                                                                                                                         | The capital case of the header in the csv file with spaces replacing underscores |
| `description`            | A description of the contents of the column (Optional)                                                                                                                                                                                                                                                                     | *none*                                                                           |
| `definition_uri`         | A uri of a resource to show how the column is created/managed (e.g. a uri of a PDF explaining a list of attribute values) (Optional)                                                                                                                                                                                       | *none*                                                                           |
| `required`               | If this boolean value is true csvcubed will flag to the user if there are blank values in this column (Optional)                                                                                                                                                                                                           | false                                                                            |
| `from_existing`          | The uri of the resource for reuse/extension (Optional)                                                                                                                                                                                                                                                                     | *none*                                                                           |
| `describes_observations` | Associates this attribute with the relevant observation values. This is only necessary for [pivoted shape data sets](../../shape-data/pivoted-shape.md) with multiple observation value columns. See the [Attributes](./attributes.md#describing-observations) page for details of how to configure this field. (Optional) | *none*                                                                           |
