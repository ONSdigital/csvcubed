# Attribute columns

This page discusses what an attribute column is, where one should be used, and how one can be defined.

> For a detailed look at an attribute column's configuration options, see the [Reference table](#reference) at the
bottom of this page.

## What is an attribute column?

Attribute columns describe or provide additional context to the data set's observed values. They **do not** identify
a particular sub-set of the data set's population. If the column you are configuring does identify such a sub-set of
the population, then it is probably a [dimension](./dimensions.md).

<!-- todo: mention:

* An attribute describes/provides context to an observed value
* Does *NOT* identify any sub-group of the statistical population (i.e. not a dimension) -->

## When to use one

Unlike [dimensions](./dimensions.md), [observations](./observations.md), [measures](./measures.md) and
[units](./units.md), attributes are optional components in a data cube. Their primary usage is to qualify
observed values by providing additional context about individual data points. Two common examples of attributes are
**observation status** and **confidence intervals**.

| Year | Location | Value |                  Measure |                   Unit |      Status | 95% CI (lower bound) | 95% CI (upper bound) |
|:-----|:---------|------:|-------------------------:|-----------------------:|------------:|---------------------:|---------------------:|
| 2022 | London   |    35 | Number of Arthur's Bakes |                  Count | Provisional |                      |                      |
| 2022 | London   |    25 |                  Revenue | GBP Sterling, Millions | Provisional |                      |                      |
| 2022 | London   |  7.85 |   Average customer spend |           GBP Sterling | Provisional |                 6.54 |                 8.06 |
| 2021 | Cardiff  |    26 | Number of Arthur's Bakes |                  Count |       Final |                      |                      |
| 2021 | Cardiff  |    18 |                  Revenue | GBP Sterling, Millions |       Final |                      |                      |
| 2021 | Cardiff  |  6.98 |   Average customer spend |           GBP Sterling |       Final |                 6.03 |                 7.52 |

In the table above, there are three attribute columns: `Status`, `95% CI (lower bound)` and `95% CI (upper bound)`.

The `Status` attribute column indicates whether the observed value is Provisional or Final, and applies to all of the
observed values in this example data set.

The `95% CI (lower bound)` and `95% CI (upper bound)` attribute columns contain the lower and upper bounds of the 95%
confidence interval for the `Average customer spend` observed values.

<!-- * Provide simple examples, e.g.
   * Observation status (provision vs final)
   * Errors
   * Confidence intervals -->

## Literals vs resources

