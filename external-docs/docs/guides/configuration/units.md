# Configuring units

This guide discusses how to reuse units which have been defined elsewhere within your data cube. If you're not sure which unit is right for your data set, take a look at the guide on [choosing units](../linked-data/units.md).

## Defining a new unit

csvcubed automatically defines new units using the unique values in your [standard shape](../shape-data.md#standard-shape) cube's units column. If desired, you can gain more control over how the units are defined by providing configuration in a [qube-config.json](./qube-config.md) file.

A data set like the one defined below can be paired with a JSON configuration allowing you to provide additional information about the units you are creating:

| Location     | Value |                           Measure |                          Unit |
|:-------------|------:|----------------------------------:|------------------------------:|
| Biscuitburgh |    31 | Annual Income (Gross Value Added) | Pounds Sterling (£), Millions |

```json
{
    "$schema": "https://purl.org/csv-cubed/qube-config/v1.0",
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

In the following example, we'll show how to define new units for `Pounds Sterling (£), Millions` and `Barrels of petrol per day (,000)` with a [standard shaped](../shape-data.md#standard-shape) cube:

**1. Ensure that your units column contains the new units' labels**

| Location     | Value |                           Measure |                                      Unit |
|:-------------|------:|----------------------------------:|------------------------------------------:|
| Biscuitburgh |    31 | Annual Income (Gross Value Added) |             Pounds Sterling (£), Millions |
| Biscuitburgh |   2.6 |  Average Daily Petrol Consumption | Barrels of petrol per day (,000) |

**2. Edit your [qube-config.json](../configuration/qube-config.md) so that your units column has the following definition**

```json
{
    "$schema": "https://purl.org/csv-cubed/qube-config/v1.0",
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

**N.B. you must ensure that your units column definition contains defintions for *all* of the units contained within your dataset.**

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

Units may be [submitted](https://github.com/qudt/qudt-public-repo/wiki/Unit-Vocabulary-Submission-Guidelines) for consideration of inclusion in the QUDT Units vocabulary. This is an advanced step that may be useful for units which are extremely common.
