# Observation configuration

Observations are the most important component of a CSV-W data set. Observation columns can have measures and units defined against them to obviate the need for separate unit and measure columns in a single measure data set.

The configuration of observation columns in your data set will primarily depend on the [shape of your data](../../shape-data/index.md). For [standard shape](../../shape-data/standard-shape.md) data sets, where units and measures are contained in their own columns, only the `type` and `data_type` fields can be populated. For [pivoted shape](../../shape-data/pivoted-shape.md) data sets, the `unit` and `measure` fields can also be configured.

For the purposes of these instructions, we will be using the `Number of Arthur's Bakes` data set.

## Standard shape

### Standard single-measure data set

| Year | Location  | Value |                  Measure |  Unit |
|:-----|:----------|------:|-------------------------:|------:|
| 2022 | London    |    35 | Number of Arthur's Bakes | Count |
| 2021 | Cardiff   |    26 | Number of Arthur's Bakes | Count |
| 2020 | Edinburgh |    90 | Number of Arthur's Bakes | Count |
| 2021 | Belfast   |     0 | Number of Arthur's Bakes | Count |

This data set is in the standard shape, with `Measure` and `Unit` columns explicitly defined for `Number of Arthur's Bakes` and `Count` respectively; therefore the `Value` column can be configured as follows:

```json
{ ...
   "columns": {
      "Value": {
         "type": "observations",
         "data_type": "integer"
      }
   }
}
```

### Standard multi-measure data set

| Year | Location | Value |                  Measure |                   Unit |
|:-----|:---------|------:|-------------------------:|-----------------------:|
| 2022 | London   |    35 | Number of Arthur's Bakes |                  Count |
| 2022 | London   |    25 |                  Revenue | GBP Sterling, Millions |
| 2021 | Cardiff  |    26 | Number of Arthur's Bakes |                  Count |
| 2021 | Cardiff  |    18 |                  Revenue | GBP Sterling, Millions |

A `Revenue` measure has now been included in the data set, with a corresponding unit of `GBP Sterling, Millions`; however, this doesn't necessitate any changes to the configuration of the `Value` column:

```json
{ ...
   "columns": {
      "Value": {
         "type": "observations",
         "data_type": "integer"
      }
   }
}
```

## Pivoted shape

### Pivoted single-measure data set

| Year | Location  | Number of Arthur's Bakes | Status      |
|:-----|:----------|-------------------------:|:------------|
| 2022 | London    |                       35 | Provisional |
| 2021 | Cardiff   |                       26 | Final       |
| 2020 | Edinburgh |                       90 | Final       |
| 2021 | Belfast   |                        0 | Final       |

Notice that the observation value column title (`Number of Arthur's Bakes`) does not use one of the [reserved column names](../convention.md#conventional-column-names), and therefore the `type` field must be set to `observations` in order for csvcubed to recognise it as such. In the example below, the `label` field has been configured for both the `unit` and `measure` fields. Please refer to the [Measures Configuration](./measures.md) and [Units Configuration](./units.md) sections for details of further configuration options available:

```json
{ ...
   "columns": {
      "Number of Arthur's Bakes": {
         "type": "observations",
         "data_type": "integer",
         "unit": {
            "label": "Count"
         },
         "measure": {
            "label": "Number of Stores"
         }
      }
   }
}
```

### Pivoted multi-measure data set

| Year | Location | Number of Arthur's Bakes | Revenue | Revenue Units  |
|:-----|:---------|-------------------------:|--------:|:---------------|
| 2022 | London   |                       35 |      25 | GBP (Sterling) |
| 2021 | Cardiff  |                       26 |      18 | GBP (Sterling) |

In this example, a second observation value column, `Revenue`,  has been added, with the associated unit contained in the `Revenue Units` column. As you can see, the `Revenue Units` column has been linked to the `Revenue` column through the `describes_observations` field. This must be formatted in exactly the same way for csvcubed to recognise the link and generate the correct results. However, there is no measure information associated for either of the observation value columns; this can be configured as follows:

```json
{ ...
   "columns": {
      "Number of Arthur's Bakes": {
         "type": "observations",
         "data_type": "integer",
         "unit": {
            "label": "Count"
         },
         "measure": {
            "label": "Number of Stores"
         }
      },
      "Revenue": {
         "type": "observations",
         "data_type": "decimal",
         "measure": {
            "label": "Revenue"
         }
      },
      "Revenue Units": {
         "type": "units",
         "describes_observations": "Revenue"
      }
   }
}
```

## Reference

| **field name** | **description**                                                                                                                                                                                                                                                                                                                                                      | **default value** |
|----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------|
| `type`         | The type of the column; to configure an observation column use the value `observations`. (Required)                                                                                                                                                                                                                                                                  | *dimension*       |
| `data_type`    | The [data type](https://www.w3.org/TR/2015/REC-tabular-metadata-20151217/#h-built-in-datatypes) of the observations. This should generally be a decimal or integer. (Optional)                                                                                                                                                                                       | *decimal*         |
| `unit`         | The unit for this observation column; this can a uri to an existing unit, or a dictionary containing a new or extended existing unit. If there is a unit column this field **must not** be provided. (Optional)                                                                                                                                                      | *none*            |
| `measure`      | The measure for this observation column; this can be a uri to an existing dimension, or a dictionary containing a new or extended existing measure. If your data set is in the [pivoted multi-measure shape](../../shape-data/pivoted-shape.md#multiple-measures), this field is required. If there is a measure column this field **must not** be provided. (Optional) | *none*            |
