# Shaping your data

> This page introduces the input data shapes supported by csvcubed with the aim of helping you understand which to use and how to generate data in the right shape.  

csvcubed requires that all CSV data inputs are provided in one of two specialised forms of [tidy data](../glossary/index.md#tidy-data):

* the [standard approach](./standard-shape.md) - the recommended shape for sparse multi-measure data cubes.
* the [pivoted approach](./pivoted-shape.md) - the recommended shape for dense data cubes.

These two shapes share a number of similarities in how they require data to be structured; this is explored in the [common structure](#common-structure) section below. More detailed configuration instructions can be found in the relevant [standard shape](./standard-shape.md) and [pivoted shape](./pivoted-shape.md) sections.

## Common Structure

csvcubed requires that data is structured as per the following example, regardless of data shape:

| Year | Location  | Value |      Status |
|:-----|:----------|------:|------------:|
| 2022 | London    |    35 | Provisional |
| 2021 | Cardiff   |    26 |       Final |
| 2020 | Edinburgh |    90 |       Final |
| 2021 | Belfast   |     0 |       Final |

> Data set representing the number of 'Arthur's Bakes' stores in UK cities from 2020 to 2022

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

## Converting to the standard shape

It is possible to convert data from the [pivoted shape](./pivoted-shape.md) into the [standard shape](./standard-shape.md); see the following examples using the [pandas library](https://pandas.pydata.org/) in Python and the [tidyverse library](https://tidyverse.org/) in R.

Starting with a dataframe in the pivoted shape:

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
    standard_shaped_data = pivoted_data.melt(
        id_vars=["Year", "Location"],
        value_vars=["Number of 'Arthur's Bakes'", "Revenue (GBP Sterling, Millions)"],
        var_name="Measure",
        value_name="Value"
    )

    # Create a units column based on the measure.
    standard_shaped_data["Unit"] = standard_shaped_data["Measure"].map({
        "Number of 'Arthur's Bakes'": "Count",
        "Revenue (GBP Sterling, Millions)": "GBP Sterling, Millions"
    })

    # Rename the measures now that the units have been extracted into their own column.
    standard_shaped_data["Measure"] = standard_shaped_data["Measure"].replace({
        "Revenue (GBP Sterling, Millions)": "Revenue"
    })

    # Output the data to CSV for input to csvcubed.
    standard_shaped_data.to_csv("my-data.csv", index=False)
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

    standard_shape_data <- pivoted_shape_data %>% 
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
    standard_shape_data %>% write.csv(file="my-data.csv", row.names=FALSE)
    ```

The data set is now in the standard shape:

| Year | Location |                    Measure | Value |                   Unit |
|:-----|:---------|---------------------------:|------:|-----------------------:|
| 2022 | London   | Number of 'Arthur's Bakes' |    35 |                  Count |
| 2021 | Cardiff  | Number of 'Arthur's Bakes' |    26 |                  Count |
| 2022 | London   |                    Revenue |    25 | GBP Sterling, Millions |
| 2021 | Cardiff  |                    Revenue |    18 | GBP Sterling, Millions |

## Converting to the pivoted shape

TODO