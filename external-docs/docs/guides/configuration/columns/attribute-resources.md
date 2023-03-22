# Resource attributes

This page discusses how a resource attribute column can be defined.

See the [Attributes page](./attributes.md) for general information about attribute columns, including when to use one, and a discussion of the difference between resource attributes and [literal](./attribute-literals.md) attributes.

> For a detailed look at a resource attribute column's configuration options, see the [Reference table](#reference) at
the bottom of this page.

## Basic configuration
<!-- todo: This should be inside each sub-section (resource/literals) -->

To configure a column as a resource attribute

| Year | Location | Value |                  Measure |                   Unit |      **Status** | 95% CI (lower bound) | 95% CI (upper bound) |
|:-----|:---------|------:|-------------------------:|-----------------------:|----------------:|---------------------:|---------------------:|
| 2022 | London   |    35 | Number of Arthur's Bakes |                  Count | **Provisional** |                      |                      |
| 2022 | London   |    25 |                  Revenue | GBP Sterling, Millions | **Provisional** |                      |                      |
| 2022 | London   |  7.85 |   Average customer spend |           GBP Sterling | **Provisional** |                 6.54 |                 8.06 |
| 2021 | Cardiff  |    26 | Number of Arthur's Bakes |                  Count |       **Final** |                      |                      |
| 2021 | Cardiff  |    18 |                  Revenue | GBP Sterling, Millions |       **Final** |                      |                      |
| 2021 | Cardiff  |  6.98 |   Average customer spend |           GBP Sterling |       **Final** |                 6.03 |                 7.52 |

The same attribute can be used to qualify multiple measures, as demonstrated in the table above, where the `Status`
of `Number of Arthur's Bakes`, `Revenue` and `Average customer spend` observed values can be designated as
`Provisional` or `Final`. This can be configured as follows, using the `observation-status` [template](https://purl.org/csv-cubed/qube-config/templates/observation-status.json):

```json
{ ...
   "columns": {
      "Status": {
         "from_template": "observation-status",
         "required": true
      }
   }
}
```

Setting the `required` field as `true` means that each row must contain a value for this attribute - any missing values
will be flagged to the user by csvcubed.

### Existing Resource attributes

<!-- from_existing, cell_uri_template -->

### New Resource attributes

<!-- values -->

## Reference

This table shows a list of the possible fields that can be entered when configuring a resource attribute column.

| **field name**           | **description**                                                                                                                                                                                                                                                                                                                                                                                      | **default value**                                                                |
|--------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| `type`                   | The type of the column; to configure an attribute column use the value `attribute` (Required)                                                                                                                                                                                                                                                                                                        | *dimension*                                                                      |
| `label`                  | The title of the column (Optional)                                                                                                                                                                                                                                                                                                                                                                   | The capital case of the header in the csv file with spaces replacing underscores |
| `description`            | A description of the contents of the column (Optional)                                                                                                                                                                                                                                                                                                                                               | *none*                                                                           |
| `required`               | If this boolean value is true csvcubed will flag to the user if there are blank values in this column (Optional)                                                                                                                                                                                                                                                                                     | false                                                                            |
| `from_template`          | Use a [column template](../templates.md) (Optional)                                                                                                                                                                                                                                                                                                                                                  | *none*                                                                           |
| `from_existing`          | The uri of the resource for reuse/extension (Optional)                                                                                                                                                                                                                                                                                                                                               | *none*                                                                           |
| `definition_uri`         | A uri of a resource to show how the column is created/managed (e.g. a uri of a PDF explaining a list of attribute values) (Optional)                                                                                                                                                                                                                                                                 | *none*                                                                           |
| `describes_observations` | Associates this attribute with the relevant observation values. This is only necessary for [pivoted shape data sets](../../shape-data/pivoted-shape.md) with multiple observation value columns. (Optional)                                                                                                                                                                                          | *none*                                                                           |
| `values`                 | (New Resource Attributes only) If automatically-generated attributes are desired, a boolean value of `true` is used to signify to csvcubed to create attribute resources from values in this column; otherwise this should be a list of attribute value objects defining the attributes used in the column. See [Attribute values configuration](./attribute-values.md) for more details. (Optional) | *none*                                                                           |
| `cell_uri_template`      | (Existing Resource Attributes only) Used to define a template to map the cell values in this column to URIs (Optional)                                                                                                                                                                                                                                                                               | *none*                                                                           |
