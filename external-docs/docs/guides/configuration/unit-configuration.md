# Unit configuration

This page discusses what a unit is, where one should be used, and how one can be defined and configured.

The configuration of units columns will not be the primary focus of this page. For help with this, see the
[Units columns](./columns/units.md) page.

> For a detailed look at a unit's configuration options, see the [Reference table](#reference) at the bottom
> of this page.

## What is a unit?

The *units* of a data set represent what unit has been used to measure an observed value in a data set.

Consider the following data set. It is a small table showing the use of units in a cube.

The following is an example of a small data set containing a units column:

| Year | Location      | Average Height of Men |        Unit |
|:-----|:--------------|----------------------:|------------:|
| 2019 | Canada        |                    70 |      Inches |
| 2020 | United States |                    69 |      Inches |
| 2021 | England       |                   175 | Centimetres |

In this case, the units are contained within their own units column. The observations in this data set are measured
using two units: `Inches` for the first two observed values, and `Centimetres` for the third.

## When to use units

A data cube must have at least one unit defined to be considered valid.

Measures can be defined and configured in two different ways. The method you should use depends on how units are used
in your data set.

If an observations column in your cube uses the same unit for all observation values, then the unit should be defined
and configured as part of that observations column's definition.

If multiple units appear in different observations within the same observations column, then units should be defined
and configured in a dedicated units column.

csvcubed automatically defines new units using the unique values in your
[standard shape](../shape-data/standard-shape.md) cube's units column. If desired, you can gain more control over how
the units are defined by providing configuration in a [qube-config.json](./qube-config.md) file.

Note that the two scenarios described above apply to both standard and pivoted shape cubes. The shape of the data cube
does not affect the representation of units.

### Defining a unit in an observation column's definition

After specifying the `type` of the column as `observations`, a unit can be created as a property containing a list of
objects, these objects being the fields that contain the unit's properties.

The example below shows an observation column definition with a unit. The unit has been given the `label` "Count".

```json
"columns": {
    "Number of Arthur's Bakes": {
        "type": "observations",
        "unit": {
            "label": "Count"
        },
    }
},
```

For more information on defining observation columns, and the resources that can be configured in them along with units,
 see the [observations columns](../configuration/columns/observations.md) page.

### Defining a unit in a units column

Placing the units in their own column should be done when different values in the same observation column are measured
differently, e.g. one row measured in US Dollars and the next row measured in Pounds Sterling.

When defining a new unit in its own column, the details are specified in the `values` field as an object, after the
`type` of the column is specified as "units".

This example data set contains a single unit, "Pounds Sterling (£), Millions"

| Location     | Value |                           Measure |                          Unit |
|:-------------|------:|----------------------------------:|------------------------------:|
| Biscuitburgh |    31 | Annual Income (Gross Value Added) | Pounds Sterling (£), Millions |

And the json configuration of the unit column containing the unit could look like this:

```json
{
    "$schema": "https://purl.org/csv-cubed/qube-config/v1",
    "columns": {
        "Unit": {
            "type": "units",
            "values": [
                {
                    "label": "Pounds Sterling (£), Millions",
                }
            ]
        }
    }
}
```

This unit's definition has a label, "Pounds Sterling (£), Millions" and a description,
"Millions of Pounds Sterling (GBP, £).". These fields add more detail to the unit, the label being a short form title
for the unit, and the description being a more in-depth, long-form text description of the title.

## Optional properties

This section will further explore the properties of units, showing examples of the possible fields that can be entered
when configuring a unit.

### Description

The previous section showed the use of a `label`, which serves as a short form title for the unit. Another way to add
more detail to the unit's definition is the `description` field. This is a long form text description that can give
further information about the unit. The JSON below shows a previously used example of a unit configuration in a units
column, this time using a description:

```json
{
    "$schema": "https://purl.org/csv-cubed/qube-config/v1",
    "columns": {
        "Unit": {
            "type": "units",
            "values": [
                {
                    "label": "Pounds Sterling (£), Millions",
                    "description": "Pounds Sterling (£) counted per million."
                }
            ]
        }
    }
}
```

### Linking a new unit to an existing unit

