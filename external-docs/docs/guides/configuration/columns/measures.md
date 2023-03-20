## Measures columns

 This section will focus on defining measure columns, the possible configurations with single and multiple measure data sets, and their presence in the structure of a cube configuration file. This page will avoid going into full detail on creating and configuring the measures themselves.

The *measure* column defines the phenomenon that is being observed, what is being quantified in this observation. In this way it is similar to a dimension. At least one measure is required to be defined in a data cube for it to be valid. Measures can either be attached to a Measure Column if there are multiple different measures appearing in columns throughout your data set, or to an Observation column's `measure` field if all observations in this column of the data set use the same measure.

For more information on defining measures, and populating a measure's fields in a cube configuration, please see the [Measures Configuration](#measures-configuration) TODO fix this link when the structure of the guide is determined and all the pages exist.

An important point to remember about measure columns is that they are only supported in a standard shape data set. This is because measures in pivoted shape data sets are defined by being attached to the observation columns they appear in, whereas in the standard shape, each row can specify the measure and unit being used for that row's observation, meaning a measure column can be used. The table below shows a simple data set containing a measures column, which uses two different measures: Average Height, and Average Weight. This small data set shows how measures can be used in a column of their own to enable an associated observations column to measure different things. Also note how different units can be used for these measures, to enable further detail and variety in what is being observed and how it is measured.

| Year | Location      | Value  | Measure        | Unit        |
|:-----|:--------------|-------:|---------------:|------------:|
| 2019 | England       |  175   | Average Height | Centimetres |
| 2019 | England       |  85    | Average Weight | Kilograms   |
| 2021 | France        |  175   | Average Height | Centimetres |
| 2021 | France        |  82    | Average Weight | Kilograms   |

Now we will show how a measure column like this could be defined in the cube configuration file, also providing some basic metadata to display how a measure column's definition fits into the structure of the config json.
To define a measure column, specify the column's `type` field as "measures", then enter any measures being used in the column into a list of objects in the `values` field, like so:

```json
{
    "$schema": "https://purl.org/csv-cubed/qube-config/v1",
    "title": "Average Height and Weight for Men in different countries",
    "columns": {
        "Units column": {
            "type": "measures",
            "values": [
              {
                "Measure 1": {
                  "label": "Average Height",
                  "description": "The average height for men in the observed country."
                },
                "Measure 2": {
                  "label": "Average Weight",
                  "description": "The average weight for men in the observed country."
                }
              }
          ]
        },
    }
}
```

When defining a measures column containing measure definitions, the measure details are specified in a list of objects which is passed into a field named `values`. The example above uses a small data set containing two measures, then shows the configuration, focusing only on the measure column's definiton with only basic configuration. For more information on defining and configuring measures, see the [measure configuration](../measure-configuration.md) page.

One of the advantages of defining measure columns in this way in standard shape data sets is that no changes are required in the cube configuration file if new measures are added. Using multiple measures in a measure column simply means adding new rows to the data set, and specifying measures (and units) to be used for the observation. To view more information on the difference between single measure and multi measure data sets, see the [Shape your data](../../shape-data/index.md) page (for both standard and pivoted shape).

## Measure definitions

This table shows a list of the possible fields that can be entered when configuring a measure.

| **field name**   | **description**                                                                                                             | **default value** |
|------------------|-----------------------------------------------------------------------------------------------------------------------------|-------------------|
| `label`          | The title of the measure (Required; Optional if `from_existing` defined)                                                    | *none*            |
| `description`    | A description of the contents of the measure (Optional)                                                                     | *none*            |
| `from_existing`  | The uri of the resource for reuse/extension (Optional)                                                                      | *none*            |
| `definition_uri` | A uri of a resource to show how the measure is created/managed (e.g. a uri of a PDF explaining the measure type) (Optional) | *none*            |
