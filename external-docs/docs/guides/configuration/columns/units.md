# Unit configuration

This section will describe the cube component of units, and explain how to define and configure units in a data cube. The section will also show the different fields that can be input to populate a unit, as well as examples of those fields being used in some example unit definitions.

The *units* of a data set represent how the measured quantity is being counted or incremented, defining what unit of measurement is being used to measure this observation. At least one unit is required to be defined in a data cube for it to be valid.

Depending on how units are used (or how exactly observations are counted) in your data set, and on your data set's shape in general, there will be differences in the way your units could be defined. One scenario is where all observations in a column use the same unit to measure observations, then the unit can be defined by being attached to the observation column's definition. If different observations in your data set use different units, then units should be created in their own column definition. In a pivoted shape data set, units are naturally attached to their corresponding observations, and are therefore defined in the observation column definition. The examples below will go into further detail on the different ways to define and configure units, showing examples of different scenarios.

Similarly to measures, units can be defined by attaching them to an observation column. After specifying the type of the column as "observations", a unit can be created as a field containing an object, where the keys are the fields of the unit itself, and the values are the contents of the fields. The example below shows an observation column definition with a measure labelled "People on stage" and a unit with the label "Number", label being the key, and "Number" being the value.

### Unit configuration example in an observation column field (single unit).

```json
"columns": {
  "Median commute time / mins": {
    "type": "observations",
    "measure": {
      "label": "People on Stage"
    },
    "unit": {
      "label": "Number"
    }
  }
},
```

A different scenario for creating units is when you want to display them in their own column. This should be done in a standard shape cube setting, when there are multiple units to be used throughout different observations.
When defining a new unit in its own column, the details are specified in the `values` field as an object, after the type of the column is specified as "units". The contents that can be entered within the values object will be described with examples.

This unit column definition has a label, "Pounds Sterling (£), Millions" and a description, "Millions of Pounds Sterling (GBP, £).". These fields add more detail to the unit, the label being a short form title for the unit, and the description being a more in-depth, long-form text description of the title.
### New Units configuration example:

```json
  "columns": {
      "Unit": {
          "type": "units",
          "values": [
              {
                  "label": "Pounds Sterling (£), Millions",
                  "description": "Millions of Pounds Sterling (GBP, £)."
              }
          ]
      }
  }
```

When defining a column using an existing unit definition, the `from_existing` field is used within the values object. Enter a URI of the resource being used as the value into the `from_existing` field to create the definition.

### Creating a units column definition using the `from_existing` field:

```json
    "columns": {
        "Unit": {
            "type": "units",
            "values": [
                {
                    "from_existing": "http://qudt.org/vocab/unit/PoundSterling",
                    "quantity_kind": "http://qudt.org/vocab/quantitykind/Currency",
                }
            ]
          }
        }
```

The way the unit is used in the data set, such as the way amounts are being displayed, or how things are being counted, can determine whether a `scaling_factor` field should be used. Using the scaling factor means a new unit is being defined using the `from_existing` field's value as a base, and altering it so the measurements made are scaled as specified in a base 10 expression. For example, a unit defined with an existing base of Pounds Sterling, could be given a scaling factor of 1000000 to create the unit "Millions of Pounds Sterling" (where 1 would mean 1 million pounds.)

### Creating a units column using the `from_existing` field, also using a scaling factor and specifying quantity kind for the existing unit being used.
```json
    "columns": {
        "Unit": {
            "type": "units",
            "values": [
                {
                    "label": "Pounds Sterling (£), Millions",
                    "from_existing": "http://qudt.org/vocab/unit/PoundSterling",
                    "quantity_kind": "http://qudt.org/vocab/quantitykind/Currency",
                    "scaling_factor": 1000000,
                    "description": "Millions of Pounds Sterling (£)."
                }
            ]
          }
        }
```

TODO: Improve si_scaling_factor description
Another optional form of scaling that can be applied to units in column definitions is `si_scaling_factor`. The purpose of this field in the values dictionary is to relate scaled units to other units that are relevant, creating consistency within their scale. Most of the units that are related in this sense are already defined. Note that this is an advanced feature and can safely be ignored if not needed.

