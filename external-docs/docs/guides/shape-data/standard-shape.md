# Standard Shape

> This page describes how to build and configure a standard shape data cube. For more information about the data shapes supported by csvcubed, see [Shaping your data](./index.md). The instructions below assume a basic understanding of writing a [qube-config.json file](../configuration/qube-config.md).

The standard shape extends the [common structure](./index.md#common-structure) by requiring that **each row** has a _measures_ column and a _units_ column; these columns define the measure and unit (of measure) for each row.

The standard shape is most appropriate where you have a [sparse](../../glossary/index.md#sparse-data) data cube, i.e. there are a large number of possible combinations of dimension values, but very few of them have observed values recorded. If your data cube is [dense](../../glossary/index.md#dense-data), then consider using the [pivoted shape](./pivoted-shape.md).

## Single Measure

In our example, the single measure observed is `Number of Arthur's Bakes` and the corresponding unit is `Count`.

| Year | Location  | Value |      Status |                  Measure |  Unit |
|:-----|:----------|------:|------------:|-------------------------:|------:|
| 2022 | London    |    35 | Provisional | Number of Arthur's Bakes | Count |
| 2021 | Cardiff   |    26 |       Final | Number of Arthur's Bakes | Count |
| 2020 | Edinburgh |    90 |       Final | Number of Arthur's Bakes | Count |
| 2021 | Belfast   |     0 |       Final | Number of Arthur's Bakes | Count |

The simplest [qube-config.json](../configuration/qube-config.md) we can define for this data set is:

```json
{
    "$schema": "https://purl.org/csv-cubed/qube-config/v1",
    "title": "Arthur's Bakes stores in UK cities from 2020 to 2022",
    "description": "The number of Arthur's Bakes stores in cities across the UK between 2020 and 2022.",
    "creator": "https://www.gov.uk/government/organisations/hm-revenue-customs",
    "publisher": "https://www.gov.uk/government/organisations/hm-revenue-customs",
    "columns": {
        "Year": {
            "type": "dimension"
        },
        "Location": {
            "type": "dimension"
        },
        "Value": {
            "type": "observations"
        },
        "Status": {
            "type": "attribute"
        },
        "Measure": {
            "type": "measures"
        },
        "Unit": {
            "type": "units"
        }
    }
}
```

It is possible to use the [configuration by convention approach](../configuration/convention.md) to generate a valid [standard shape](./standard-shape.md) cube without defining a [qube-config.json](../configuration/qube-config.md) at all. Just ensure that your columns use the [conventional column names](../configuration/convention.md#conventional-column-names) appropriate to their type.

## Multiple Measures

One of the benefits of the standard shape is that it is relatively straightforward to add new measure types and unit types; all that you have to do is add additional rows to your data set with the appropriate units and measures present.

We can extend our example data set so that it now includes revenue values for the given year by adding rows to the table:

| Year | Location | Value |      Status |                  Measure |                   Unit |
|:-----|:---------|------:|------------:|-------------------------:|-----------------------:|
| 2022 | London   |    35 | Provisional | Number of Arthur's Bakes |                  Count |
| 2022 | London   |    25 | Provisional |                  Revenue | GBP Sterling, Millions |
| 2021 | Cardiff  |    26 |       Final | Number of Arthur's Bakes |                  Count |
| 2021 | Cardiff  |    18 |       Final |                  Revenue | GBP Sterling, Millions |

Note that extending the data set to include multiple measures does not require any changes to the [qube-config.json](../configuration/qube-config.md) column definitions.

The same data could be represented in the [equivalent multi-measure pivoted shape](./pivoted-shape.md#multiple-measures) as follows:

| Year | Location | Number of Arthur's Bakes | Number of Stores Status | Revenue | Revenue Units  | Revenue Status |
|:-----|:---------|-------------------------:|:------------------------|--------:|:---------------|:---------------|
| 2022 | London   |                       35 | Provisional             |      25 | GBP (Sterling) | Provisional    |
| 2021 | Cardiff  |                       26 | Final                   |      18 | GBP (Sterling) | Final          |
