# Shaping your data

> This page discusses the shapes of input data supported by csvcubed with the aim to help you understand which to use and how to generate data in the right shape.  

csvcubed requires that all CSV data inputs are provided in one of two specialised form of [tidy data](../glossary/index.md#tidy-data):

* the [canonical approach](#canonical-shape) - the **default recommended shape** accepted by csvcubed. It is the **most flexible** but also the most **verbose**.
* the [pivoted approach](#pivoted-shape) - a **terser** shape currently only compatible with data sets containing a **single measure**.

These two shapes share a number of similarities in how they require data to be structured; this is explored in the following section on the [common structure](#common-structure).

## Common Structure

Both data shapes expect that data is structured as per the following example:

_Data set representing the number of 'Arthur's Bakes' stores in UK cities from 2020 to 2022_

| Year | Location  | Value |      Status |
|:-----|:----------|------:|------------:|
| 2022 | London    |    35 | Provisional |
| 2021 | Cardiff   |    26 |       Final |
| 2020 | Edinburgh |    90 |       Final |
| 2021 | Belfast   |     0 |       Final |

**Note that**:

1. The table has a flat and _tidy_ header row.
    * No attempt has been made to group headers or bring any identifying characteristics such as the year into the headers.
2. Each identifying characteristic has its own _dimension_ column.
    * the `Year` and `Location` _dimension_ columns define the subset of the population that the row's observed value covers, i.e. each row describes the number of _Arthur's Bakes_ stores in a particular UK city in a given year.
3. Every row has an _observed values_ column containing the measured value of some property.
    * the `Value` column holds the observed values here.
4. Each piece of information describing the _observed value_ has its own _attribute_ column.
    * the `Status` _attribute_ column contains information describing the state of the observed value itself.
    * Note that _attributes_ should only describe the observed value and must not identify any subset of the population.  

## Canonical Shape

The canonical shape extends the [common structure](#common-structure) by requiring that **each row** has a _measures_ column and a _units_ column; these columns define the measure and unit (of measure) for each row.

| Year | Location  | Value |      Status |                    Measure |  Unit |
|:-----|:----------|------:|------------:|---------------------------:|------:|
| 2022 | London    |    35 | Provisional | Number of 'Arthur's Bakes' | Count |
| 2021 | Cardiff   |    26 |       Final | Number of 'Arthur's Bakes' | Count |
| 2020 | Edinburgh |    90 |       Final | Number of 'Arthur's Bakes' | Count |
| 2021 | Belfast   |     0 |       Final | Number of 'Arthur's Bakes' | Count |

The simplest [qube-config.json](./qube-config.md) column mappings we can define for this data set are:

```json
{
    "$schema": "http://purl.org/csv-cubed/qube-config/v1.0",
    "title": "'Arthur's Bakes' stores in UK cities from 2020 to 2022",
    "description": "The number of 'Arthurs' Bakes' stores in cities across the UK between 2020 and 2022.",
    "creator": "HM Revenue & Customs",
    "publisher": "HM Revenue & Customs",
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

### Multiple Measures

One of the benefits of the canonical shape is that it makes it simple to add new measure types and unit types; all that you have to do is add additional rows to your data set with the appropriate units and measures present.

We can extend out example data set so that it now includes revenue values for the given year by adding rows to the table:

| Year | Location | Value |      Status |                    Measure |                   Unit |
|:-----|:---------|------:|------------:|---------------------------:|-----------------------:|
| 2022 | London   |    35 | Provisional | Number of 'Arthur's Bakes' |                  Count |
| 2022 | London   |    25 | Provisional |                    Revenue | GBP Sterling, Millions |
| 2021 | Cardiff  |    26 |       Final | Number of 'Arthur's Bakes' |                  Count |
| 2021 | Cardiff  |    18 |       Final |                    Revenue | GBP Sterling, Millions |

The same data could be more naturally represented in the equivalent pivoted shape:

| Year | Location | Number of 'Arthur's Bakes' | Revenue (GBP Sterling, Millions) |
|:-----|:---------|---------------------------:|---------------------------------:|
| 2022 | London   |                         35 |                               25 |
| 2021 | Cardiff  |                         26 |                               18 |

**Note that csvcubed does not currently support data sets containing multiple measures in the [pivoted shape](#pivoted-shape).**

### Converting from the Pivoted Shape to the Canonical Shape

Since csvcubed doesn't current support multi-measure data sets in the [pivoted shape](#pivoted-shape), it is often necessary to convert your data from the [pivoted shape](#pivoted-shape) into the [canonical shape](#canonical-shape). See the following examples using the [pandas library](https://pandas.pydata.org/) in python and using [tibble](https://tibble.tidyverse.org/) in R to convert from a pivoted to the canonical shape.

Starting with a dataframe looking in the pivoted form:

| Year | Location | Number of 'Arthur's Bakes' | Revenue (GBP Sterling, Millions) |
|:-----|:---------|---------------------------:|---------------------------------:|
| 2022 | London   |                         35 |                               25 |
| 2021 | Cardiff  |                         26 |                               18 |

=== "Python"
    ```python
    import pandas as pd

    # Starting with a dataframe in the pivoted format
    pivoted_data = pd.DataFrame({
        "Year": [2022, 2021],
        "Location": ["London", "Cardiff"],
        "Number of 'Arthur's Bakes'": [35, 26],
        "Revenue (GBP Sterling, Millions)": [25, 18]
    })

    # Melt the data frame - this reshapes the data so there are now 'Measure' and 'Value' columns.
    canonical_shaped_data = pivoted_data.melt(
        id_vars=["Year", "Location"],
        value_vars=["Number of 'Arthur's Bakes'", "Revenue (GBP Sterling, Millions)"],
        var_name="Measure",
        value_name="Value"
    )

    # Create a units column based on the measure.
    canonical_shaped_data["Unit"] = canonical_shaped_data["Measure"].map({
        "Number of 'Arthur's Bakes'": "Count",
        "Revenue (GBP Sterling, Millions)": "GBP Sterling, Millions"
    })

    # Rename the measures now that the units have been extracted into their own column.
    canonical_shaped_data["Measure"] = canonical_shaped_data["Measure"].replace({
        "Revenue (GBP Sterling, Millions)": "Revenue"
    })

    # Output the data to CSV for input to csvcubed.
    canonical_shaped_data.to_csv("my-data.csv", index=False)
    ```
=== "R"
    ```r
    library(tidyverse)

    pivoted_shape_data <- tibble( 
        Year = c(2022, 2021),
        Location = c("London", "Cardiff"),
        `Number of 'Arthur's Bakes'` = c(35, 26),
        `Revenue (GBP Sterling, Millions)` = c(25, 18)
    )

    canonical_shape_data <- pivoted_shape_data %>% 
        # Re-pivot the data frame - this reshapes the data so there are now 'Measure' and 'Value' columns.
        pivot_longer(
            cols = c(`Number of 'Arthur's Bakes'`, "Revenue (GBP Sterling, Millions)"), 
            names_to="Measure", 
            values_to="Value"
        ) %>% 
        # Create a units column based on the measure.
        add_column(
            `Unit` = recode(
                .$Measure,
                `Number of 'Arthur's Bakes'` = "Count",
                `Revenue (GBP Sterling, Millions)` = "GBP Sterling, Millions"
            )
        ) %>%
        # Rename the measures now that the units have been extracted into their own column.
        mutate(
            `Measure` = recode(
                .$Measure,
                `Revenue (GBP Sterling, Millions)` = "Revenue"
            )
        )

    # Output the data to CSV for input to csvcubed.
    canonical_shape_data %>% write.csv(file="my-data.csv", row.names=FALSE)
    ```

The data is now in canonical form.

| Year | Location |                    Measure | Value |                   Unit |
|:-----|:---------|---------------------------:|------:|-----------------------:|
| 2022 | London   | Number of 'Arthur's Bakes' |    35 |                  count |
| 2021 | Cardiff  | Number of 'Arthur's Bakes' |    26 |                  count |
| 2022 | London   |                    Revenue |    25 | GBP Sterling, Millions |
| 2021 | Cardiff  |                    Revenue |    18 | GBP Sterling, Millions |

## Pivoted Shape

Suggest that people start from the canonical form and alter their configurations if they realise every measure has the same measure.

todo: Pivoted Example
