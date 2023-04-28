# Using the Inspect API to load a dereferenced CSVW.

This documentation is a reference point for developers showing some functionality of the Inspect API, focusing on the use of the get_dataframe function to dereference the URIs of a CSV into human readable labels.

note: this document is temporarily being placed in the root docs folder while the structure and location of inspect documentation is being figured out.

## The get_dataframe function

This `get_dataframe` function is used to get a pandas DataFrame from the CSV URL from the currently loaded data cube. It is part of the `DataCubeInspector` class, and is used by providing a `csv_url` as well as setting the `dereference_uris` parameter. It is set to `True` by default. This means the column values of the input CSV will be altered to contain their human readable labels rather than the fragment of the URI.

The example below shows the get_dataframe function being used on a CSV input from a cube that contains locally defined code lists, attribute resource values, multiple units and multiple measures.

Here is the example data set:

| Dim1        | Dim2             | Dim3 | AttrResource | AttrLiteral | Units       | Measures       | Obs |
|:------------|:-----------------|-----:|:-------------|:------------|:------------|:---------------|:----|
| something-1 | something-else-1 | 2021 | final        | -90         | some-unit-1 | some-measure-1 | 127 |
| something-2 | something-else-2 | 2022 | provisional  | -80         | some-unit-2 | some-measure-2 | 227 |
| something-3 | something-else-3 | 2023 | estimated    | -70         | some-unit-3 | some-measure-3 | 327 |

Assuming the CSV URL that is to be used as input has been assigned to a variable called `csv_url`, and that a `DataCubeInspector` object exists, the `get_dataframe` function can be used with the `dereference_uris` parameter set to `True` like so:

```python
    dataframe, validation_errors = data_cube_inspector.get_dataframe(
        csv_url, dereference_uris=True
    )
```

In this scenario, the contents of the DataFrame object returned by the `get_dataframe` function would look like this:

| Dim1        | Dim2             | Dim3 | AttrResource | AttrLiteral | Units       | Measures       | Obs |
|:------------|:-----------------|-----:|:-------------|:------------|:------------|:---------------|:----|
| Something 1 | Something Else 1 | 2021 | Final        | -90         | Some Unit 1 | Some Measure 1 | 127 |
| Something 2 | Something Else 2 | 2022 | Provisional  | -80         | Some Unit 2 | Some Measure 2 | 227 |
| Something 3 | Something Else 3 | 2023 | Estimated    | -70         | Some Unit 3 | Some Measure 3 | 327 |
