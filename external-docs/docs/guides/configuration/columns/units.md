## Units columns

This section will focus on the configuration of units columns, their presence in the structure of a cube config file, and how their definition can vary depending on the shape of the data set, or the number of units. The configuration of units themselves will not be the primary focus of this section. For more information on defining and configuring units, with examples, see the [configuring units](./units.md) page.

The *units* column represents how the measured quantity is being counted or incremented in each row, defining what unit of measurement is being used to measure this observation. At least one unit is required to be defined in a data cube for it to be valid.

In a configuration file, the unit column is a form of attribute column. This means they share similarities to configure, sharing all of the attribute column’s configuration options, but with some additional options unique to units.

However, defining unit columns is also quite different to other components such as dimensions, observations and attributes, as unit column definitions contain references to discrete units. To define a unit column, specify the `type` field of the column definition as "units". An example of a cube configuration containing a unit column definition is shown below:

| Year | Location      | Value | Measure                | Unit        |
|:-----|:--------------|------:|-----------------------:|------------:|
| 2019 | Canada        |  70   | Average Height for Men | Inches      |
| 2020 | United States |  69   | Average Height for Men | Inches      |
| 2021 | England       |  175  | Average Height for Men | Centimetres |
| 2021 | Scotland      |  175  | Average Height for Men | Centimetres |

```json
{
    "$schema": "https://purl.org/csv-cubed/qube-config/v1",
    "title": "Average Height for Men in different countries",
    "columns": {
        "Units column": {
            "type": "units",
            "values": [
              {
                "Unit 1": {
                    "label": "Inches",
                    "description": "Height measured in Inches"
                },
                "Unit 2": {
                  "label": "Centimetres",
                  "description": "Height measured in Centimetres, cm"
                }
              }
          ]
        },
    }
}
```

<!-- TODO: At some point, add an example of a single measure pivoted data set with a units column (multiple units) -->

The unit column definition should contain a "values" object. This object can be filled in with the fields that are used to populate a unit that will appear in the column. The example above uses a basic data set containing two units, showing the configuration, but only focusing on the units column's definition with basic unit details given.

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
