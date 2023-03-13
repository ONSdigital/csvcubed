# Attribute configuration

For the purposes of these instructions, we will be using the `Number of Arthur's Bakes` data set.

## Standard shape

### Standard single-measure data set

| Year | Location  | Value |      Status |                  Measure |  Unit |
|:-----|:----------|------:|------------:|-------------------------:|------:|
| 2022 | London    |    35 | Provisional | Number of Arthur's Bakes | Count |
| 2021 | Cardiff   |    26 |       Final | Number of Arthur's Bakes | Count |
| 2020 | Edinburgh |    90 |       Final | Number of Arthur's Bakes | Count |
| 2021 | Belfast   |     0 |       Final | Number of Arthur's Bakes | Count |

For the standard single-measure version of the `Number of Arthur's Bakes` data set, there is a single attribute column, `Status`, indicating whether the `Number of Arthur's Bakes` count is a provisional or final value. This could be configured as follows:

```json
{ ...
   "columns": {
      "Status": {
         "type": "attribute",
         "label": "Observation Status",
         "description": "Indicates whether the number of Arthur's Bakes stores is a provisional or final value",
         "required": "true"
      }
   }
}
```

The `type` field indicates to csvcubed that this is an attribute column. The `label` and `description` fields allow additional information to be recorded for the column. If the `label` field is omitted, this value will default to the capital case version of the CSV column header. The `required` field is set to `true`, which means that each row must contain a value in the `Status` column - if any rows are missing these values, this will be flagged to the user by csvcubed.

### Standard multi-measure data set

| Year | Location | Value |      Status |                  Measure |                   Unit | 95% CI (lower bound) | 95% CI (upper bound) |
|:-----|:---------|------:|------------:|-------------------------:|-----------------------:|---------------------:|---------------------:|
| 2022 | London   |    35 | Provisional | Number of Arthur's Bakes |                  Count |                      |                      |
| 2022 | London   |    25 | Provisional |                  Revenue | GBP Sterling, Millions |                      |                      |
| 2022 | London   |  7.85 | Provisional |   Average customer spend |           GBP Sterling |                 6.54 |                 8.06 |
| 2021 | Cardiff  |    26 |       Final | Number of Arthur's Bakes |                  Count |                      |                      |
| 2021 | Cardiff  |    18 |       Final |                  Revenue | GBP Sterling, Millions |                      |                      |
| 2021 | Cardiff  |  6.98 |       Final |   Average customer spend |           GBP Sterling |                 6.03 |                 7.52 |

The same attribute can be used to qualify multiple measures, as is demonstrated in the example above, where the `Number of Arthur's Bakes`, `Revenue` and `Average customer spend` observed values can be designated as provisional or final. This can be configured as follows:

```json
{ ...
   "columns": {
      "Status": {
         "type": "attribute",
         "data_type": "string",
         "definition_uri": "http://example.org/arthurs-bakes-store-status"
      }
   }
}
```

The `data_type` field indicates that `Status` values should be strings. Built-in data types are available in the [CSV-W standard](https://www.w3.org/TR/2015/REC-tabular-metadata-20151217/#h-built-in-datatypes) for a range of numeric, text, date/time and other values. This field should only be used for the creation of attribute literals - to refer to existing attributes or to repurpose existing attributes for the purposes of your data set, see the instructions below.
<!-- TODO: add link to specific guidance for resource-type attributes -->
The `definition_uri` fields allows you to specify a link to a resource describing the attribute and its permitted values.

This data set has two additional attribute components defined for the 95% confidence interval for the `Average customer spend` values.

## Pivoted shape

### Pivoted single-measure data set

| Year | Location  | Number of Arthur's Bakes | Status      |
|:-----|:----------|-------------------------:|:------------|
| 2022 | London    |                       35 | Provisional |
| 2021 | Cardiff   |                       26 | Final       |
| 2020 | Edinburgh |                       90 | Final       |
| 2021 | Belfast   |                        0 | Final       |

### Pivoted multi-measure data set

| Year | Location | Number of Arthur's Bakes | Number of Stores Status | Revenue | Revenue Units  | Revenue Status |
|:-----|:---------|-------------------------:|:------------------------|--------:|:---------------|:---------------|
| 2022 | London   |                       35 | Provisional             |      25 | GBP (Sterling) | Provisional    |
| 2021 | Cardiff  |                       26 | Final                   |      18 | GBP (Sterling) | Final          |



```json
{ ...
   "columns": {

   }
}
```

```json
{ ...
   "columns": {
      "Marker": {
         "from_template": "observation-status"
      }
   }
}
```

## Attribute values configuration

TODO

## Attributes reference

| **field name**           | **description**                                                                                                                                                                                                                                                                                                                                                                                     | **default value**                                                                |
|--------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| `type`                   | The type of the column; to configure an attribute column use the value `attribute` (Required)                                                                                                                                                                                                                                                                                                       | *dimension*                                                                      |
| `from_template`          | (New/Existing Resource Attributes only) Use a [column template](../templates.md)                                                                                                                                                                                                                                                                                                                       | *none*                                                                           |
| `label`                  | The title of the column (Optional)                                                                                                                                                                                                                                                                                                                                                                  | The capital case of the header in the csv file with spaces replacing underscores |
| `description`            | A description of the contents of the column (Optional)                                                                                                                                                                                                                                                                                                                                              | *none*                                                                           |
| `from_existing`          | The uri of the resource for reuse/extension (Optional)                                                                                                                                                                                                                                                                                                                                              | *none*                                                                           |
| `definition_uri`         | A uri of a resource to show how the column is created/managed (e.g. a uri of a PDF explaining a list of attribute values) (Optional)                                                                                                                                                                                                                                                                | *none*                                                                           |
| `describes_observations` | Associates this attribute with the relevant observation values. This is only necessary for [pivoted shape data sets](../../shape-data/pivoted-shape.md) with multiple observation value columns.                                                                                                                                                                                                       | *none*                                                                           |
| `required`               | If this boolean value is true csvcubed will flag to the user if there are blank values in this column                                                                                                                                                                                                                                                                                               | false                                                                            |
| `data_type`              | (Attribute Literals only) The [xml data type](https://www.w3.org/TR/xmlschema-2/#built-in-datatypes) of the contents of the column, if this is provided it becomes a Literal Attribute column (Optional)                                                                                                                                                                                            | *none*                                                                           |
| `values`                 | (New Resource Attributes only) If automatically-generated attributes are desired, a boolean value of `true` is used to signify to csvcubed to create attribute resources from values in this column; otherwise this should be a list of attribute value objects defining the attributes used in the column. See [Attribute values configuration](#attribute-values-configuration) for more details. | *none*                                                                           |
| `cell_uri_template`      | (Existing Resource Attributes only) Used to define a template to map the cell values in this column to URIs                                                                                                                                                                                                                                                                                         | *none*                                                                           |

## Attribute values reference

| **field name**   | **description**                                                             | **default value** |
|------------------|-----------------------------------------------------------------------------|-------------------|
| `label`          | The title of the attribute (Required; Optional if `from_existing` defined)  | *none*            |
| `description`    | A description of the contents of the attribute (Optional)                   | *none*            |
| `from_existing`  | The uri of the resource for reuse/extension (Optional)                      | *none*            |
| `definition_uri` | A uri of a resource to show how the attribute is created/managed (Optional) | *none*            |
