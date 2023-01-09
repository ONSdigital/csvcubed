## Single Measure

The [standard shape](./standard-shape.md) is flexible but it also has a lot of redundancy which can often be removed by using the more concise pivoted form. Our dataset on the distribution of the number of `Arthur's Bakes' stores can be expressed in the pivoted shape as follows:

| Year | Location  | Number of 'Arthur's Bakes' | Status      |
|:-----|:----------|---------------------------:|:------------|
| 2022 | London    |                         35 | Provisional |
| 2021 | Cardiff   |                         26 | Final       |
| 2020 | Edinburgh |                         90 | Final       |
| 2021 | Belfast   |                          0 | Final       |

Note that this shape doesn't require that you add any additional columns to the underlying [common structure](#common-structure); however it does require a different [qube-config.json](./configuration/qube-config.md) configuration; we must ensure that the measure and corresponding unit are attached to the _observations_ column:

```json
{
    "$schema": "http://purl.org/csv-cubed/qube-config/v1",
    "title": "'Arthur's Bakes' stores in UK cities from 2020 to 2022",
    "description": "The number of 'Arthurs' Bakes' stores in cities across the UK between 2020 and 2022.",
    "creator": "https://www.gov.uk/government/organisations/hm-revenue-customs",
    "publisher": "https://www.gov.uk/government/organisations/hm-revenue-customs",
    "columns": {
        "Year": {
            "type": "dimension"
        },
        "Location": {
            "type": "dimension"
        },
        "Number of 'Arthur's Bakes'": {
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

Incorporating multiple measures into the pivoted shape can be achieved by defining unit and measure information for **each** `observation` column. This can be configured in two ways:

1. By specifying a `unit` property within the `observation` column definition (as with the "Number of Arthur's Bakes" column).
2. By associating a separate `unit` column with the relevant `observation` column using the `describes_observations` property (as with the "Revenue Units" column).

Similarly, the `describes_observation` property can be used to associate attributes with the relevant observation values.

| Year | Location   | Number of 'Arthur's Bakes' | Number of Stores Status | Revenue | Revenue Units  | Revenue Status | 
|:-----|:-----------|---------------------------:|:------------------------|--------:|:---------------|:---------------|
| 2022 | London     |                         35 | Provisional             |      25 | GBP (Sterling) | Provisional    |
| 2021 | Cardiff    |                         26 | Final                   |      18 | GBP (Sterling) | Final          |

```json
{
    "$schema": "http://purl.org/csv-cubed/qube-config/v1",
    "title": "'Arthur's Bakes' stores and revenues in UK cities from 2020 to 2022",
    "description": "The number of 'Arthurs' Bakes' stores and store revenues in cities across the UK between 2020 and 2022.",
    "creator": "https://www.gov.uk/government/organisations/hm-revenue-customs",
    "publisher": "https://www.gov.uk/government/organisations/hm-revenue-customs",
    "columns": {
        "Year": {
            "type": "dimension"
        },
        "Location": {
            "type": "dimension"
        },
        "Number of 'Arthur's Bakes'": {
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