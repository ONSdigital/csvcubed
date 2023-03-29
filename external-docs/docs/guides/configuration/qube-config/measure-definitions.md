# Measure definitions

This page discusses what a measure is, where one should be used, and how one can be defined and configured.

> For a table showing a measure's configuration options, see the [Reference table](#reference) at the bottom
> of this page.

## What is a measure?

 A *measure* describes the phenomenon that has been measured by the observed values of a data set.

 Consider the following data set. This small table contains its measures within a measures column.

| Year | Location | Value |        Measure |        Unit |
|:-----|:---------|------:|---------------:|------------:|
| 2019 | England  |   175 | Average Height | Centimetres |
| 2019 | England  |    85 | Average Weight |   Kilograms |
| 2021 | France   |   175 | Average Height | Centimetres |

This data set contains two different measures. The first observed value is measured using the measure `Average Height`,
and the second observed value uses the measure `Average Weight`. This is a common way measures are represented in a
standard shape data set.

## When to use measures

A data cube must have at least one measure to be considered valid.

The way a measure is defined and configured depends on the shape of your data set. A measure can be defined and
configured in two different ways: Either by attaching it inside an observations column's configuration as a property, or
in a dedicated measures column of its own.

For more information on defining observations columns, see the [observations columns](./columns/observations.md) page.
For more information on defining measures columns, see the [measures columns](./columns/measures.md) page.

## Basic configuration

This section will cover how to define measures in the two previously mentioned ways. Basic examples will be provided
that show the minimum required configuration to define a measure using each method.

### Defining measures by attaching them to observations columns

Measures can be defined inside an observations column to directly define what phenomenon is being measured. This is how
measures are to be defined in a pivoted shape data set, with each observations column having their measures attached to
them. Consider the following pivoted shape data set:

| Year | Location      | Average Height of Men |        Unit |
|:-----|:--------------|----------------------:|------------:|
| 2019 | Canada        |                    70 |      Inches |
| 2020 | United States |                    69 |      Inches |
| 2021 | England       |                   175 | Centimetres |

This data set does not contain a measures column. Instead, the measure is attached to the observations column, which in
this case is titled `Average Height of Men`.

When defining a measure by attaching it to an observations column, the measure can be defined after specifying that the
`type` of the column is `observations`. The measure is entered as a property of the observations column definition,
like shown in the example below:

```json
"columns": {
  "Average Height of Men": {
    "type": "observations",
    "measure": {
      "label": "Average Height of Men"
    }
  }
},
```

This observations column definition is given a measure by creating an object where the keys are the fields of the
measure component, and the values are the field contents. This measure has the label "Average Height of Men".

For more information on defining observations columns, and how to configure their different possible fields along with
measures, see the [Observations page](./columns/observations.md).

### Defining measures in a measures column

When creating a new measures column definition by specifying the `type` as "measures", the measure's details are
entered into a field named `values`. Note this is different from how the measure details are given when giving the
measure in an observations column, as measure columns contain references to discrete measures.

If basic measures are wanted without specifying measure properties in any fields, the `values` field of the column
definition can simply be set to `true` (as shown in the example below) which will indicate to csvcubed to automatically
generate measure definitions unique to your data set.

```json
"columns": {
  "Measures column": {
    "type": "measures",
    "values": true
  }
}
```

This is how measures would be defined in a standard shape data set, showing the most basic way to define a measure
within a dedicated measures column.

## Optional properties

This section will provide more detail on the different properties that can be provided when defining a measure, showing
examples of each of these properties being configured.

A basic field for adding information to measures when creating a `values` object in new measure column definitions is
the `label` field, which serves as a short-form title of the measure.

### Description

An optional field that can be used to give more detail to the measure is `description`. This is not required in any
scenario, but helps provide more information about the measure if wanted, in a longer free-text form that can go into
more detail than a label.

The following example shows a measure being created within a measures column, being given the `label` "Measure" and the
`description` "This is a measure".

### Measure column configuration example for a new measure

```json
"columns": {
  "Measure column": {
    "type": "measures",
    "values": [
      {
      "label": "Measure",
      "description": "This is a measure"
    }
    ]
  }
}
```

### Definition URI

Another optional field that is used when defining a new measure is `definition_uri`. This is a URI that links to the
definition of the resource being used.

A point to remember about measures is that they must be accompanied by units, which represent in what intervals or
units the observation is being measured in. Units can be defined by being attached to observations the same way that
measures can when all observations in a column use the same measure/unit, or they can be defined in a dedicated units
column. For more information on defining units, see the [unit definitions](./unit-definitions.md) page.

## Inheritance

 This section will show how to create measures by re-using existing definitions.

To reuse an existing measure definition, whether it is reused in its entirety as an exact copy of the existing
definition, or if it is used as a base to create a new measure upon, use the `from_existing` property.
This allows a URI to be used to apply an existing measure's definition.

When the `from_existing` field is used, specifying any other fields in the values object will override those fields of
the re-used measure's definition. This is how an existing definition can be used as a base to create new measures.

Measure definition using the `from_existing` field can be done either when attaching the measure to an observation
column, or when defining a measure within a measures column.

Defining a measure in an observations column, using an existing measure definition:

```json
   "Exports": {
      "type": "observations",
      "measure": {
            "from_existing": "http://example.com/measures/measure"
      }
   }
```

Defining a measure in an observations column, using an existing measure definition and overwriting the label:

```json
   "Exports": {
      "type": "observations",
      "measure": {
            "label": "New measure",
            "from_existing": "http://example.com/measures/measure"
      }
   }
```

This effectively means a new measure is created, using the existing measure as a base.

Example of a measure created using the `from_existing` field in a measures column definition:

```json
"columns": {
   "type": "measures",
   "from_existing": "http://purl.org/linked-data/sdmx/2009/measure#refPeriod"
}
```

## Reference

| **field name**   | **description**                                                                                                             | **default value** |
|------------------|-----------------------------------------------------------------------------------------------------------------------------|-------------------|
| `label`          | The title of the measure (Required; Optional if `from_existing` defined)                                                    | *none*            |
| `description`    | A description of the contents of the measure (Optional)                                                                     | *none*            |
| `from_existing`  | The URI of the resource for reuse/extension (Optional)                                                                      | *none*            |
| `definition_uri` | A URI of a resource to show how the measure is created/managed (e.g. a URI of a PDF explaining the measure type) (Optional) | *none*            |
