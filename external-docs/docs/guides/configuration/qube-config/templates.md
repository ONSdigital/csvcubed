# Using column templates

Column templates are pre-configured column definitions which speed up creating linked data.

This page aims to introduce column template functionality, show you how to make use of it in a [qube-config.json](index.md) configuration file and list common templates you might wish to use yourself.

Also see the quick start [introduction to linking data](../../../quick-start/linking-data.md).

Templates are currently configured for [dimensions](./columns/dimensions.md), [resource attributes](./columns/attributes/attribute-resources.md) and [units columns](./columns/units.md).

## How to use templates

To use a column template in the [qube-config.json](index.md) configuration file set the `from_template` property on the column definition to one the available templates, for example with a column representing year:

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

The templates are currently in version 1.0; with future development planned. You can see the entire list of the templates inline below or on [csvcubed GitHub](https://github.com/GSS-Cogs/csvcubed/tree/main/src/csvcubed/readers/cubeconfig/v1_0/templates). The `from_template` functionality fetches the most recent version of our templates from the web.

### Date/Time period template

| Template                                                                                           | Description                                                                                                                               | Example             |
|----------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|---------------------|
| [year](https://purl.org/csv-cubed/qube-config/templates/calendar-year.json)                        | The calendar period of year                                                                                                               | 2017                |
| [half-year](https://purl.org/csv-cubed/qube-config/templates/calendar-half-year.json)              | The calendar period of half-year (January-June, July-December)                                                                            | 2017-H2             |
| [quarter](https://purl.org/csv-cubed/qube-config/templates/calendar-quarter.json)                  | The calendar period of quarter (January-March, April-June, July-September, October-December)                                              | 2019-Q3             |
| [month](https://purl.org/csv-cubed/qube-config/templates/calendar-month.json)                      | The calendar period of month                                                                                                              | 1995-11             |
| [week](https://purl.org/csv-cubed/qube-config/templates/calendar-week.json)                        | The ISO-8601 definition of calendar week                                                                                                  | 2014-W25            |
| [day](https://purl.org/csv-cubed/qube-config/templates/calendar-day.json)                          | The calendar period of day                                                                                                                | 1999-12-31          |
| [hour](https://purl.org/csv-cubed/qube-config/templates/calendar-hour.json)                        | The calendar period of hour                                                                                                               | 2015-11-18T06       |
| [minute](https://purl.org/csv-cubed/qube-config/templates/calendar-minute.json)                    | The calendar period of minute                                                                                                             | 2015-11-18T06:42    |
| [second](https://purl.org/csv-cubed/qube-config/templates/calendar-second.json)                    | The calendar period of second                                                                                                             | 2015-11-18T06:42:32 |
| [government-year](https://purl.org/csv-cubed/qube-config/templates/government-year.json)           | The UK Government calendar period of year starting in April                                                                               | 2017-2018           |
| [government-half-year](https://purl.org/csv-cubed/qube-config/templates/government-half-year.json) | The UK Government calendar period of half-year starting in April (April-September, October-March)                                         | 2010-2011/H1        |
| [government-quarter](https://purl.org/csv-cubed/qube-config/templates/government-quarter.json)     | The UK Government calendar period of quarter starting in April (April-June, July-September, October-December, January-March)              | 2014-2015/Q2        |
| [government-week](https://purl.org/csv-cubed/qube-config/templates/government-week.json)           | The UK Government calendar period of week as defined at reference.data.gov.uk.                                                            | 2019-2020/W7        |
| [mixed-period](https://purl.org/csv-cubed/qube-config/templates/mixed-period.json)                 | Template allows the definition of mixed time periods within a single dimension, e.g. 2020-Q4 (quarter), 2021-06 (month), 2019-08-06 (day) | See Description     |

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
