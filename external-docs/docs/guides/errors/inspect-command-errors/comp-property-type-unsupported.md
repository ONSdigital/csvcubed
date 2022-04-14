# Error - DSD component property type `<property_type>` is not supported.

## When it occurs

The supported data structure definition (DSD) property types are `Dimension`,  `Attribute` and `Measure`.

## How to fix

Make sure the input CSV-W json-ld is a valid data cube or a code list that is provided in one of two specialised forms of tidy data: [standard shape](../../../guides/shape-data.md#standard-shape) and [pivoted shape](../../../guides/shape-data.md#pivoted-shape).