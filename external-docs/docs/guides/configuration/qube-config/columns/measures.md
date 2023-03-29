# Measures columns

This page discusses what a measures column is, where one should be used, and how one can be defined.

The configuration of measure definitions themselves will not be the primary focus of this page; for help with this, see
[Measure definitions](../measure-definitions.md).

> For a detailed look at a measure column's configuration options, see the [Reference table](#reference) at the bottom
> of this page.

## What is a measures column?

A *measures* column defines the phenomenon that has been measured in your observed values. It is useful to help express
the measure used in [sparse data](../../../../glossary/index.md#sparse-data) sets.

Consider the following data set containing a measures column; the measures column is the one with the title `Measure`.

| Year | Location | Value |        Measure |        Unit |
|:-----|:---------|------:|---------------:|------------:|
| 2019 | England  |   175 | Average Height | Centimetres |
| 2019 | England  |    85 | Average Weight |   Kilograms |
| 2021 | France   |   175 | Average Height | Centimetres |

The `Measure` column declares that the phenomenon measured in the first row is `Average Height`, the phenomenon measured
in the second row is `Average Weight`, and so on. Note that there can only ever be one observed value per row when using
a measures column.

## When to use a measures column

Every valid data cube requires **at least one measure**. If you choose to use the
[Standard Shape](../../../shape-data/standard-shape.md) to represent your data then you **must** include a measures column.

If you choose to use the [Pivoted Shape](../../../shape-data/pivoted-shape.md) to represent your data then all measures
must be defined against [Observations Columns](./observations.md); in this case you cannot include a measures column.

N.B. It is **not possible** to define multiple measures columns in the same data cube.

## Basic configuration

Now we will show how a measures column can be defined in a [qube configuration](../index.md) file.

A basic measures column definition can be seen below:

```json
{
    "$schema": "https://purl.org/csv-cubed/qube-config/v1",
    "title": "Average Height and Weight for Men in different countries",
    "columns": {
        "Measure": {
            "type": "measures"
        },
    }
}
```

Note that the `type` has been set to `measures`.

If you use one of the conventional column titles for measures then the above configuration is
equivalent to what csvcubed would do to your column by default.

One of the advantages of measure columns in standard shape data sets is that no changes are required in the cube
configuration file if new measures are added. Using multiple measures in a measure column simply means
adding new rows to the data set, and specifying measures (and units) to be used for the observation.

To view more information on the difference between single measure and multi measure data sets, see the
[Shape your data](../../../shape-data/index.md) page (for both standard and pivoted shape).

### Optional properties

When defining a measures column, there are optional properties that can be entered, depending on how your measures are
being defined within the column.

### Values

If you are creating new measures within your measures column, the details of the new measures should be entered into a
`values` field. The JSON below shows an example of the `values` field used in a measures column.

```json
{
    ...
    "columns": {
        "Measure": {
            "type": "measures",
            "values": true
        },
    }
}
```

By default, the `values` field is set to `true`. This indicates to csvcubed to automatically generate
[measure definitions](../measure-definitions.md) unique to your data set. See the previous link for more information
on configuring measures and the fields that can be provided to the `values` object list.

### Cell URI Template

If you are re-using existing measures in your measures column, then do not use the `values` field to define the
measures. Instead, use the field `cell_uri_template` to define your existing measure. The JSON below shows an example
of this field in use.

```json
{
    ...
    "columns": {
        "Measure": {
            "type": "measures",
            "from_existing": "http://example.org/measures/example-measure",
            "cell_uri_template": "http://example.org/code-lists/example-measure/{+measure}"
        },
    }
}
```

 After setting the `type` of the column as `measures`, provide the field `cell_uri_template` with a URI of a measure
 resource to use in the definition.

 !!! Warning
    The use of the `cell_uri_template` field is considered an advanced configuration option, and therefore care must be taken to ensure that the values generated are valid.

The format of the `cell_uri_template` value **must** follow [RFC6570](https://www.rfc-editor.org/rfc/rfc6570) guidance
for URI Templates. In the case of any doubt, follow the pattern in the examples shown above (e.g.
`http://example.org/some-uri/{+column_name}`), as this will ensure csvcubed safely
[transforms the column header](../../../uris.md#csv-column-name-safe-transformation) to the CSV-W format.

## Reference

| **field name**      | **description**                                                                                                                                                                                                                                                                                        | **default value** |
|---------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------|
| `type`              | The type of the column, provide `"measures"` for the measure column type.(Required)                                                                                                                                                                                                                    | *dimension*       |
| `values`            | (New Measures only) If basic measures are desired, a boolean value of `true` is used to signify to csvcubed to create units/measures from values in this column; otherwise values is a dictionary which defines the measures using the notation from [Measures definitions](../measure-definitions.md) | `true`            |
| `cell_uri_template` | (Existing Measures only) Used to define a template to map the cell values in this column to URIs                                                                                                                                                                                                       | *none*            |
