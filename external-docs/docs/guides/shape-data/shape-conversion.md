# Converting data shape

Depending on the format of your existing data set, you may need to convert it to the standard or pivoted shape in order to use csvcubed. See the instructions below on how to achieve this in Python and R.

## Converting to the standard shape

To convert data from the [pivoted shape](./pivoted-shape.md) into the [standard shape](./standard-shape.md), see the following examples using the [pandas library](https://pandas.pydata.org/) in Python and the [tidyverse library](https://tidyverse.org/) in R.

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

To convert data from the [standard shape](./standard-shape.md) into the [pivoted shape](./pivoted-shape.md), see the following examples using the [pandas library](https://pandas.pydata.org/) in Python and the [tidyverse library](https://tidyverse.org/) in R.

=== "Python"
    ```python
    import pandas as pd

    # Starting with a dataframe in the standard shape format
    standard_shape_data = {
        "Year": [2022, 2021, 2022, 2021],
        "Location": ["London", "Cardiff", "London", "Cardiff"],
        "Measure": [
            "Number of 'Arthur's Bakes'",
            "Number of 'Arthur's Bakes'",
            "Revenue",
            "Revenue",
        ],
        "Value": [35, 26, 25, 18],
        "Unit": ["Count", "Count", "GBP Sterling, Millions", "GBP Sterling, Millions"]
    }

    # Pivot the dataframe
    pivoted_data = standard_shaped_data.pivot(
        index=["Year", "Location"], columns="Measure", values="Value"
    ).reset_index()

    # Rename the "Revenue" column to include the unit information
    pivoted_data.rename(
        columns={"Revenue": "Revenue (GBP Sterling, Millions)"}
    )

    # Output the data to CSV for input to csvcubed.
    pivoted_data.to_csv("my-data.csv", index=False)
    ```
=== "R"
    ```r
    library(tidyverse)

    standard_shape_data <- tibble(
        Year = c(2022, 2021, 2022, 2021),
        Location = c("London", "Cardiff", "London", "Cardiff"),
        Measure = c("Number of 'Arthur's Bakes'", "Number of 'Arthur's Bakes'", "Revenue", "Revenue"),
        Value = c(35, 26, 25, 18),
        Unit = c("Count", "Count", "GBP Sterling, Millions", "GBP Sterling, Millions")
    )

    pivoted_shape_data <- standard_shape_data %>%
        # Identify the columns to be included in the output
        select(Year, Location, Measure, Value) %>%
        # Pivot the data
        pivot_wider(
            names_from = Measure,
            values_from = Value
        ) %>%
        # Rename the "Revenue" column to include the unit information
        rename("Revenue (GBP Sterling, Millions)" = "Revenue")

    # Output the data to CSV for input to csvcubed.
    pivoted_shape_data %>% write.csv(file="my-data.csv", row.names = FALSE)
    ```

The data set is now in the pivoted shape:

| Year | Location | Number of 'Arthur's Bakes' | Revenue (GBP Sterling, Millions) |
|:-----|:---------|---------------------------:|---------------------------------:|
| 2022 | London   |                         35 |                               25 |
| 2021 | Cardiff  |                         26 |                               18 |
