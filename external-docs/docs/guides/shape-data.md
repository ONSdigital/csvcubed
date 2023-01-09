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

