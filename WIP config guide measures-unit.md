## Measures and Units

Measures can either be attached to a Measure Column if there are multiple different measures in your data set, or to an Observation column's `measure` field if all observations in the cube have the same measure.
Units can either be attached to a Unit Column if there are a mixture of units in your data set, or to an Observation column if all observations in the cube have the same unit.
The definition of measures and units is similar in that it depends on the number of measures/units present in the data set. If only one measure/unit is present, then the measure/unit can be defined by being attached to the Observation column, by entering them into their own field in the Observation column's definition. When multiple measures/units are present in the data set, they can be defined in their own column so that the column may clearly show which of the possible measures is being counted, or which unit is being used to measure each value in observations.

## Measure and Unit Columns Configuration

Measure and unit columns are treated slightly differently to dimension, attribute, and observation columns. Measure and unit columns contain references to discrete units and measures. In both cases by defining `"type": "measures"` or `"type": "units"` provides the same behaviour. Do not put measures in unit columns or units in measure columns.

Measure and unit columns share some fields in that they can be populated directly in the column's definition with the `values` field, allowing a dictionary to be input that defines the units/measures. Existing column definitions can also be reused to quickly define measures and units, or serve as a "base" for a new column to be created on.

TODO: Find out if cell_uri_template in measures/units has any distinctions compared to when it is used as a field in other column definitions.

When creating a units column, it is also possible to specify an observation value to associate the units with, by entering the observation value into the `describes_observations` field. This is (only) necessary to associate a unit to its relevant observation value when there are multiple measures and the data set is in the pivoted shape, and there are multiple observation values, as otherwise there would be no clear link between the two. For more information on the distinction between pivoted/standard shape data sets, as well as single/multiple measures, see the [Pivoted Shape](../shape-data/pivoted-shape) TODO: Fix this link to the pivoted shape page when the location of the new guide page is decided.


