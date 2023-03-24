# Literal attributes

This page discusses how a literal attribute column can be defined.

See the [Attributes page](./attributes.md) for general information about attribute columns, including when to use one,
and a discussion of the difference between [resource](./attribute-resources.md) attributes and literal attributes.

> For a detailed look at a literal attribute column's configuration options, see the [Reference table](#reference) at
the bottom of this page.

## Basic configuration

| Year | Location | Value |                  Measure |                   Unit | **95% CI (lower bound)** | **95% CI (upper bound)** |
|:-----|:---------|------:|-------------------------:|-----------------------:|-------------------------:|-------------------------:|
| 2022 | London   |    35 | Number of Arthur's Bakes |                  Count |                          |                          |
| 2022 | London   |    25 |                  Revenue | GBP Sterling, Millions |                          |                          |
| 2022 | London   |  7.85 |   Average customer spend |           GBP Sterling |                 **6.54** |                 **8.06** |
| 2021 | Cardiff  |    26 | Number of Arthur's Bakes |                  Count |                          |                          |
| 2021 | Cardiff  |    18 |                  Revenue | GBP Sterling, Millions |                          |                          |
| 2021 | Cardiff  |  6.98 |   Average customer spend |           GBP Sterling |                 **6.03** |                 **7.52** |

To configure a column as a literal attribute, specify the `type` field as `attribute` and include the `data_type` field in the column configuration details:

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

The `data_type` field indicates that `95% CI (lower bound)` and `95% CI (upper bound)` values should be decimals.
Built-in data types are available in the [CSV-W standard](https://www.w3.org/TR/2015/REC-tabular-metadata-20151217/#h-built-in-datatypes)
for a range of numeric, text, date/time and other values.

## Label, description and definition

```json
{ ...
   "columns": {
      "95% CI (lower bound)": {
         "type": "attribute",
         "data_type": "decimal",
         "label": "95% confidence interval (lower bound)",
         "description": "The lower bound of the 95% confidence interval for the observed value",
         "definition_uri": "https://en.wikipedia.org/wiki/Confidence_interval"
      },
      "95% CI (upper bound)": {
         "type": "attribute",
         "data_type": "decimal",
         "label": "95% confidence interval (upper bound)",
         "description": "The upper bound of the 95% confidence interval for the observed value",
         "definition_uri": "https://en.wikipedia.org/wiki/Confidence_interval"
      }
   }
}
```

The `label` and `description` fields can be used to provide additional information about the attribute. The
`definition_uri` field allows you to specify a link to a resource describing the attribute and its permitted values.

## Reference

This table shows a list of the possible fields that can be entered when configuring a literal attribute column.

| **field name**           | **description**                                                                                                                                                                                             | **default value**                                                                |
|--------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| `type`                   | The type of the column; to configure an attribute column use the value `attribute` (Required)                                                                                                               | *dimension*                                                                      |
| `data_type`              | The [xml data type](https://www.w3.org/TR/xmlschema-2/#built-in-datatypes) of the contents of the column. If this is provided it becomes a Literal Attribute column (Optional)                              | *none*                                                                           |
| `label`                  | The title of the column (Optional)                                                                                                                                                                          | The capital case of the header in the csv file with spaces replacing underscores |
| `description`            | A description of the contents of the column (Optional)                                                                                                                                                      | *none*                                                                           |
| `definition_uri`         | A uri of a resource to show how the column is created/managed (e.g. a uri of a PDF explaining a list of attribute values) (Optional)                                                                        | *none*                                                                           |
| `required`               | If this boolean value is true csvcubed will flag to the user if there are blank values in this column (Optional)                                                                                            | false                                                                            |
| `from_existing`          | The uri of the resource for reuse/extension (Optional)                                                                                                                                                      | *none*                                                                           |
| `describes_observations` | Associates this attribute with the relevant observation values. This is only necessary for [pivoted shape data sets](../../shape-data/pivoted-shape.md) with multiple observation value columns. (Optional) | *none*                                                                           |
