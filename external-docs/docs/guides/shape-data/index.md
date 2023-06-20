# Shaping your data

> This page introduces the input data shapes supported by csvcubed with the aim of helping you understand which to use and how to generate data in the right shape.

csvcubed requires that all CSV data inputs are provided in one of two specialised forms of [tidy data](../../glossary/index.md#tidy-data):

* the [standard approach](./standard-shape.md) - the recommended shape for [sparse](../../glossary/index.md#sparse-data) multi-measure data cubes.
* the [pivoted approach](./pivoted-shape.md) - the recommended shape for [dense](../../glossary/index.md#dense-data) data cubes.

These two shapes share a number of similarities in how they require data to be structured; this is explored in the [common structure](#common-structure) section. Examples of [standard shape](#standard-shape) and [pivoted shape](#pivoted-shape) data sets are also presented below.

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
    * the `Status` _attribute_ column contains information describing the status of the observed value itself.
    * Note that _attributes_ should only describe the observed value and must not be used to identify any subset of the population.

## Standard Shape

Examples of single measure and multiple measure **standard** shape data sets are below. More detailed configuration instructions can be found in the [standard shape](./standard-shape.md) section. See [Converting to standard shape](./shape-conversion.md#converting-to-the-standard-shape) for instructions on how to convert the shape of your data in Python and R.

### Single Measure

In this example, the single measure observed is `Count of Arthur's Bakes` and the corresponding unit is `Number`.

| Year | Location  | Value |      Status |                 Measure |   Unit |
|:-----|:----------|------:|------------:|------------------------:|-------:|
| 2022 | London    |    35 | Provisional | Count of Arthur's Bakes | Number |
| 2021 | Cardiff   |    26 |       Final | Count of Arthur's Bakes | Number |
| 2020 | Edinburgh |    90 |       Final | Count of Arthur's Bakes | Number |
| 2021 | Belfast   |     0 |       Final | Count of Arthur's Bakes | Number |

### Multiple Measures

In this example, there are two measures recorded - `Count of Arthur's Bakes` and `Revenue`. The corresponding units are `Number` and `GBP Sterling, Millions` respectively.

| Year | Location | Value |      Status |                 Measure |                   Unit |
|:-----|:---------|------:|------------:|------------------------:|-----------------------:|
| 2022 | London   |    35 | Provisional | Count of Arthur's Bakes |                 Number |
| 2022 | London   |    25 | Provisional |                 Revenue | GBP Sterling, Millions |
| 2021 | Cardiff  |    26 |       Final | Count of Arthur's Bakes |                 Number |
| 2021 | Cardiff  |    18 |       Final |                 Revenue | GBP Sterling, Millions |

## Pivoted Shape

Examples of single measure and multiple measure **pivoted** shape data sets are below. More detailed configuration instructions can be found in the [pivoted shape](./pivoted-shape.md) section. See [Converting to pivoted shape](./shape-conversion.md#converting-to-the-pivoted-shape) for instructions on how to convert the shape of your data in Python and R.

### Single Measure

In this example, the single measure recorded is `Count of Arthur's Bakes`.

| Year | Location  | Count of Arthur's Bakes | Status      |
|:-----|:----------|------------------------:|:------------|
| 2022 | London    |                      35 | Provisional |
| 2021 | Cardiff   |                      26 | Final       |
| 2020 | Edinburgh |                      90 | Final       |
| 2021 | Belfast   |                       0 | Final       |

### Multiple Measures

In this example, there are two measures recorded - `Count of Arthur's Bakes` and `Revenue`.

| Year | Location | Count of Arthur's Bakes | Count of Stores Status | Revenue | Revenue Units  | Revenue Status |
|:-----|:---------|------------------------:|:-----------------------|--------:|:---------------|:---------------|
| 2022 | London   |                      35 | Provisional            |      25 | GBP (Sterling) | Provisional    |
| 2021 | Cardiff  |                      26 | Final                  |      18 | GBP (Sterling) | Final          |
