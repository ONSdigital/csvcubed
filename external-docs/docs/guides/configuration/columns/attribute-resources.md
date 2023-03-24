# Resource attributes

This page discusses how a resource attribute column can be defined.

See the [Attributes page](./attributes.md) for general information about attribute columns, including when to use one, and a discussion of the difference between resource attributes and [literal](./attribute-literals.md) attributes.

> For a detailed look at a resource attribute column's configuration options, see the [Reference table](#reference) at
the bottom of this page.

## New vs Existing Resource attributes
<!-- TODO: Expand this section -->

The configuration options you define in a `qube-config.json` file will determine whether csvcubed treats an attribute
column as a New or an Existing resource.

## New Resource attributes

### Basic configuration
<!-- todo: This should be inside each sub-section (resource/literals) -->

| Year | Location | Value |                  Measure |                   Unit |      **Status** |
|:-----|:---------|------:|-------------------------:|-----------------------:|----------------:|
| 2022 | London   |    35 | Number of Arthur's Bakes |                  Count | **Provisional** |
| 2022 | London   |    25 |                  Revenue | GBP Sterling, Millions | **Provisional** |
| 2022 | London   |  7.85 |   Average customer spend |           GBP Sterling | **Provisional** |
| 2021 | Cardiff  |    26 | Number of Arthur's Bakes |                  Count |       **Final** |
| 2021 | Cardiff  |    18 |                  Revenue | GBP Sterling, Millions |       **Final** |
| 2021 | Cardiff  |  6.98 |   Average customer spend |           GBP Sterling |       **Final** |

To configure a column as a resource attribute, specify the `type` field as `attribute`:

```json
{
   "title": "The title of the cube",
   "description": "A description of the contents of the cube",
   "summary": "A summary of the data set",
   "columns": {
      "Status": {
         "type": "attribute"
      }
   }
}
```

This minimal definition results in:

* the `label` field defaulting to the column title (`Status` in this example);
* the `required` field defaulting to `false` - this means that csvcubed will accept a CSV file with empty cells in the
`Status` column;
* [attribute values](./attribute-values.md) automatically being generated from the unique cell values in the `Status` column (`Provisional` and `Final` in this example).

If all cells in the `Status` column should be populated, set the `required` field to `true`. Doing so will prompt csvcubed to flag to the user if there are any blank cells in the `Status` column:

```json
{
   "title": "The title of the cube",
   "description": "A description of the contents of the cube",
   "summary": "A summary of the data set",
   "columns": {
      "Status": {
         "type": "attribute",
         "required": true
      }
   }
}
```

### Label, description and definition

Additional details can be associated with the attributes in your data set through the `label`, `description` and
`definition_uri` fields.

As mentioned above, the `label` field will default to the column title unless explicitly configured in the
`qube-config.json` file. In the example below, the `Status` label is amended to `Observation status`:

```json
{ ...
   "columns": {
      "Status": {
         "type": "attribute",
         "label": "Observation status"
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
      "Status": {
         "type": "attribute",
         "description": "The status of the observed value (Provisional or Final)"
      }
   }
}
```

The `definition_uri` fields allows you to refer to external resources that further define an attribute's values:

```json
{ ...
   "columns": {
      "Status": {
         "type": "attribute",
         "definition_uri": "https://sdmx.org/wp-content/uploads/01_sdmx_cog_annex_1_cdc_2009.pdf"
      }
   }
}
```

### Attribute values

Rather than allowing csvcubed to automatically generate attribute values from the unique cell values in the `Status` column, the `values` field can be configured to specify a list of permitted cell values:

```json
{ ...
   "columns": {
      "Status": {
         "type": "attribute",
         "values": [
            "Provisional",
            "Final"
         ]
      }
   }
}
```

See [Attribute values configuration](./attribute-values.md) for more information on the configuration options available for the `values` field.

## Existing Resource attributes

### Basic configuration

### Inheritance

To reuse or extend an existing attribute, the `from_existing` field can be configured to link to a URI where the
attribute to be reused or extended is defined.

To reuse a parent attribute without making any changes to it, set the `from_existing` field to the URI defining the
attribute to be reused:

```json
{ ...
   "columns": {
      "Status": {
         "type": "attribute",
         "from_existing": "http://purl.org/linked-data/sdmx/2009/attribute#obsStatus"
      }
   }
}
```

To extend a parent attribute and create a new attribute from it, set the `from_existing` field to the URI defining the
attribute to be reused, and set the `label` field to indicate that this is a new child attribute of
`http://purl.org/linked-data/sdmx/2009/attribute#obsStatus`:

```json
{ ...
   "columns": {
      "Status": {
         "type": "attribute",
         "from_existing": "http://purl.org/linked-data/sdmx/2009/attribute#obsStatus",
         "label": "Observation status"
      }
   }
}
```

## Attribute column templates

The `Status` column could also be configured by using a [column template](../templates.md) - doing so means that the
`type`, `from_existing` and `label` fields will be automatically populated based on the
`observation-status` [template](https://purl.org/csv-cubed/qube-config/templates/observation-status.json):

```json
{ ...
   "columns": {
      "Status": {
         "from_template": "observation-status"
      }
   }
}
```

## Advanced configuration

### Cell URI templates
<!-- TODO: Complete this section -->

## Reference

This table shows a list of the possible fields that can be entered when configuring a resource attribute column.

| **field name**           | **description**                                                                                                                                                                                                                                                                                                                                                                                      | **default value**                                                                |
|--------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| `type`                   | The type of the column; to configure an attribute column use the value `attribute` (Required)                                                                                                                                                                                                                                                                                                        | *dimension*                                                                      |
| `label`                  | The title of the column (Optional)                                                                                                                                                                                                                                                                                                                                                                   | The capital case of the header in the csv file with spaces replacing underscores |
| `description`            | A description of the contents of the column (Optional)                                                                                                                                                                                                                                                                                                                                               | *none*                                                                           |
| `definition_uri`         | A uri of a resource to show how the column is created/managed (e.g. a uri of a PDF explaining a list of attribute values) (Optional)                                                                                                                                                                                                                                                                 | *none*                                                                           |
| `required`               | If this boolean value is true csvcubed will flag to the user if there are blank values in this column (Optional)                                                                                                                                                                                                                                                                                     | false                                                                            |
| `values`                 | (New Resource Attributes only) If automatically-generated attributes are desired, a boolean value of `true` is used to signify to csvcubed to create attribute resources from values in this column; otherwise this should be a list of attribute value objects defining the attributes used in the column. See [Attribute values configuration](./attribute-values.md) for more details. (Optional) | *none*                                                                           |
| `from_existing`          | The uri of the resource for reuse/extension (Optional)                                                                                                                                                                                                                                                                                                                                               | *none*                                                                           |
| `from_template`          | Use a [column template](../templates.md) (Optional)                                                                                                                                                                                                                                                                                                                                                  | *none*                                                                           |
| `describes_observations` | Associates this attribute with the relevant observation values. This is only necessary for [pivoted shape data sets](../../shape-data/pivoted-shape.md) with multiple observation value columns. (Optional)                                                                                                                                                                                          | *none*                                                                           |
| `cell_uri_template`      | (Existing Resource Attributes only) Used to define a template to map the cell values in this column to URIs (Optional)                                                                                                                                                                                                                                                                               | *none*                                                                           |
