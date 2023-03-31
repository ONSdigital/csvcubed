# Units columns

This page discusses what a units column is, where one should be used, and how one can be defined.

The configuration of unit definitions themselves will not be the primary focus of this page; for help with this, see
[Unit definitions](../unit-definitions.md).

> For a detailed look at a unit column's configuration options, see the [Reference table](#reference) at the bottom of
>this page.

## What is a units column?

A *units* column describes the unit that each row in your CSV has been measured using.

The following is an example of a small data set containing a units column:

| Year | Location      | Average Height of Men |        Unit |
|:-----|:--------------|----------------------:|------------:|
| 2019 | Canada        |                    70 |      Inches |
| 2020 | United States |                    69 |      Inches |
| 2021 | England       |                   175 | Centimetres |

The units column is titled `Unit`. The first two rows of the data set use the unit `Inches` to measure height, and the
third row uses a different unit, `Centimetres`. In this case, different units are being used to measure the same thing.

## When to use a units column

Every valid data cube needs at least one unit. Units columns can be used in both
[standard](../../../shape-data/standard-shape.md) and [pivoted shape](../../../shape-data/pivoted-shape.md) cubes.

If every value in an [observations column](./observations.md) has the same unit, then you should configure the unit
against the [observations column](./observations.md).

If some values in your observations column use one unit and some other values in the same column use a different unit
then you should use a units column. In the example table above, we see a clear example of this given that the first two
rows use `Inches` and the third row uses `Centimetres` to measure the `Average Height of Men`.

## Basic configuration

The following JSON shows how a units column can be defined in a [qube configuration file](../../qube-config/index.md):

```json
{
    "$schema": "https://purl.org/csv-cubed/qube-config/v1",
    "title": "Average Height of Men in different countries",
    "columns": {
        "Unit": {
            "type": "units"
        },
    }
}
```

To define a units column, specify the `type` of the column definition as `units`.

In this scenario of a minimal definition, since we do not specify any other details or properties; the unit
will auto-generate a `label` field by default that takes the column's title. Here, the label would be `Unit`.

## Optional properties

When defining a units column, there are optional properties that can be entered, depending on how your units are
being defined within the column.

### Values

If you are creating new units within your units column, the details of the new units should be entered into a
`values` field. The JSON below shows an example of the `values` field used in a units column.

```json
{
    "$schema": "https://purl.org/csv-cubed/qube-config/v1",
    "title": "Average Height and Weight for Men in different countries",
    "columns": {
        "Unit": {
            "type": "units",
            "values": true
        },
    }
}
```

By default, the `values` field is set to `true`. This indicates to csvcubed to automatically generate
[unit definitions](../unit-definitions.md) unique to your data set.

### From Template

Units columns can also make use of the `from_template` field. Templates are pre-configured column definitions that help
speed up the creation of linked data columns. The use of this field in a units column is shown in the example below:

```json
{
    "$schema": "https://purl.org/csv-cubed/qube-config/v1",
    "title": "Average Income in Pounds Sterling",
    "columns": {
        "Unit": {
            "from_template": "qudt-units"
        },
    }
}
```

Enter the identifier of a template to be used as the units column. Note that you can override the configuration of used
templates by specifying individual properties.

For more information on templates, as well as a list of templates that can be used, see the
[Templates](../templates.md) page.

### Cell URI Template

If you are re-using existing units in your measures column, then do not use the `values` field to define the
unit details. Instead, use the field `cell_uri_template`.

```json
{
    ...
    "columns": {
        "Unit": {
            "from_existing": "http://example.org/units/example-unit",
            "cell_uri_template": "http://example.org/code-lists/example-units/{+unit}"
        },
    }
}
```

 Provide a URI of a unit resource to use in the definition.

!!! Warning
    The use of the `cell_uri_template` field is considered an advanced configuration option, and therefore care must be
    taken to ensure that the values generated are valid.

The format of the `cell_uri_template` value **must** follow [RFC6570](https://www.rfc-editor.org/rfc/rfc6570) guidance
for URI Templates. Note that the only variable which can be used in a `cell_uri_template` references the column itself;
the name of the variable can be calculated by applying the
[CSV column name safe transformation](../../../uris.md#csv-column-name-safe-transformation) to the CSV column title.

### Describing Observations

Another field that can be applied to units columns that can be passed into their definition is `describes_observations`.
This field associates the units column with the relevant observation values where the units are being used. Note that
this is only applicable to pivoted shape cubes with multiple measures and multiple observation value columns. The use of
this field is covered on the [Pivoted shape cube](../../../shape-data/pivoted-shape.md#multiple-measures) page.

## Reference

| **field name**           | **description**                                                                                                                                                                                                      | **default value** |
|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------|
| `type`                   | The type of the column, provide `"units"` for a units column.(Required)                                                                                                                                              | *dimension*       |
| `values`                 | (New Units only) If basic units are desired, a boolean value of `true` is used to signify to csvcubed to create units from values in this column                                                                     | `true`            |
| `from_template`          | (Existing Units only) Use a [column template](../templates.md)                                                                                                                                                       | *none*            |
| `cell_uri_template`      | (Existing Units only) Used to define a template to map the cell values in this column to URIs                                                                                                                        | *none*            |
| `describes_observations` | (Unit column only) Associates the unit column with the relevant observation values. This is only necessary for [pivoted shape data sets](../../../shape-data/pivoted-shape.md) with multiple observation value columns. | *none*            |
