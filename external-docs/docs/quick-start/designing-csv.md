# Designing a CSV

## A transcribed video walkthrough

<iframe src="https://share.descript.com/embed/SJiVPSziEkw" width="640" height="360" frameborder="0" allowfullscreen></iframe>

## Prerequisites to follow along

csvcubed must be installed in order to proceed, please go back to [installation](installation.md).

## How csvcubed interprets a CSV

csvcubed needs to understand how your statistical data is structured in order to make it more machine readable. There are two ways that you can do this with csvcubed, we are covering the [configuration by convention approach](../guides/configuration/convention.md) in this quick-start. Configuration by convention requires a [standard CSV data shape](../guides/shape-data/index.md#standard-shape) with conventional column titles and fill it out with your data which is explained briefly below.

## Structuring your data

### Standard shape

The [standard shape](../guides/shape-data/index.md#standard-shape) of data is the recommended way to start using csvcubed. It requires that your CSV has the following columns:

| ...Identifying characteristics... | Value | Measure | Unit |
|:---------------------------------:|------:|--------:|-----:|
|                ...                |   3.4 |  Length | Feet |
|                ...                |   3.6 |  Length | Feet |

In the above table:

* *identifying characteristics* are one or more columns which identify the sub-set of the population that has been observed in a given row. These are called [dimensions](../glossary/index.md#dimension) elsewhere in documentation.
* the `Value` column contains the value which has been observed or measured; there is only ever one observed value per row in the [standard shape](../guides/shape-data/index.md#standard-shape).
* the `Measure` column describes what has been observed or measured; note that the measure should not include any information about the units of measure.
* the `Unit` column describes the unit of measure in which the `Value` has been recorded.

The names of the columns is how csvcubed interprets what each column contains in the [configuration by convention approach](../guides/configuration/convention.md). Using the column titles `Value`, `Measure` and `Unit` or one of their [synonyms](../guides/configuration/index.md#conventional-column-names) in your CSV will work. All other columns are assumed to be *identifying characteristics* ([dimensions](../glossary/index.md#dimensionl)).

### Pivoted shape

Once you have gained some familiarity with using csvcubed, you may find that the [pivoted shape](../guides/shape-data/pivoted-shape.md) is a better way to represent your data. See the [Shaping your data](../guides/shape-data/index.md) section for more information on the pivoted shape.

## Adding your data

First, we start by taking the above shape and adding columns for each of your *identifying characteristics* ([dimensions](../glossary/index.md#dimension)).

From hereon in we will be creating a data set to represent the competition winners in Eurovision. Our CSV will be structured as per the following extract where `Year`, `Entrant`, `Song` and `Language` are the cube's identifying [dimensions](../glossary/index.md#dimension). Note that we have included multiple measures in this dataset, as `Final Rank`, `Final Points` and `People on Stage` are recorded for each contestant:

| Year | Entrant            | Song     | Language | Value |         Measure |     Unit |
|:----:|:-------------------|:---------|:---------|------:|----------------:|---------:|
| 1974 | ABBA               | Waterloo | English  |     1 |      Final Rank | Unitless |
| 1974 | ABBA               | Waterloo | English  |    24 |    Final Points | Unitless |
| 1974 | ABBA               | Waterloo | English  |     6 | People on Stage |   Number |
| 2008 | Charlotte Perrelli | Hero     | English  |     5 | People on Stage |   Number |
| 2008 | Charlotte Perrelli | Hero     | English  |    18 |      Final Rank | Unitless |
| 2008 | Charlotte Perrelli | Hero     | English  |    47 |    Final Points | Unitless |

```csv
Year,Entrant,Song,Language,Value,Measure,Unit
1974,ABBA,Waterloo,English,1,Final Rank,Unitless
1974,ABBA,Waterloo,English,24,Final Points,Unitless
1974,ABBA,Waterloo,English,6,People on Stage,Number
2008,Charlotte Perrelli,Hero,English,5,People on Stage,Number
2008,Charlotte Perrelli,Hero,English,18,Final Rank,Unitless
2008,Charlotte Perrelli,Hero,English,47,Final Points,Unitless
```

You can [download the full CSV](https://raw.githubusercontent.com/GSS-Cogs/csvcubed-demo/v1.0/sweden_at_eurovision_no_missing.csv) from GitHub.

## Next

The next step is to [build a CSV-W](./build.md).

## Optional: further reading

The other way to configure a CSV-W cube is using the [explicit configuration approach](../guides/configuration/qube-config.md) - you write a JSON configuration file which tells csvcubed exactly how to interpret your data.
