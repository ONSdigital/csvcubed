# Attribute columns

This page discusses what an attribute column is, where one should be used, and how one can be defined.

> For a detailed look at an attribute column's configuration options, see the [Reference table](#reference) at the
bottom of this page.

## What is an attribute column?

Attribute columns describe or provide additional context to the data set's observed values. They **do not** identify
a particular sub-set of the data set's population. If the column you are configuring does identify such a sub-set of
the population, then it is probably a [dimension](./dimensions.md).

## When to use one

Unlike [dimensions](./dimensions.md), [observations](./observations.md), [measures](./measures.md) and
[units](./units.md), attributes are optional components of a data cube. Their primary usage is to qualify
observed values by providing additional context about individual data points. Two common examples of attributes are
**observation status** and **confidence intervals**.

| Year | Location | Value |                  Measure |                   Unit |      Status | 95% CI (lower bound) | 95% CI (upper bound) |
|:-----|:---------|------:|-------------------------:|-----------------------:|------------:|---------------------:|---------------------:|
| 2022 | London   |    35 | Number of Arthur's Bakes |                  Count | Provisional |                      |                      |
| 2022 | London   |    25 |                  Revenue | GBP Sterling, Millions | Provisional |                      |                      |
| 2022 | London   |  7.85 |   Average customer spend |           GBP Sterling | Provisional |                 6.54 |                 8.06 |

In the table above, there are three attribute columns: `Status`, `95% CI (lower bound)` and `95% CI (upper bound)`.

The `Status` attribute column indicates whether the observed value is Provisional or Final, and applies to all of the
observed values in this data set.

The `95% CI (lower bound)` and `95% CI (upper bound)` attribute columns contain the lower and upper bounds of the 95%
confidence interval for the `Average customer spend` observed values.

## Resources vs Literals

The configuration of attribute columns in your data set will depend primarily on whether you choose to represent the
attribute as a [Resource](../../../glossary/index.md#resource) or a [Literal](../../../glossary/index.md#literal).

**Resource attributes** are suitable for categorical values which **can be reused as linked data**. Given that the goal
of the csvcubed project is to simplify the process of creating [5-star linked data](https://5stardata.info/en/) from CSV
files, using Resource attributes in your data cube where appropriate is encouraged.

Observation status is a good example of a Resource attribute, since there are a number of categories (Provisional,
Final etc) which describe the observed value.

See the [Resource attributes](./attribute-resources.md) page for more information on how to configure these columns.

**Literal attributes** are simple values and **are not linked data**. You should only use Literal attributes when
your attribute values are not categorical.

Confidence intervals are a good example of when the use of Literal attributes is appropriate, as the attribute values
are numeric (i.e. not categorical), and each value is unique to the observed value it qualifies.

See the [Literal attributes](./attribute-literals.md) page for more information on how to configure these columns.

## Basic configuration

As mentioned above, the configuration of attribute columns will depend on whether you choose to represent them as Resources or Literals. Please refer to the [Resource attributes](./attribute-resources.md) and [Literal attributes](./attribute-literals.md) pages for further information.

## Describing observations

In a [pivoted shape data set](../../shape-data/pivoted-shape.md) with multiple observation columns, attributes must be
explicitly associated with the observed values they qualify. In the example below, there are two attribute columns,
`Number of Stores Status` and `Revenue Status`, which qualify the `Number of Arthur's Bakes` and `Revenue` columns
respectively.

| Year | Location | Number of Arthur's Bakes | Number of Stores Status | Revenue | Revenue Status |
|:-----|:---------|-------------------------:|:------------------------|--------:|:---------------|
| 2022 | London   |                       35 | Provisional             |      25 | Provisional    |
| 2021 | Cardiff  |                       26 | Final                   |      18 | Final          |

This can be configured as follows:

```json
{ ...
   "columns": {
      "Number of Stores Status": {
         "type": "attribute",
         "describes_observations": "Number of Arthur's Bakes"
      },
      "Revenue Status": {
         "type": "attribute",
         "describes_observations": "Revenue"
      }
   }
}
```

The `describes_observations` field has been used to associate each attribute with the observed values it qualifies. The formatting of the fields' values (in this case, `Number of Arthur's Bakes` and `Revenue`) **must** match the relevant column titles exactly in order for csvcubed to recognise the association.

## Reference

This table shows a list of the possible fields that can be entered when configuring an attribute column.

| **field name**           | **description**                                                                                                                                                                                                                                                                                                                                                                                      | **default value**                                                                |
|--------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| `type`                   | The type of the column; to configure an attribute column use the value `attribute` (Required)                                                                                                                                                                                                                                                                                                        | *dimension*                                                                      |
| `label`                  | The title of the column (Optional)                                                                                                                                                                                                                                                                                                                                                                   | The capital case of the header in the CSV file with spaces replacing underscores |
| `description`            | A description of the contents of the column (Optional)                                                                                                                                                                                                                                                                                                                                               | *none*                                                                           |
| `definition_uri`         | A URI of a resource to show how the column is created/managed (e.g. a URI of a PDF explaining a list of attribute values) (Optional)                                                                                                                                                                                                                                                                 | *none*                                                                           |
| `required`               | If this boolean value is true csvcubed will flag to the user if there are blank values in this column (Optional)                                                                                                                                                                                                                                                                                     | false                                                                            |
| `data_type`              | (Literal attributes only) The [XML data type](https://www.w3.org/TR/xmlschema-2/#built-in-datatypes) of the contents of the column. If this is provided it becomes a Literal attribute column (Optional)                                                                                                                                                                                             | *none*                                                                           |
| `values`                 | (New Resource Attributes only) If automatically-generated attributes are desired, a boolean value of `true` is used to signify to csvcubed to create Resource attributes from values in this column; otherwise this should be a list of attribute value objects defining the attributes used in the column. See [Attribute values configuration](./attribute-values.md) for more details. (Optional) | *none*                                                                           |
| `from_template`          | (New/Existing Resource Attributes only) Use a [column template](../templates.md) (Optional)                                                                                                                                                                                                                                                                                                          | *none*                                                                           |
| `from_existing`          | The URI of the resource for reuse/extension (Optional)                                                                                                                                                                                                                                                                                                                                               | *none*                                                                           |
| `describes_observations` | Associates this attribute with the relevant observation values. This is only necessary for [pivoted shape data sets](../../shape-data/pivoted-shape.md) with multiple observation value columns. (Optional)                                                                                                                                                                                          | *none*                                                                           |
| `cell_uri_template`      | (Existing Resource Attributes only) Used to define a template to map the cell values in this column to URIs (Optional)                                                                                                                                                                                                                                                                               | *none*                                                                           |