| **field name**           | **description**                                                                                                                                                                                                                                                                                                  | **default value** |
|--------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------|
| `type`                   | The type of the column, provide `"measures"` for the measure column type or `"units"` for the unit column (Required)                                                                                                                                                                                             | *dimension*       |
| `values`                 | (New Measures/Units only) If basic units/measures are desired, a boolean value of `true` is used to signify to csvcubed to create units/measures from values in this column; otherwise values is a dictionary which defines the units/measures using the notation from [Measures and Units](#measures-and-units) | `true`            |
| `from_template`          | (Existing Units only) Use a [column template](templates.md)                                                                                                                                                                                                                                                      | *none*            |
| `cell_uri_template`      | (Existing Measures/Units only) Used to define a template to map the cell values in this column to URIs                                                                                                                                                                                                           | *none*            |
| `describes_observations` | (Unit column only) Associates the unit column with the relevant observation values. This is only necessary for [pivoted shape data sets](../shape-data/pivoted-shape.md) with multiple observation value columns.                                                                                                | *none*            |

### Measures

The *measure* column defines the phenomenon that is being observed, what is being quantified in this observation. In this way it is similar to a dimension. At least one measure is required to be defined in a data cube for it to be valid.

### Measures Configuration

Before defining measures for the configuration, it is important to know if there are multiple measures in the data set, or if all observations in the data set use the same measure.
If there is only one measure that is being applied to all observations in the data set, then the measure can be attached to the optional field of the Observation column’s configuration. A measure defined in this field can either be a URI linking to an existing dimension, or a dictionary to define a new measure (or extend an existing one).

When creating a new measure column definition, the field details are entered into a `values` dictionary, which appears like so in the column definition:
```json
"columns": {
  "Measure column": {
    "type": "measures",
    "values": {

    }
  }
}
```

The following will describe the possible fields that can be entered into the `values` dictionary when defining a new measure.

If basic measures are wanted, the `value` field can simply be set to True which will indicate to csvcubed to create a measures column from this definition.
A basic, required field for all new measure column definitions is the `label` field, which serves as the title of the measure. Note that this is optional if the measure is reusing or extending an existing column definition. (If the `from_existing` field is populated.)

An optional field that can be used to give more detail to the measure is `description`. This is not required in any scenario, but helps provide more information about the measure if wanted, in a longer free-text form that can go into more detail than a label.

To reuse an existing measure column definition, whether it is reused in its entirety as an exact copy of the existing definition, or if it is used as a base to create a new column definition upon, the `from_existing` field allows a URI to be given to apply an existing column's definition (and therefore all its details) to this column. When this is done, specifying any other fields in the values dictionary such as `label` or `description` will overwrite those fields of the existing column definition. This is how an existing column definition can be used as a base to create new measures.

Another optional field that is used when defining a new measure is `definition_uri`. This is a URI that links to the definition of the resource being used.
TODO: Ask if this is required when the from_existing field is being used.

The table below shows the fields that can be provided to a measure column's definition.

| **field name**   | **description**                                                                                                             | **default value** |
|------------------|-----------------------------------------------------------------------------------------------------------------------------|-------------------|
| `label`          | The title of the measure (Required; Optional if `from_existing` defined)                                                    | *none*            |
| `description`    | A description of the contents of the measure (Optional)                                                                     | *none*            |
| `from_existing`  | The uri of the resource for reuse/extension (Optional)                                                                      | *none*            |
| `definition_uri` | A uri of a resource to show how the measure is created/managed (i.e. a uri of a PDF explaining the measure type) (Optional) | *none*            |

### WIP Measure configuration example in an Observation column field(Single measure):

note: making up these json column definitions for now when the Eurovision data set doesn't really match.

```json
"columns": {
  "Median commute time / mins": {
    "type": "observations",
    "measure": {
      "label": "Final Rank"
    }
  }
},
```

### Measure column configuration example for a new measure:

```json
"columns": {
  "Measure column": {
    "type": "measures",
    "values": {
      "label": "Measure",
      "description": "This is a measure"
    }
  }
}
```

### Units

The *units* column is how the measured quantity is being counted or incremented, defining what unit of measurement is being used to measure this observation. At least one unit is required to be defined in a data cube for it to be valid.

### Units Configuration

In a config file, the unit column is a form of attribute column. This means it is similar to configure, sharing all of the attribute column’s configuration options, but with some additional options unique to units.
Configuration of units columns shares a theme with measure columns, where if the data set only features one unit, then that unit can be defined in the observation column’s optional unit field. However, if the data set contains multiple different units, a units column is required to specify which unit applies to each observation.

When defining a new unit, the details are specified in the `values` field as another dictionary, after the type of the column is declared as a unit. The contents entered within the values dictionary must at least be a label, acting as the title of the unit, and optionally a description.
When defining a column using an existing unit definition, the `from_existing` field is used within the values dictionary. Enter a URI of the resource being used as the value into the `from_existing` field to create the definition.
The way the unit is used in the data set, such as the amounts being displayed, can determine whether a `scaling_factor` field should be used. Using the scaling factor means a new unit is being defined using the `from_existing` field's value as a base, and altering it so the measurements made are scaled as specified in a base 10 expression. For example, a unit defined with an existing base of Pounds Sterling, could be given a scaling factor of 1000000 to create the unit "Millions of Pounds Sterling" (where 1 would mean 1 million pounds.)
Another optional form of scaling that can be applied to units in column definitions is `si_scaling_factor`. The purpose of this field in the values dictionary is to relate scaled units to other units that are related, creating consistency within their scale. Most of the units that are related in this sense are already defined. Note that this is an advanced feature and can safely be ignored if not needed.
The `quantity_kind` field can make use of the QUDT extensive number of various types of measurable quantities to help group and identify units. Provide a URI of a valid resource, adding it onto the prefix http://qudt.org/vocab/quantitykind/ to take advantage of QUDT's vast library of quantity kind resources.
For a dedicated page with more information on defining units, see [configuring units](./units.md).

The table below shows the fields that can be specified in a unit column's definition.

| **field name**      | **description**                                                                                                                                                                                         | **default value** |
|---------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------|
| `label`             | The title of the unit (Required; Optional if `from_existing` defined)                                                                                                                                   | *none*            |
| `description`       | A description of the contents of the unit (Optional)                                                                                                                                                    | *none*            |
| `from_existing`     | The uri of the resource for reuse/extension (Optional)                                                                                                                                                  | *none*            |
| `definition_uri`    | A uri of a resource to show how the unit is created/managed (i.e. a uri of a image which shows the formula on how the unit is derived) (Optional)                                                       | *none*            |
| `scaling_factor`    | The scaling factor (expressed in base 10) is used to define a new unit from an existing base (i.e. "GBP millions" would have a from_existing unit of GBP, and a `"scaling_factor": 1000000`) (Optional) | *none*            |
| `si_scaling_factor` | The si_scaling_factor helps relate common scaled units to source SI units, for example kilograms are 1000 grams. Most of these units are already defined. (Optional) (Advanced)                         | *none*            |
| `quantity_kind`     | The [QUDT quantity kind](http://www.qudt.org/doc/DOC_VOCAB-QUANTITY-KINDS.html#Instances) helps group units                                                                                             | *none*            |


### Unit configuration example in an observation column field (single unit).

```json
"columns": {
  "Median commute time / mins": {
    "type": "observations",
    "measure": {
      "label": "People on Stage"
    },
    "unit": "Number"
  }
},
```

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

### Creating a units column using the `from_existing` field, also using scaling and specifying quantity kind.
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

### Perhaps an example for new units in a pivoted shape with multiple obs val columns, to show the "describes_observations" field?