The configuration of attribute columns in your data set will depend primarily on whether you choose to represent the
attribute as a [resource](../../../glossary/index.md#uri) or a [literal value](../../../glossary/index.md#literal).

**Resource attributes** are categorical values which **can be reused as linked data**. Given that the goal of the
csvcubed project is to simplify the process of creating [5-star linked data](https://5stardata.info/en/) from CSV
files, using resource attributes in your data cube where appropriate is encouraged.

Observation status is a prime example of a resource attribute since there are a number of categories (Provisional,
Final etc) which describe the observed value.

**Literal attributes** are simple values and **are not linked data**. You should only use literal attributes when
your attribute values are not categorical.

Confidence intervals are a good example of when the use of literal attributes is appropriate, as the attribute values
are numerical (i.e. not categorical), and each value is unique to the observed value it qualifies.

<!-- todo: This is where we should link to the literal and resources definitions, but we should bring the important bits into this section.

* Resources are categorical values which *can be reused as linked data*.
  * So you should really be trying to represent your values as resources in the first instance.
  * Observation status is the prime example of a resource attribute since there are a number of categories (e.g. Provisional/Final) which describe the observed value.
* Literals are simple values and are *not linked data*. You should only use literals where your data is not categorical.
  * Errors + Confidencens intervals are examples of where literal attributes are appropriate - since they range over a continuous scale and are unique to each observed value. -->

## Resource attributes

### Basic configuration
<!-- todo: This should be inside each sub-section (resource/literals) -->

The same attribute can be used to qualify multiple measures, as demonstrated in the table below, where the `Status`
of `Number of Arthur's Bakes`, `Revenue` and `Average customer spend` observed values can be designated as
`Provisional` or `Final`.

| Year | Location | Value |                  Measure |                   Unit |      **Status** | 95% CI (lower bound) | 95% CI (upper bound) |
|:-----|:---------|------:|-------------------------:|-----------------------:|----------------:|---------------------:|---------------------:|
| 2022 | London   |    35 | Number of Arthur's Bakes |                  Count | **Provisional** |                      |                      |
| 2022 | London   |    25 |                  Revenue | GBP Sterling, Millions | **Provisional** |                      |                      |
| 2022 | London   |  7.85 |   Average customer spend |           GBP Sterling | **Provisional** |                 6.54 |                 8.06 |
| 2021 | Cardiff  |    26 | Number of Arthur's Bakes |                  Count |       **Final** |                      |                      |
| 2021 | Cardiff  |    18 |                  Revenue | GBP Sterling, Millions |       **Final** |                      |                      |
| 2021 | Cardiff  |  6.98 |   Average customer spend |           GBP Sterling |       **Final** |                 6.03 |                 7.52 |

This can be configured as follows, using the `observation-status` [template](https://purl.org/csv-cubed/qube-config/templates/observation-status.json):

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

Setting the `required` field as `true` means that each row must contain a value for this attribute - any missing values will be flagged to the user by csvcubed.

### Existing Resource attributes

<!-- from_existing, cell_uri_template -->

### New Resource attributes

<!-- values -->

## Literal attributes

### Basic configuration

| Year | Location | Value |                  Measure |                   Unit |      Status | **95% CI (lower bound)** | **95% CI (upper bound)** |
|:-----|:---------|------:|-------------------------:|-----------------------:|------------:|-------------------------:|-------------------------:|
| 2022 | London   |    35 | Number of Arthur's Bakes |                  Count | Provisional |                          |                          |
| 2022 | London   |    25 |                  Revenue | GBP Sterling, Millions | Provisional |                          |                          |
| 2022 | London   |  7.85 |   Average customer spend |           GBP Sterling | Provisional |                 **6.54** |                 **8.06** |
| 2021 | Cardiff  |    26 | Number of Arthur's Bakes |                  Count |       Final |                          |                          |
| 2021 | Cardiff  |    18 |                  Revenue | GBP Sterling, Millions |       Final |                          |                          |
| 2021 | Cardiff  |  6.98 |   Average customer spend |           GBP Sterling |       Final |                 **6.03** |                 **7.52** |

```json
{ ...
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

The `data_type` field indicates that `95% CI (lower bound)` and `95% CI (upper bound)` values should be decimals. Built-in data types are available in the [CSV-W standard](https://www.w3.org/TR/2015/REC-tabular-metadata-20151217/#h-built-in-datatypes) for a range of numeric, text, date/time and other values. The `data_type` field should only be used for the configuration of literal attributes.

### Label, description and definition

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

The `label` and `description` fields can be used to provide additional information about the attribute. The `definition_uri` field allows you to specify a link to a resource describing the attribute and its permitted values.

## Pivoted multi-measure data sets
<!-- TODO: Move to parent doc -->
| Year | Location | Number of Arthur's Bakes | Number of Stores Status | Revenue | Revenue Units  | Revenue Status |
|:-----|:---------|-------------------------:|:------------------------|--------:|:---------------|:---------------|
| 2022 | London   |                       35 | Provisional             |      25 | GBP (Sterling) | Provisional    |
| 2021 | Cardiff  |                       26 | Final                   |      18 | GBP (Sterling) | Final          |

In this example, there are two attribute columns - `Number of Stores Status` and `Revenue Status`. These columns need to be explicitly associated with the relevant observation values columns, which can be achieved as follows:

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

The `describes_observations` field has been used to associate each attribute with the observed values it qualifies. The formatting of the fields' values (in this case, `Number of Arthur's Bakes` and `Revenue`) must match the relevant column titles exactly in order for csvcubed to recognise the association.

## Reference

This table shows a list of the possible fields that can be entered when configuring an attribute column.

| **field name**           | **description**                                                                                                                                                                                                                                                                                                                                                                                      | **default value**                                                                |
|--------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| `type`                   | The type of the column; to configure an attribute column use the value `attribute` (Required)                                                                                                                                                                                                                                                                                                        | *dimension*                                                                      |
| `label`                  | The title of the column (Optional)                                                                                                                                                                                                                                                                                                                                                                   | The capital case of the header in the csv file with spaces replacing underscores |
| `description`            | A description of the contents of the column (Optional)                                                                                                                                                                                                                                                                                                                                               | *none*                                                                           |
| `from_template`          | (New/Existing Resource Attributes only) Use a [column template](../templates.md) (Optional)                                                                                                                                                                                                                                                                                                          | *none*                                                                           |
| `from_existing`          | The uri of the resource for reuse/extension (Optional)                                                                                                                                                                                                                                                                                                                                               | *none*                                                                           |
| `data_type`              | (Literal Attributes only) The [xml data type](https://www.w3.org/TR/xmlschema-2/#built-in-datatypes) of the contents of the column. If this is provided it becomes a Literal Attribute column (Optional)                                                                                                                                                                                             | *none*                                                                           |
| `values`                 | (New Resource Attributes only) If automatically-generated attributes are desired, a boolean value of `true` is used to signify to csvcubed to create attribute resources from values in this column; otherwise this should be a list of attribute value objects defining the attributes used in the column. See [Attribute values configuration](./attribute-values.md) for more details. (Optional) | *none*                                                                           |
| `describes_observations` | Associates this attribute with the relevant observation values. This is only necessary for [pivoted shape data sets](../../shape-data/pivoted-shape.md) with multiple observation value columns. (Optional)                                                                                                                                                                                          | *none*                                                                           |
| `required`               | If this boolean value is true csvcubed will flag to the user if there are blank values in this column (Optional)                                                                                                                                                                                                                                                                                     | false                                                                            |
| `definition_uri`         | A uri of a resource to show how the column is created/managed (e.g. a uri of a PDF explaining a list of attribute values) (Optional)                                                                                                                                                                                                                                                                 | *none*                                                                           |
| `cell_uri_template`      | (Existing Resource Attributes only) Used to define a template to map the cell values in this column to URIs (Optional)                                                                                                                                                                                                                                                                               | *none*                                                                           |
