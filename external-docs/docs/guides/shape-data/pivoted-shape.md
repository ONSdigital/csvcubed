# Pivoted Shape

> This page describes how to build and configure a pivoted shape data cube. For more information about the data shapes supported by csvcubed, see [Shaping your data](./index.md). The instructions below assume a basic understanding of writing a [qube-config.json file](../configuration/qube-config.md).

## Single Measure

The [standard shape](./standard-shape.md) is flexible but has a lot of redundancy which can often be removed by using the more concise pivoted form. Our data set on the distribution of the number of Arthur's Bakes stores can be expressed in the pivoted shape as follows:

| Year | Location  | Number of Arthur's Bakes | Status      |
|:-----|:----------|-------------------------:|:------------|
| 2022 | London    |                       35 | Provisional |
| 2021 | Cardiff   |                       26 | Final       |
| 2020 | Edinburgh |                       90 | Final       |
| 2021 | Belfast   |                        0 | Final       |

Note that this shape doesn't require that you add any additional columns to the underlying [common structure](./index.md#common-structure); however it does require a different (and explicit) [qube-config.json](../configuration/qube-config.md) configuration, to ensure that the corresponding measure and unit are attached to the _observations_ column:

```json
{
    "$schema": "https://purl.org/csv-cubed/qube-config/v1",
    "title": "Arthur's Bakes stores in UK cities from 2020 to 2022",
    "description": "The number of Arthurs' Bakes stores in cities across the UK between 2020 and 2022.",
    "creator": "https://www.gov.uk/government/organisations/hm-revenue-customs",
    "publisher": "https://www.gov.uk/government/organisations/hm-revenue-customs",
    "columns": {
        "Year": {
            "type": "dimension"
        },
        "Location": {
            "type": "dimension"
        },
        "Number of Arthur's Bakes": {
            "type": "observations",
            "unit": {
                "label": "Count"
            },
            "measure": {
                "label": "Number of Stores"
            }
        },
        "Status": {
            "type": "attribute"
        }
    }
}
```

## Multiple Measures

Incorporating multiple measures into the pivoted shape can be achieved by defining [unit](../../glossary/index.md#unit) and [measure](../../glossary/index.md#measure) information for **each** `observation` column. Measures in the pivoted shape are always configured against the observed values column in the associated [qube-config.json file](../configuration/qube-config.md). Units can be configured in two ways:

1. By specifying a `unit` property within the `observation` column definition (as with the "Number of Arthur's Bakes" [observation](../../glossary/index.md#observation-observed-value) column).
2. By associating a separate `unit` column with the relevant `observation` column using the `describes_observations` property (as with the "Revenue Units" [unit](../../glossary/index.md#unit) column). See the [Measure and Unit Columns Configuration](../configuration/qube-config.md/#measure-and-unit-columns-configuration) section for more information on the `describes_observation` property.

Similarly, the `describes_observation` property can be used to associate _attributes_ with the relevant _observation_ values, as with the "Number of Stores Status" and "Revenue Status" [attribute](../../glossary/index.md#attribute) columns below. See the [Attributes configuration](../configuration/qube-config.md/#attributes-configuration) section for more information on the `describes_observation` property.

| Year | Location | Number of Arthur's Bakes | Number of Stores Status | Revenue | Revenue Units  | Revenue Status |
|:-----|:---------|-------------------------:|:------------------------|--------:|:---------------|:---------------|
| 2022 | London   |                       35 | Provisional             |      25 | GBP (Sterling) | Provisional    |
| 2021 | Cardiff  |                       26 | Final                   |      18 | GBP (Sterling) | Final          |

```json
{
    "$schema": "https://purl.org/csv-cubed/qube-config/v1",
    "title": "Arthur's Bakes stores and revenues in UK cities from 2020 to 2022",
    "description": "The number of Arthur's Bakes stores and store revenues in cities across the UK between 2020 and 2022.",
    "creator": "https://www.gov.uk/government/organisations/hm-revenue-customs",
    "publisher": "https://www.gov.uk/government/organisations/hm-revenue-customs",
    "columns": {
        "Year": {
            "type": "dimension"
        },
        "Location": {
            "type": "dimension"
        },
        "Number of Arthur's Bakes": {
            "type": "observations",
            "unit": {
                "label": "Count"
            },
            "measure": {
                "label": "Number of Stores"
            }
        },
        "Number of Stores Status": {
            "type": "attribute",
            "describes_observations": "Number of Arthur's Bakes"
        },
        "Revenue": {
            "type": "observations",
            "measure": {
                "label": "Revenue"
            }
        },
        "Revenue Units": {
            "type": "units",
            "describes_observations": "Revenue"
        },
        "Revenue Status": {
            "type": "attribute",
            "describes_observations": "Revenue"
        }
    }
}
```