The `quantity_kind` field can make use of the QUDT extensive various types of measurable quantities to help group and identify units. Provide a URI of a valid resource, adding it onto the prefix http://qudt.org/vocab/quantitykind/ to take advantage of QUDT's vast library of quantity kind resources.
For a dedicated page with more information on defining units, see [configuring units](./configuring-units.md).

When creating a units column, it is also possible to specify an observation value to associate the units with, by entering the observation value into the `describes_observations` field. This is (only) necessary to associate a unit to its relevant observation value when there are multiple measures and the data set is in the pivoted shape, and there are multiple observation values, as otherwise there would be no clear link between the unit being used for different observations in columns. For more information on the distinction between pivoted/standard shape data sets, as well as single/multiple measures, see the [Pivoted Shape](../shape-data/pivoted-shape) TODO: Fix this link to the pivoted shape page when the location of the new guide page is decided.

### Example of a units column being defined with the `describes_obserations` field used to link to an observation.

Here is an observation that the unit will describe:
```json
        "Exports": {
            "type": "observations",
            "measure": {
                "label": "Exports Monetary Value",
                "from_existing": "http://example.com/measures/monetary-value"
            }
        }
```

And here is the unit, showing the use of the `describes_observations` field:

```json
        "Exports Unit": {
            "type": "units",
            "describes_observations": "Exports"
        }
```

## Units columns

This section will focus on the configuration of units columns, their presence in the structure of a cube config file, and how their application can vary depending on the shape of the data set, or the number of units. The configuration of units themselves will not be the primary focus of this section. For more information on defining and configuring units, with examples, see the [configuring units](./units.md) page.

The *units* column represents how the measured quantity is being counted or incremented, defining what unit of measurement is being used to measure this observation. At least one unit is required to be defined in a data cube for it to be valid.

In a configuration file, the unit column is a form of attribute column. This means they share similarities to configure, sharing all of the attribute column’s configuration options, but with some additional options unique to units.

However, defining unit columns is also quite different to other components such as dimensions, observations and attributes, as unit column definitions contain references to discrete units. To define a unit column, specify the `type` field of the column definition as "units". An example of a cube configuration containing a unit column definition is shown below:

TODO: Make this example bigger so there is more context about the structure in which a unit column definition appears in:

```json
"columns": {
   "type": "units",
   "values": true
}
```

The unit column should contain a "values" object. This object can be filled in with the fields that are used to populate a unit. As this section will not focus on how to define units, for now, this unit column's "values" object simply contains "true". This indicates to csvcubed to generate auto-configured units unique to your data set, and is essentially intended used when basic units are wanted and you are not filling in the unit contents of the column manually.

A point to remember about unit columns is that they are only required to be defined in a standard shape data set, where each row has to specify what unit is being used to measure that row's observation. This is in contrast to the pivoted shape, where units are attached to the observation column they are used in and unit columns are not necessary. For more information on the differences between standard and pivoted shape data sets, as well as some examples, see the [Standard shape](../shape-data/standard-shape.md) and [Pivoted shape](../shape-data/pivoted-shape.md) sections of the Shape your data documentation.

## Unit definitions

This table shows the possible fields that can be provided when defining a unit. The use of many of these fields is optional and depends on how your unit is defined and used.

| **field name**      | **description**                                                                                                                                                                                         | **default value** |
|---------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------|
| `label`             | The title of the unit (Required; Optional if `from_existing` defined)                                                                                                                                   | *none*            |
| `description`       | A description of the contents of the unit (Optional)                                                                                                                                                    | *none*            |
| `from_existing`     | The uri of the resource for reuse/extension (Optional)                                                                                                                                                  | *none*            |
| `definition_uri`    | A uri of a resource to show how the unit is created/managed (e.g. a uri of a image which shows the formula on how the unit is derived) (Optional)                                                       | *none*            |
| `scaling_factor`    | The scaling factor (expressed in base 10) is used to define a new unit from an existing base (i.e. "GBP millions" would have a form_existing unit of GBP, and a `"scaling_factor": 1000000`) (Optional) | *none*            |
| `si_scaling_factor` | The si_scaling_factor helps relate common scaled units to source SI units, for example kilograms are 1000 grams. Most of these units are already defined. (Optional) (Advanced)                         | *none*            |
| `quantity_kind`     | The [QUDT quantity kind](http://www.qudt.org/doc/DOC_VOCAB-QUANTITY-KINDS.html#Instances) helps group units                                                                                             | *none*            |
