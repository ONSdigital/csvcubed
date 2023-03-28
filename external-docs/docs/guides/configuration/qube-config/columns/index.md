# Column definitions

A CSV-W file provides detailed information about the columns beyond their values. In csvcubed, we are targeting a level of detail which results in a data cube which can be expressed using W3C's [RDF Cube Vocabulary](https://www.w3.org/TR/vocab-data-cube/). In order to be valid, a data cube must have at least one dimension, at least one observations column, along with at least one defined unit and measure per observations column. A cube may also have one or more attribute columns which provide clarification to observational data. Units and measures may be attached to the [observations column](#observations), or appear in a [measure column](#measures) or [unit column](#units) of their own.

To define a column in a `qube-config.json` file, provide the column title as a JSON object key, and create a new JSON object containing the column's configuration details.

```json
{ ...
  "columns": {
    "Column title": {
      "Column configuration option 1": "Column configuration value 1",
      "Column configuration option 2": "Column configuration value 2",
      "Column configuration option 3": "Column configuration value 3"
      ...
    }
  }
}
```

A column is assumed to be a dimension unless otherwise configured using the `type` key or the column title is one of the [reserved names](../../../configuration/convention.md#conventional-column-names). A dimension can still have a `"type": "dimension"` key/value pair.

<!-- TODO Add some metadata to examples and links to json/csv files -->

```json
{
  "title": "Example qube-config.json",
  "description": "This is an example of a qube-config.json file",
  "publisher": "https://www.gov.uk/government/organisations/office-for-national-statistics",
  "columns": {
    "Example column": {
      "type": "dimension",
      ...
    }
  }
}
```

**If a column mapping is not defined in the `qube-config.json` file for a given CSV column, the column is [configured by convention](../../convention.md).**  To ignore a column and not configure it, set the column's value to `false`. This will ensure the column will not be recognised as part of the cube by csvcubed.

```json
{ ...
  "columns": {
    "Suppressed column": false
  }
}
```

Brief descriptions of the five column types are given below. For more information on each type, and to see configuration examples, click on the section header.

## [Dimensions](./dimensions.md#dimension-configuration)

*Dimension* columns serve to identify observations in the data set. A combined set of values for all dimension components (including measures) should uniquely identify a single observation value. Examples of dimensions include the time period to which the observation applies, or the geographic region which the observation covers. Think of the principle of [MECE](https://en.wikipedia.org/wiki/MECE_principle).

## [Observations](./observations.md#observation-configuration)

*Observation* columns contain the numerical values of observations recorded in the data set.

## [Measures](./measures.md#measure-configuration)

*Measure* columns represent the phenomenon being observed, and are effectively another form of dimension.

## [Units](./units.md#unit-configuration)

*Unit* columns are a type of attribute column which provide the units of the observation.

## [Attributes](./attributes/index.md#attribute-configuration)

*Attribute* columns allow us to qualify and interpret observed values. This enables specification of units of measure, any scaling factors and metadata such as the status of the observation (e.g. *estimated*, *provisional*). Attributes can either be [resources](../../../../glossary/index.md#resource) or [literals](../../../../glossary/index.md#literal).
