# Measure configuration

This section will cover how to define and configure measures in a cube configuration file. It will focus on the possible scenarios/ways a measure can be defined, as well as the fields that can be populated when doing so, providing examples for different fields and scenarios of creating measures. This section will not discuss how to define measure columns or a measure column's role in the context of a data cube's structure. For information on defining measure columns, see the [Measure column definition](Add link here when structure is implemented). For a simpler quick tabular look at what fields can be used to configure a measure, see the [measure fields table](TODO) at the bottom of this page.

A measure can be defined and configured in two different ways: Either by attaching it inside an observation column's definition, or in a dedicated measures column of its own. When attaching a measure to an observation column, the measure can be defined after specifying that the type of the column is `observations`. The measure is entered as an object attached to the observation column definition, like shown in the example below:

### Measure configuration example in an Observation column field:

This observation column definition is given a measure by creating an object where the keys are the fields of the measure component, and the values are the field contents. This measure has the label "Median commute time" and the description of "The median amount of time taken to commute, in minutes".

```json
"columns": {
  "Median commute time / mins": {
    "type": "observations",
    "measure": {
      "label": "Median commute time",
      "description": "The median amount of time taken to commute, in minutes"
    }
  }
},
```

When creating a new measure column definition by specifying the `type` as "measures", the measure's field details are entered into a `values` object. Note this is different from how the measure details are given when giving the measure in an observation column.

The following will describe the possible fields that can be entered into the `values` object when defining a new measure, providing some examples of those fields being used to define measures.

If basic measures are wanted without specifying measure details in the fields, the `values` field of the column definition can simply be set to True (as shown in the example below) which will indicate to csvcubed to create auto-configured measures unique to your data set.

TODO: Should we include a larger example with more columns and maybe some metadata when starting out? Then narrow down focus of examples later.
```json
"columns": {
  "Measure column": {
    "type": "measures",
    "values": true
  }
}
```

A basic field for adding information when creating a `values` object in new measure column definitions is the `label` field, which serves as the title of the measure. Note that this is optional if the measure is reusing or extending an existing column definition. (If the `from_existing` field is populated.)

An optional field that can be used to give more detail to the measure is `description`. This is not required in any scenario, but helps provide more information about the measure if wanted, in a longer free-text form that can go into more detail than a label.

### Measure column configuration example for a new measure:

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

To reuse an existing measure definition, whether it is reused in its entirety as an exact copy of the existing definition, or if it is used as a base to create a new measure upon, the `from_existing` field allows a URI to be given to apply an existing measure's definition (and therefore all its details) to this column. When this is done, specifying any other fields in the values object such as `label` or `description` will overwrite those fields of the existing column definition. This is how an existing definition can be used as a base to create new measures.

Measure configuration using the `from_existing` field can be done either by attaching the measure to an observation column, or by defining a measures column.

### Defining a measure in an observation column, using an existing measure definition:
```json
   "Exports": {
      "type": "observations",
      "measure": {
            "from_existing": "http://example.com/measures/measure"
      }
   }
```

### Defining a measure in an observation column, using an existing measure definition and overwriting the label:
```json
   "Exports": {
      "type": "observations",
      "measure": {
            "label": "New measure",
            "from_existing": "http://example.com/measures/measure"
      }
   }
```

### Example of a measure created using the `from_existing` field in a measure column definition:
```json
"columns": {
   "type": "measures",
   "from_existing": "http://purl.org/linked-data/sdmx/2009/measure#refPeriod"
}
```

Another optional field that is used when defining a new measure is `definition_uri`. This is a URI that links to the definition of the resource being used.
TODO: Ask if this is required when the from_existing field is being used. Add an example showing it in use for a measure.

A point to remember about measures is that they must be accompanied by units, which represent in what intervals or units the observation is being measured in. Units can be defined by being attached to observations the same way that measures can when all observations in a column use the same measure/unit, or they can be defined in a dedicated units column. For more information on defining units, see the [configuring units](./units.md) page.
## Measures columns

 This section will focus on defining measure columns, the possible configurations with single and multiple measure data sets, and their presence in the structure of a cube configuration file. This page will avoid going into full detail on creating and configuring the measures themselves.

The *measure* column defines the phenomenon that is being observed, what is being quantified in this observation. In this way it is similar to a dimension. At least one measure is required to be defined in a data cube for it to be valid. Measures can either be attached to a Measure Column if there are multiple different measures appearing in columns throughout your data set, or to an Observation column's `measure` field if all observations in this column of the data set use the same measure.

For more information on defining measures, and populating a measure's fields in a cube configuration, please see the [Measures Configuration](#measures-configuration) TODO fix this link when the structure of the guide is determined and all the pages exist.

An important point to remember about measure columns is that they are only supported in a standard shape data set. This is because measures in pivoted shape data sets are defined by being attached to the observation columns they appear in, whereas in the standard shape, each row must specify the measure and unit being used for that row's observation, meaning a measure column is needed.

To define a measure column, specify the column's `type` field as "measures", like so:
TODO: Make this example bigger so there is more context about the structure in which the measure column definition appears in.

```json
"columns": {
   "type": "measures",
   "values": true
}
```

When defining a measure column, the contents of the column are specified in a list of objects which is passed into a field named `values`. For now, as this page will not go into detail on configuring individual measures, the example simply populates the column with "values": true, which indicates to csvcubed to create auto-configured measures unique to your data set.

One of the advantages of defining measure columns in this way in standard shape data sets is that no changes are required in the cube configuration file if new measures are added. Using multiple measures in a measure column simply means adding new rows to the data set, and specifying measures (and units) to be used for the observation. To view more information on the difference between single measure and multi measure data sets, see the standard shape section of [Shape your data](../shape-data/standard-shape.md)

## Measure definitions

This table shows a list of the possible fields that can be entered when configuring a measure.

| **field name**   | **description**                                                                                                             | **default value** |
|------------------|-----------------------------------------------------------------------------------------------------------------------------|-------------------|
| `label`          | The title of the measure (Required; Optional if `from_existing` defined)                                                    | *none*            |
| `description`    | A description of the contents of the measure (Optional)                                                                     | *none*            |
| `from_existing`  | The uri of the resource for reuse/extension (Optional)                                                                      | *none*            |
| `definition_uri` | A uri of a resource to show how the measure is created/managed (e.g. a uri of a PDF explaining the measure type) (Optional) | *none*            |
