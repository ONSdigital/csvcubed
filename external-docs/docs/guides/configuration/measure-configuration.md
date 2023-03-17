# Measure configuration

This section will cover how to define and configure measures in a cube configuration file. It will focus on the possible scenarios/ways a measure can be defined, as well as the fields that can be populated when doing so, providing examples for different fields and scenarios of creating measures. This section will not discuss how to define measure columns or a measure column's role in the context of a data cube's structure. For information on defining measure columns, see the [Measure column definition](Add link here when structure is implemented).

A measure can be defined and configured in two different ways: Either by attaching it inside an observation column's definition, or in a dedicated measures column of its own. The way a measure is defined and configured can highly depend on the shape of your data set, and whether there are multiple measures present or not.
For more information on defining observation columns, see the [observations columns](./columns/observations.md) page.
For more information on defining measures columns, see the [measures columns](./columns/measures.md) page.

### Defining measures by attaching them to observation columns

When there is only one measure present in the data set, or if an observation column only features one measure in its rows, then it is easiest to define the measure by attaching it to the observation column's definition. This is also how measures are to be defined in a pivoted shape data set, since each observation column naturally has their measures and units attached to them.

When defining a measure by attaching it to an observation column, the measure can be defined after specifying that the type of the column is `observations`. The measure is entered as an object field of the observation column definition, like shown in the example below:

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

This observation column definition is given a measure by creating an object where the keys are the fields of the measure component, and the values are the field contents. This measure has the label "Median commute time" and the description of "The median amount of time taken to commute, in minutes".

For more information on defining observation columns, and how to configure their different possible fields along with measures, see the [Observations page](./observations.md).

### Defining measures in a measure column

When creating a new measure column definition by specifying the `type` as "measures", the measure's field details are entered into a `values` object. Note this is different from how the measure details are given when giving the measure in an observation column, as measure columns contain references to discrete measures.

The following will describe the possible fields that can be entered into the `values` object when defining a new measure, providing some examples of those fields being used to define measures.

If basic measures are wanted without specifying measure details in the fields, the `values` field of the column definition can simply be set to True (as shown in the example below) which will indicate to csvcubed to create auto-configured measures unique to your data set.

```json
"columns": {
  "Measure column": {
    "type": "measures",
    "values": true
  }
}
```

A basic field for adding information to measures when creating a `values` object in new measure column definitions is the `label` field, which serves as the title of the measure. Note that this is optional if the measure is reusing or extending an existing column definition. (If the `from_existing` field is populated.)

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

Measure definition using the `from_existing` field can be done either by attaching the measure to an observation column, or by defining a measure within a measures column.

Defining a measure in an observation column, using an existing measure definition:

```json
   "Exports": {
      "type": "observations",
      "measure": {
            "from_existing": "http://example.com/measures/measure"
      }
   }
```

Defining a measure in an observation column, using an existing measure definition and overwriting the label:

```json
   "Exports": {
      "type": "observations",
      "measure": {
            "label": "New measure",
            "from_existing": "http://example.com/measures/measure"
      }
   }
```

Example of a measure created using the `from_existing` field in a measure column definition:

```json
"columns": {
   "type": "measures",
   "from_existing": "http://purl.org/linked-data/sdmx/2009/measure#refPeriod"
}
```

Another optional field that is used when defining a new measure is `definition_uri`. This is a URI that links to the definition of the resource being used.
TODO: Ask if this is required when the from_existing field is being used. Add an example showing it in use for a measure.

A point to remember about measures is that they must be accompanied by units, which represent in what intervals or units the observation is being measured in. Units can be defined by being attached to observations the same way that measures can when all observations in a column use the same measure/unit, or they can be defined in a dedicated units column. For more information on defining units, see the [configuring units](./units.md) page.