In the above example we defined a new unit called `Pounds Sterling (£), Millions`. Looking at the guide on
[choosing units](../linked-data/units.md) we see that we could relate this unit back to a well established standard
unit defined by QUDT: [PoundSterling](http://qudt.org/vocab/unit/PoundSterling).

Our dataset could of course be expressed directly in [PoundSterling](http://qudt.org/vocab/unit/PoundSterling) but that
may make the data harder to read and compare so it would be ideal if you could define your own new unit
`Pounds Sterling (£), Millions`.

We've done some checking on the [QUDT Units vocabulary](http://www.qudt.org/doc/DOC_VOCAB-UNITS.html#Instances) to make
sure that our new unit doesn't duplicate an existing unit so we decide that it is helpful to link
`Pounds Sterling (£), Millions` back to [PoundSterling](http://qudt.org/vocab/unit/PoundSterling). This will ensure
that software can automatically figure out how to compare our data with other data sets that use units related to
[PoundSterling](http://qudt.org/vocab/unit/PoundSterling).

In the following examples, we'll show how to define new units re-using existing unit definitions, then how to apply
scaling to create the new units for `Pounds Sterling (£), Millions` and `Barrels of petrol per day (,000)` with a
[standard shaped](../shape-data/standard-shape.md) cube, using the different fields available for re-using existing
units. Here is the data set that we want to create units for in our json config file:

| Location     | Value |                           Measure |                             Unit |
|:-------------|------:|----------------------------------:|---------------------------------:|
| Biscuitburgh |    31 | Annual Income (Gross Value Added) |    Pounds Sterling (£), Millions |
| Biscuitburgh |   2.6 |  Average Daily Petrol Consumption | Barrels of petrol per day (,000) |

### Creating units using the from_existing field

This first example shows the existing definition for Pound Sterling being used from its URI entered into the
`from_existing` field. Normally, this would re-use the exact same unit definition. However, in our case, we want to
alter its configuration to suit our data set. So the existing unit definition is given the label
"Pounds Sterling (£), Millions", and this means it is now a new unit created that is derived from the existing
Pound Sterling unit definition.

```json
{
    "columns": {
        "Unit": {
            "type": "units",
            "values": [
                {
                    "label": "Pounds Sterling (£), Millions",
                    "from_existing": "http://qudt.org/vocab/unit/PoundSterling",
                },
            ]
        }
    }
}
```

### Scaling factor

The way the unit is used in the data set, such as the way amounts are being displayed, or how things are being counted,
can determine whether a `scaling_factor` field should be used.

Using the `scaling_factor` field means a new unit is being defined using the `from_existing` field's value as a base,
and altering it so the measurements made are scaled as specified in a base 10 expression. As shown in the example, a
unit defined with an existing base of Pounds Sterling, could be given a scaling factor of 1000000 to create the unit
"Millions of Pounds Sterling" (where 1 would mean 1 million pounds).

This essentially means that to convert from this new unit to the original unit, you would multiply it by the scaling
factor. The example defines the new unit further by specifying scaling.

```json
{
    "columns": {
        "Unit": {
            "type": "units",
            "values": [
                {
                    "label": "Pounds Sterling (£), Millions",
                    "from_existing": "http://qudt.org/vocab/unit/PoundSterling",
                    "quantity_kind": "http://qudt.org/vocab/quantitykind/Currency",
                    "scaling_factor": 1000000,
                },
            ]
        }
    }
}
```

Note that when the `scaling_factor` field is not specified in a unit that re-uses an existing unit's definition,
`scaling_factor` is automatically set to 1 by default.

### Quantity kind

The `quantity_kind` field can make use of the QUDT extensive various types of measurable quantities to help group and identify units. Provide a URI of a valid resource, adding it onto the prefix http://qudt.org/vocab/quantitykind/ to take advantage of QUDT's vast library of quantity kind resources. The previous example uses the `quantity_kind` field to specify that the unit is categorized as a currency unit.
For more information on quantity kinds as well as several quantity kinds to make use of, see the [Linked data Units](../../linked-data/units.md) page.

```json
{
    "columns": {
        "Unit": {
            "type": "units",
            "values": [
                {
                    "label": "Pounds Sterling (£), Millions",
                    "from_existing": "http://qudt.org/vocab/unit/PoundSterling",
                    "quantity_kind": "http://qudt.org/vocab/quantitykind/Currency",
                },
            ]
        }
    }
}
```

### si_scaling_factor

Another optional property useful for scaling is `si_scaling_factor`. The purpose of this field in the values object is
to relate scaled units to other units that are relevant, creating consistency within their scale. Most of the units
that are related in this sense are already defined.

**Note that this is an advanced feature and can safely be ignored if not needed.**

For our example data set, we also want another unit to measure barrels of oil per day, by the thousands.
This is where the `quantity_kind` and `si_scaling_factor` fields can be used to create a new unit that is grouped
together with its relevant quantity kind, and also measures units in a way that is consistently scaled.

```json
        "Unit": {
            "type": "units",
            "values": [
                {
                    "label": "Barrels of petrol per day (,000)",
                    "from_existing": "http://qudt.org/vocab/unit/BBL_UK_PET-PER-DAY",
                    "quantity_kind": "http://qudt.org/vocab/quantitykind/VolumePerUnitTime",
                    "scaling_factor": 1000,
                    // The SI unit for the `VolumePerUnitTime` is cubic meters per second.
                    // According to the webpage at http://qudt.org/vocab/unit/BBL_UK_PET-PER-DAY,
                    // `BBL_UK_PET-PER-DAY` has an SI scaling factor of `0.000001841587`
                    //
                    // Since our new unit is 1000 times larger than this, our scaling factor is:
                    "si_scaling_factor": 0.001841587
                },
            ]
        }

```

This unit uses a more exotic definition of "BBL_UK_PET-PER-DAY" as a base. It is then given the same quantity kind as
"BBL_UK_PET-PER-DAY", then, since we want to measure our observations by the thousands, the scaling factor of 1000 is
specified. Finally, the re-used unit of "BBL_UK_PET-PER-DAY" has a SI scaling factor of its own; 0.000001841587, and
since we are applying different scaling on our new unit, the `si_scaling_factor` field also sets the si_scaling_factor
to 1000 times the existing unit's, to match our scaling factor.

### Submitting to QUDT

Units may be [submitted](https://github.com/qudt/qudt-public-repo/wiki/Unit-Vocabulary-Submission-Guidelines) for
consideration of inclusion in the QUDT Units vocabulary. This is an advanced step that may be useful for units which
are extremely common.

### Linking a unit to the observation it describes

When creating a unit in a units column, it is also possible to specify an observation value to associate the units with,
 by entering the observation value into the `describes_observations` field. This is (only) necessary to associate a
 unit to its relevant observation value when there are multiple measures and the data set is in the pivoted shape.

 For more information on the distinction between pivoted/standard shape data sets, as well as single/multiple measures,
 see the [Pivoted Shape](../shape-data/pivoted-shape.md)

Example of a units column being defined with the `describes_obserations` field used to link to an observation.

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

<!-- # Configuring units

This guide discusses how to reuse units which have been defined elsewhere within your data cube. If you're not sure which unit is right for your data set, take a look at the guide on [choosing units](../linked-data/units.md).

## Defining a new unit

csvcubed automatically defines new units using the unique values in your [standard shape](../shape-data/standard-shape.md) cube's units column. If desired, you can gain more control over how the units are defined by providing configuration in a [qube-config.json](./qube-config.md) file.

A data set like the one defined below can be paired with a JSON configuration allowing you to provide additional information about the units you are creating:

| Location     | Value |                           Measure |                          Unit |
|:-------------|------:|----------------------------------:|------------------------------:|
| Biscuitburgh |    31 | Annual Income (Gross Value Added) | Pounds Sterling (£), Millions |

```json
{
    "$schema": "https://purl.org/csv-cubed/qube-config/v1",
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
}
```

**N.B. you must ensure that your units column definition contains defintions for *all* of the units contained within your dataset; the `label` property must match the value found in the cell.**

We can see in the above that we've defined a new unit called `Pounds Sterling (£), Millions` and been able to configure its description; this will give extra context to help people really understand your data. But we can still improve our data by describing how this new unit relates to standardised units defined by other organisations so users can compare your data with other data cubes with confidence.

### Linking a new unit to an existing unit

In the above example we defined a new unit called `Pounds Sterling (£), Millions`. Looking at the guide on [choosing units](../linked-data/units.md) we see that we could relate this unit back to a well established standard unit defined by QUDT: [PoundSterling](http://qudt.org/vocab/unit/PoundSterling).

Our dataset could of course be expressed directly in [PoundSterling](http://qudt.org/vocab/unit/PoundSterling) but that may make the data harder to read and compare so it would be ideal if you could define your own new unit `Pounds Sterling (£), Millions`.

We've done some checking on the [QUDT Units vocabulary](http://www.qudt.org/doc/DOC_VOCAB-UNITS.html#Instances) to make sure that our new unit doesn't duplicating an existing unit so we decide that it is helpful to link `Pounds Sterling (£), Millions` back to [PoundSterling](http://qudt.org/vocab/unit/PoundSterling). This will ensure that software can automatically figure out how to compare our data with other data sets that use units related to [PoundSterling](http://qudt.org/vocab/unit/PoundSterling).

In the following example, we'll show how to define new units for `Pounds Sterling (£), Millions` and `Barrels of petrol per day (,000)` with a [standard shaped](../shape-data/standard-shape.md) cube:

**1. Ensure that your units column contains the new units' labels**

| Location     | Value |                           Measure |                             Unit |
|:-------------|------:|----------------------------------:|---------------------------------:|
| Biscuitburgh |    31 | Annual Income (Gross Value Added) |    Pounds Sterling (£), Millions |
| Biscuitburgh |   2.6 |  Average Daily Petrol Consumption | Barrels of petrol per day (,000) |

**2. Edit your [qube-config.json](../configuration/qube-config.md) so that your units column has the following definition**

```json
{
    "$schema": "https://purl.org/csv-cubed/qube-config/v1",
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
                },
                {
                    "label": "Barrels of petrol per day (,000)",
                    "from_existing": "http://qudt.org/vocab/unit/BBL_UK_PET-PER-DAY",
                    "quantity_kind": "http://qudt.org/vocab/quantitykind/VolumePerUnitTime",
                    "scaling_factor": 1000,
                    "si_scaling_factor": 0.001841587
                }
            ]
        }
    }
}
```

**N.B. you must ensure that your units column definition contains definitions for *all* of the units contained within your dataset.**

Taking a closer look at the new `Pounds Sterling (£), Millions` unit:

```json
{
    // We start by defining the label; this must exactly match the label's value in the `unit` column.
    "label": "Pounds Sterling (£), Millions",
    // We give our unit a more verbose description detailing what it represents.
    "description": "Millions of Pounds Sterling (£).",
    // We state that our new unit is derived from QUDT's existing PoundSterling unit.
    "from_existing": "http://qudt.org/vocab/unit/PoundSterling",
    // Like PoundSterling we also categorise our new unit as a kind of currency.
    "quantity_kind": "http://qudt.org/vocab/quantitykind/Currency",

    // We state that to convert from this unit back into the `PoundSterling` unit you multiply values by 1,000,000.
    "scaling_factor": 1000000

    // Since currencies fluctuate so readily and there is no standard SI unit for currencies, we do not define any `si_scaling_factor`.
}
```

Taking a closer look at the new `Barrels of petrol per day (,000)` unit:

```json
{
    // Again, the label must exactly match the label's value in the `unit` column.
    "label": "Barrels of petrol per day (,000)",
    // We start using the more exotic unit `BBL_UK_PET-PER-DAY` (Barrel (UK Petroleum) Per Day).
    "from_existing": "http://qudt.org/vocab/unit/BBL_UK_PET-PER-DAY",
    // Just like `BBL_UK_PET-PER-DAY`, our new unit is also a kind of volume per unit time.
    "quantity_kind": "http://qudt.org/vocab/quantitykind/VolumePerUnitTime",

    // We state that to convert a value from this unit back to the `BBL_UK_PET-PER-DAY` unit you must multily values by 1,000.
    "scaling_factor": 1000,

    // The SI unit for the `VolumePerUnitTime` is cubic meters per second.
    // According to the webpage at http://qudt.org/vocab/unit/BBL_UK_PET-PER-DAY,
    // `BBL_UK_PET-PER-DAY` has an SI scaling factor of `0.000001841587`
    //
    // Since our new unit is 1000 times larger than this, our scaling factor is:
    "si_scaling_factor": 0.001841587
}
```

## Submitting to QUDT

Units may be [submitted](https://github.com/qudt/qudt-public-repo/wiki/Unit-Vocabulary-Submission-Guidelines) for consideration of inclusion in the QUDT Units vocabulary. This is an advanced step that may be useful for units which are extremely common. -->
