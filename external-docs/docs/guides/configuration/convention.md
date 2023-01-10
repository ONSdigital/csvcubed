# Configuration by convention

This page details the approach that csvcubed takes to configuring cubes by convention. This makes it possible to generate a valid CSV-W cube without writing a [qube-config.json](./qube-config.md) at all. For an introduction to this topic, see the [quick start on designing your CSV](../../quick-start/designing-csv.md).

## Minimum requirements

The configuration by conventional approach in csvcubed requires that:

* Your data set must be in the [standard data shape](../standard-shape.md). If your data set is in the [pivoted shape](../pivoted-shape.md), you **must** provide a [qube-config.json](./qube-config.md).
* The data CSV's column titles use [conventional column names](#conventional-column-names) for [measure](../../glossary/index.md#measure) columns, [unit](../../glossary/index.md#unit) columns and [observed value](../../glossary/index.md#observation-observed-value) columns.

Adhering to the [conventional column names](#conventional-column-names) is important since csvcubed uses those to understand what each column in your data set contains.

## Inferred configuration

In order to generate a cube, csvcubed needs some additional metadata and makes a few inferences to ensure it has all of the information it needs:

* The title of the cube is the name of the csv file in [title case](https://en.wikipedia.org/wiki/Title_case) with underscores or dashes replaced by spaces.
* Every column which does not use a conventional name is interpreted as a [dimension](../../glossary/index.md#dimension).
    * The title of each dimension is the [title case](https://en.wikipedia.org/wiki/Title_case) version of the column header with any underscores or dashes replaced by spaces.
    * A code list is generated for each dimension column. This code list is generated from the unique values present in the data CSV column.
* Observation values are decimal values.
* New measures are created using the unique values in the measures column unless a URI is present, where that uri is assumed to point to an existing measure.
* New units are created using the unique values in the units column unless a URI is present, where that uri is assumed to point to an existing unit.

## Conventional column names

The following table defines the conventional column names understood by csvcubed:

| Component type                                                           | Reserved names                                                                  | Resulting configuration                                                                                                                                                                         |
|--------------------------------------------------------------------------|---------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [Dimension](../../glossary/index.md#dimension)                           | none                                                                            | A new dimension with the label of the csv column as its title                                                                                                                                   |
| [Measure](../../glossary/index.md#measure) Column                        | Measure, measures, measures column, measure column, measure type, measure types | A new measure column with the values within the measure column as new measures unless the values are uris, when csvcubed will assume these are existing measures                                |
| [Observation](../../glossary/index.md#observation-observed-value) Column | Observations, obs, values, value, val, vals                                     | A new observation column with the values in this column; the data type of this column must be numeric and is assumed to be of type [xsd:decimal](https://www.w3.org/TR/xmlschema11-2/#decimal). |
| [Unit](../../glossary/index.md#unit) Column                              | Unit, units, units column, unit column, unit type, unit types                   | A new unit column with the values within the unit column as new units unless the values are uris, when csvcubed will assume these are existing units                                            |

A valid configuration by convention cube must have a column of each *component type* to be valid. It is possible to override the default configuration of a conventional column by [writing a column definition](qube-config.md#column-definitions) in a [qube-config.json](qube-config.md) file.
