# Using column templates

Column templates are pre-configured column definitions which speed up creating linked data.

This page aims to introduce column template functionality, show you how to make use of it in a [qube-config.json](qube-config.md) configuration file and list common templates you might wish to use yourself.

Also see the quick start [introduction to linking data](../../quick-start/linking-data.md).

## How to use templates

To use a column template in the [qube-config.json](qube-config.md) configuration file set the `from_template` property on the column definition to one the available templates, for example with a column representing year:

```json
"Year": {
    "from_template": "year"
}
```

### Overriding template configuration

It is possible to override the configuration inherited from the template; do this by manually specifying individual properties you wish to override within the column definition, e.g. with a column representing year:

```json
"Year": {
    "from_template": "year",
    "label": "Competition Year"
}
```

In the above example, we have reused the `year` template, but given the dimension created the label of `Competition Year`.

## Available templates

The templates are currently in version 1.0; with future development planned. You can see the entire list of the templates inline below or on [csvcubed github](https://github.com/GSS-Cogs/csvcubed/tree/main/src/csvcubed/readers/cubeconfig/v1_0/templates). The `from_template` functionality fetches the most recent version of our templates from the web.

### Date/Time period template

| Template                                                                                           | Description                                                                                                                                                                                        | Example             |
|----------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------|
| [year](https://purl.org/csv-cubed/qube-config/templates/calendar-year.json)                        | The calendar period of year                                                                                                                                                                        | 2017                |
| [half-year](https://purl.org/csv-cubed/qube-config/templates/calendar-half-year.json)              | The calendar period of half-year (January-June, July-December)                                                                                                                                     | 2017-H2             |
| [quarter](https://purl.org/csv-cubed/qube-config/templates/calendar-quarter.json)                  | The calendar period of quarter (January-March, April-June, July-September, October-December)                                                                                                       | 2019-Q3             |
| [month](https://purl.org/csv-cubed/qube-config/templates/calendar-month.json)                      | The calendar period of month                                                                                                                                                                       | 1995-11             |
| [week](https://purl.org/csv-cubed/qube-config/templates/calendar-week.json)                        | The ISO-8601 definition of calendar week                                                                                                                                                           | 2014-W25            |
| [day](https://purl.org/csv-cubed/qube-config/templates/calendar-day.json)                          | The calendar period of day                                                                                                                                                                         | 1999-12-31          |
| [hour](https://purl.org/csv-cubed/qube-config/templates/calendar-hour.json)                        | The calendar period of hour                                                                                                                                                                        | 2015-11-18T06       |
| [minute](https://purl.org/csv-cubed/qube-config/templates/calendar-minute.json)                    | The calendar period of minute                                                                                                                                                                      | 2015-11-18T06:42    |
| [second](https://purl.org/csv-cubed/qube-config/templates/calendar-second.json)                    | The calendar period of second                                                                                                                                                                      | 2015-11-18T06:42:32 |
| [government-year](https://purl.org/csv-cubed/qube-config/templates/government-year.json)           | The UK Government calendar period of year starting in April                                                                                                                                        | 2017-2018           |
| [government-half-year](https://purl.org/csv-cubed/qube-config/templates/government-half-year.json) | The UK Government calendar period of half-year starting in April (April-September, October-March)                                                                                                  | 2010-2011/H1        |
| [government-quarter](https://purl.org/csv-cubed/qube-config/templates/government-quarter.json)     | The UK Government calendar period of quarter starting in April (April-June, July-September, October-December, January-March)                                                                       | 2014-2015/Q2        |
| [government-week](https://purl.org/csv-cubed/qube-config/templates/government-week.json)           | The UK Government calendar period of week as defined at reference.data.gov.uk.                                                                                                                     | 2019-2020/W7        |
| [mixed-period](https://purl.org/csv-cubed/qube-config/templates/mixed-period.json)                 | Dimension consisting of mixed time periods, e.g. 2020-Q4 (quarter), 2021-06 (month), 2019-08-06 (day). See [How to deal with Mixed Periods](#how-to-deal-with-mixed-periods) for further guidance. | See Description     |

### Date/Time instant/interval templates

| Template                                                                                       | Description                                         | Example                 |
|------------------------------------------------------------------------------------------------|-----------------------------------------------------|-------------------------|
| [gregorian-instant](https://purl.org/csv-cubed/qube-config/templates/gregorian-instant.json)   | The gregorian-instant expressed in ISO-8601 format  | 1970-01-01T00:00:00     |
| [gregorian-interval](https://purl.org/csv-cubed/qube-config/templates/gregorian-interval.json) | The gregorian-interval expressed in ISO-8601 format | 1970-01-01T00:00:00/P3D |


### Geographical area templates

| Template                                                                                             | Description                                     | Example   |
|------------------------------------------------------------------------------------------------------|-------------------------------------------------|-----------|
| [statistical-geography](https://purl.org/csv-cubed/qube-config/templates/statistical-geography.json) | ONS Geography codes for statistical geographies | K02000001 |


### Attribute templates

| Template                                                                                       | Description                                                 | Example    |
|------------------------------------------------------------------------------------------------|-------------------------------------------------------------|------------|
| [observation-status](https://purl.org/csv-cubed/qube-config/templates/observation-status.json) | A template which describes the status of the observed value | Suppressed |

### Unit templates

Units used, have to match the terminal part of the URI exactly including case sensitivity.

| Template                                                                       | Description                                    | Example                                                                              |
|--------------------------------------------------------------------------------|------------------------------------------------|--------------------------------------------------------------------------------------|
| [qudt-units](https://purl.org/csv-cubed/qube-config/templates/qudt-units.json) | A template which contains units of measurement | [http://qudt.org/vocab/unit/PoundSterling](http://qudt.org/vocab/unit/PoundSterling) |

## How to deal with Mixed Periods

The purpose of this section is to provide guidance on configuration of a data set with mixed time periods, e.g. daily, weekly, monthly, government-year, half-year, etc. Also, an example of how to wrangle a dataset using Python so that the CSV can be used to create a CSV-W is provided.

In the table below we have two different types of dates, representing daily and weekly frequencies. The format of the daily figures is acceptable. However, there is an issue with the weekly data. The date `2019-04-01` represents the week beginning `2019-04-01`, and `2019-04-08` represents the following week. Instead, the ISO8601 format `week/YYYY-WWW` should be used, e.g., the week beginning `2019-04-01` should be `week/2019-W14`.

| Period     | Frequency | ... |
|------------|-----------|-----|
| 2019-04-01 | Daily     | ... |
| 2019-04-02 | Daily     | ... |
| 2019-04-01 | Weekly    | ... |
| 2019-04-08 | Weekly    | ... |

**NB:** it is important to validate whether the weekly data matches the ISO8601 definition, as this is slightly different from the traditional Gregorian calendar.

**Things to note:**

- The week date representation must commence on a Monday. If not, a [gregorian-interval](https://purl.org/csv-cubed/qube-config/templates/gregorian-interval.json) of one week must be used.
- Unlike the Gregorian calendar, there are no weeks that extend across years. Each ISO8601 year consists of either 52 or 53 weeks depending on when the year begins. If 1 January falls on a Monday, Tuesday, Wednesday or Thursday it is in week 01 of the new year. If 1 January falls on a Friday, Saturday or Sunday, it is in week 52 or 53 of the previous year.
- More information can be found [here](https://en.wikipedia.org/wiki/ISO_8601#Week_dates)

### How to format mixed periods

- For daily data, prefix the date with `day/`: `day/YYYY-MM-DD`
- For weekly data, calculate the ISO8601 week value and prefix with `week/`: `week/YYYY-WWW`. For example, the week commencing 01/04/2019 would be `week/2019-W14`.
- Once the dates have been formatted as above, the 'Frequency' column should be removed.

### Example Python code

The following code is an example of how this can be achieved in Python:

```python
import click
import pandas as pd
import numpy as np
from pathlib import Path

@click.command()
@click.argument("input", type=click.Path(exists=True, path_type=Path))
@click.option("--output", default=Path("./output.csv"), type=click.Path(path_type=Path))
def wrangle(input: Path(), output: Path()) -> None:
    df = pd.read_csv(input_file_path)

    # Convert dates which represent weeks to correct format 'YYYY-WWW'
    df['Period'].loc[df['Frequency']] = np.where(df['Frequency'] == 'Weekly', pd.to_datetime(df['Period']).dt.strftime('%Y-%V'), df['Period'])

    # Prefix the date with `week/` when Weekly is used in frequency column
    df['Period'] = np.where(df['Frequency'] == 'Weekly', ('week/' + df['Period']), df['Period'])

    # Prefix the date with `day/` when Daily is used in frequency column
    df['Period'] = np.where(df['Frequency'] == 'Daily', ('day/' + df['Period']), df['Period'])

    # Drop 'Frequency' column
    df.drop("Frequency", axis=1, inplace=True)

    # Save the updated file as CSV
    df.to_csv(output_file_path, index=False)
    return

if __name__ == "__main__":
    wrangle()
```


Making this transformation to the table above the period column should appear as follows:

| Period         | ... |
|----------------|-----|
| day/2019-04-01 | ... |
| day/2019-04-02 | ... |
| week/2019-W14  | ... |
| week/2019-W15  | ... |

### Next Steps

An example of how the `Period` column should be described in the [qube-config](qube-config.md) file using the mixed period template can be found below:

```json
"columns": {
    ...
        "Period": {
            "from_template": "mixed-period"
        },
    ...
```
