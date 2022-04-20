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
The templates are currently in version 1.0; with future development planned. You can see the entire list of the templates inline below or on [csvcubed github](https://github.com/GSS-Cogs/csvcubed/tree/main/csvcubed/csvcubed/readers/cubeconfig/v1_0/templates). The `from_template` funcitonality fetches the most recent version of our templates from the web.

### Date/Time period template

| Template                                                                                                                                             | Description                                                                                                                  | Example             |
| ---------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------- |
| [year](https://github.com/GSS-Cogs/csvcubed/blob/main/csvcubed/csvcubed/readers/cubeconfig/v1_0/templates/calendar-year.json)                        | The calendar period of year                                                                                                  | 2017                |
| [half-year](https://github.com/GSS-Cogs/csvcubed/blob/main/csvcubed/csvcubed/readers/cubeconfig/v1_0/templates/calendar-half-year.json)              | The calendar period of half-year (Jaunary-June, July-December)                                                               | 2017-H2             |
| [quarter](https://github.com/GSS-Cogs/csvcubed/blob/main/csvcubed/csvcubed/readers/cubeconfig/v1_0/templates/calendar-quarter.json)                  | The calendar period of quarter (January-March, April-June, July-September, October-December)                                 | 2019-Q3             |
| [month](https://github.com/GSS-Cogs/csvcubed/blob/main/csvcubed/csvcubed/readers/cubeconfig/v1_0/templates/calendar-month.json)                      | The calendar period of month                                                                                                 | 1995-11             |
| [week](https://github.com/GSS-Cogs/csvcubed/blob/main/csvcubed/csvcubed/readers/cubeconfig/v1_0/templates/calendar-week.json)                        | The ISO-8601 definition of calendar week                                                                                     | 2014-25             |
| [day](https://github.com/GSS-Cogs/csvcubed/blob/main/csvcubed/csvcubed/readers/cubeconfig/v1_0/templates/calendar-day.json)                          | The calendar period of day                                                                                                   | 1999-12-31          |
| [hour](https://github.com/GSS-Cogs/csvcubed/blob/main/csvcubed/csvcubed/readers/cubeconfig/v1_0/templates/calendar-hour.json)                        | The calendar period of hour                                                                                                  | 2015-11-18T06       |
| [minute](https://github.com/GSS-Cogs/csvcubed/blob/main/csvcubed/csvcubed/readers/cubeconfig/v1_0/templates/calendar-minute.json)                    | The calendar period of minute                                                                                                | 2015-11-18T06:42    |
| [second](https://github.com/GSS-Cogs/csvcubed/blob/main/csvcubed/csvcubed/readers/cubeconfig/v1_0/templates/calendar-second.json)                    | The calendar period of second                                                                                                | 2015-11-18T06:42:32 |
| [government-year](https://github.com/GSS-Cogs/csvcubed/blob/main/csvcubed/csvcubed/readers/cubeconfig/v1_0/templates/government-year.json)           | The UK Government calendar period of year starting in April                                                                  | 2017-2018           |
| [government-half-year](https://github.com/GSS-Cogs/csvcubed/blob/main/csvcubed/csvcubed/readers/cubeconfig/v1_0/templates/government-half-year.json) | The UK Government calendar period of half-year starting in April (April-September, October-March)                            | 2010-2011/H1        |
| [government-quarter](https://github.com/GSS-Cogs/csvcubed/blob/main/csvcubed/csvcubed/readers/cubeconfig/v1_0/templates/government-quarter.json)     | The UK Government calendar period of quarter starting in April (April-June, July-September, October-December, January-March) | 2014-2018/Q2        |
| [government-week](https://github.com/GSS-Cogs/csvcubed/blob/main/csvcubed/csvcubed/readers/cubeconfig/v1_0/templates/government-week.json)           | The UK Government calendar period of week as defined at reference.data.gov.uk.                                               | 2019-2020/7         |

### Date/Time instant templates

| Template                                                                                                                                       | Description                                        | Example             |
| ---------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- | ------------------- |
| [gregorian-instant](https://github.com/GSS-Cogs/csvcubed/blob/main/csvcubed/csvcubed/readers/cubeconfig/v1_0/templates/gregorian-instant.json) | The gregorian-instant expressed in ISO-8601 format | 1970-01-01T00:00:00 |

### Attribute templates

| Template                                                                                                                                         | Description                                                 | Example    |
| ------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------- | ---------- |
| [observation-status](https://github.com/GSS-Cogs/csvcubed/blob/main/csvcubed/csvcubed/readers/cubeconfig/v1_0/templates/observation-status.json) | A template which describes the status of the observed value | Suppressed |