# Column definitions

This page explores how to configure a cube's column definitions inside a [qube-config.json](../index.md) file. It
discusses which columns are required for a valid cube, how to define what your columns mean and how to tell csvcubed
to ignore data which isn't part of the cube.

## A valid cube

A CSV-W file provides detailed information about the columns beyond their values. In csvcubed, we create CSV-Ws which
express data cubes using W3C's [RDF Data Cube Vocabulary](https://www.w3.org/TR/vocab-data-cube/). The column
definitions in a [qube-config.json](../index.md) file are designed to map to components in the RDF Data Cube Vocabulary.

In order to be valid, a cube in csvcubed must have:

* at least one [Dimension](./dimensions.md),
* at least one [Observations column](./observations.md),
* at least one unit and measure defined; these may be attached either to the [Observations column](./observations.md),
  or be defined in [Measures columns](./measures.md) or [Units columns](./units.md),

And it may have:

* one or more [Attribute columns](./attributes/index.md); which provide clarification to observational data.

## Configuration

Consider the follow data set about the weight of badgers:

| Location  | Year | Average Badger Weight / kg |
|:----------|:-----|---------------------------:|
| Sheffield | 1996 |                        9.6 |
| Carlisle  | 1994 |                       10.5 |

For each of the columns that we need to configure, we write an entry in the `columns` section of the
[qube-config.json](./index.md) document, using the column title as key, and create a new JSON object containing the
column's configuration details.

Below, you can see that we've provided definitions for two of the three columns:

```json
{
    "$schema": "https://purl.org/csv-cubed/qube-config/v1",
    "title": "Badger weight watch",
    "columns": {
      "Location": {
         "type": "dimension"
      },
      "Average Badger Weight / kg": {
         "type": "observations",
         "measure": {
            "label": "Average Badger Weight"
         },
         "unit": {
            "label": "kg"
         }
      }
    }
}
```

If we don't define a column mapping for a column in the CSV file then it is **assumed to be a dimension** unless it uses
one of the configuration by convention [reserved names](../../../configuration/convention.md#conventional-column-names).

In our example:

* we didn't define a mapping for `Year` so it is assumed by csvcubed to be a dimension,
* the `Locations` column has been defined as a [Dimension](./dimensions.md), and
* the `Average Badger Weight / kg` column has been configured as an [Observations column](./observations.md) with
  [unit](../unit-definitions.md) and [measure](../measure-definitions.md) definitions.

## Supported Column Types

|                                                  |              What it means to csvcubed              |
|-------------------------------------------------:|:---------------------------------------------------:|
|             [Dimension](./dimensions.md) |    Identifies what the observed value describes.    |
| [Observations column](./observations.md) | Holds the statistical data which has been recorded. |
|         [Measures column](./measures.md) |            Specifies what was measured.             |
|               [Units column](./units.md) |           Specifies the unit of measure.            |
|       [Attribute](./attributes/index.md) |        Further describes the observed value.        |

## Ignoring columns

To ignore a column and not configure it, set the column's value to `false`. This will ensure the column will not be
recognised as part of the cube by csvcubed.

```json
{ ...
  "columns": {
    "The Column's Title": false
  }
}
```
