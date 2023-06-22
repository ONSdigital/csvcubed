# Worked example 3

The Inspect API facilitates statistical analysis of CSV-Ws by leveraging the formal structure of a data cube to identify the data set's components and pass this information into an existing statistical model. These models can therefore be generalised and applied to multiple data cubes simply by providing the file path to the metadata JSON file.

## Loading the data

The first step in the process is to load the CSV-W into csvcubed and create the Inspector object:

```python
>>> from csvcubed.inspect.inspectortable import Inspector

>>> eurovision_inspector = Inspector('sweden-at-eurovision-complete-dataset.csv-metadata.json')
```

## Exploring the data

You can then explore the structure of the data set:

```python
>>> eurovision.tables
[DataCubeTable(csv_url='sweden-at-eurovision-complete-dataset.csv', title='Sweden at Eurovision Complete Dataset', shape=<CubeShape.Standard: 1>, data_set_uri='sweden-at-eurovision-complete-dataset.csv#dataset'),
 CodeListTable(csv_url='entrant.csv', title='Entrant', concept_scheme_uri='entrant.csv#code-list'),
 CodeListTable(csv_url='language.csv', title='Language', concept_scheme_uri='language.csv#code-list'),
 CodeListTable(csv_url='song.csv', title='Song', concept_scheme_uri='song.csv#code-list'),
 CodeListTable(csv_url='year.csv', title='Year', concept_scheme_uri='year.csv#code-list')]

>>> primary_table = eurovision_inspector.tables[0]
>>> primary_table
DataCubeTable(csv_url='sweden-at-eurovision-complete-dataset.csv', title='Sweden at Eurovision Complete Dataset', shape=<CubeShape.Standard: 1>, data_set_uri='sweden-at-eurovision-complete-dataset.csv#dataset')

>>> csv_url = primary_table.csv_url
>>> csv_url
'sweden-at-eurovision-complete-dataset.csv'

>>> primary_table_columns = primary_table.columns
>>> primary_table_columns
OrderedDict([('Year',
              DimensionColumn(dimension=LocalDimension(dimension_uri='sweden-at-eurovision-complete-dataset.csv#dimension/year', label='Year'))),
             ('Entrant',
              DimensionColumn(dimension=LocalDimension(dimension_uri='sweden-at-eurovision-complete-dataset.csv#dimension/entrant', label='Entrant'))),
             ('Song',
              DimensionColumn(dimension=LocalDimension(dimension_uri='sweden-at-eurovision-complete-dataset.csv#dimension/song', label='Song'))),
             ('Language',
              DimensionColumn(dimension=LocalDimension(dimension_uri='sweden-at-eurovision-complete-dataset.csv#dimension/language', label='Language'))),
             ('Value',
              StandardShapeObservationsColumn(unit=UnitsColumn(), measures_column=MeasuresColumn())),
             ('Measure',
              MeasuresColumn()),
             ('Unit',
              UnitsColumn()),
             ('Marker',
              AttributeColumn(attribute=LocalAttribute(attribute_uri='sweden-at-eurovision-complete-dataset.csv#attribute/observation-status', label='Observation Status'), required=False))])
```

## Formatting the data

You can also load the CSV as a pandas DataFrame:

```python
>>> data_cube_repository = primary_table.data_cube_repository
>>> df, errors = data_cube_repository.get_dataframe(csv_url=csv_url, include_suppressed_cols=False, dereference_uris=False)
>>> df.head()
|   | Year | Entrant    | Song          | Language | Value |         Measure |     Unit | Marker |
| 0 | 1958 | Alice Babs | Lilla stjärna | Swedish  |   4.0 |      Final Rank | Unitless |    NaN |
| 1 | 1958 | Alice Babs | Lilla stjärna | Swedish  |  10.0 |    Final Points | Unitless |    NaN |
| 2 | 1958 | Alice Babs | Lilla stjärna | Swedish  |   1.0 | People on Stage |   Number |    NaN |
| 3 | 1959 | Brita Borg | Augustin      | Swedish  |   9.0 |      Final Rank | Unitless |    NaN |
| 4 | 1959 | Brita Borg | Augustin      | Swedish  |   4.0 |    Final Points | Unitless |    NaN |
```

In this example, the data set is in the [standard shape](../shape-data/standard-shape.md). Some statistical methods will need the dataframe to be in the [pivoted shape](../shape-data/pivoted-shape.md), and this can be achieved by accessing the column types and passing this information to the pandas `DataFrame.pivot` method:

```python
>>> from csvcubed.inspect.inspectorcolumns import DimensionColumn, MeasuresColumn, ObservationsColumn

>>> dimension_col_titles = [title for title, column in primary_table_columns.items() if isinstance(column, DimensionColumn)]
>>> measure_col_titles = [title for title, column in primary_table_columns.items() if isinstance(column, MeasuresColumn)]
>>> value_col_titles = [title for title, column in primary_table_columns.items() if isinstance(column, ObservationsColumn)]

>>> pivoted_df = df.pivot(index=dimension_col_titles, columns=measure_col_titles[0], values=value_col_titles[0]).dropna().reset_index()
>>> pivoted_df.head()

| Year | Entrant        | Song                  | Language | Final Rank | Final Points | People on Stage |
| 1958 | Alice Babs     | Lilla stjärna         | Swedish  |        4.0 |         10.0 |             1.0 |
| 1959 | Brita Borg     | Augustin              | Swedish  |        9.0 |          4.0 |             1.0 |
| 1960 | Siw Malmkvist  | Alla andra får varann | Swedish  |       10.0 |          4.0 |             1.0 |
| 1961 | Lill-Babs      | April,april           | Swedish  |       14.0 |          2.0 |             1.0 |
| 1962 | Inger Berggren | Sol och vår           | Swedish  |        7.0 |          4.0 |             1.0 |
```

## Analysing the data (Factor Analysis)

With the data set available as a DataFrame, you can apply any appropriate statistical analysis - for example, imagine that you want to visualise how the three observed variables (`Final Rank`, `Final Points` and `People on Stage`) are correlated with each other:

```python
>>> import plotly.express as px

>>> c = pivoted_df.corr()
>>> fig = px.imshow(c, labels=dict(color="Correlation"))
>>> fig.show()
```

![Correlation heatmap](../../images/heatmap.png)


You could also undertake a Factor Analysis to explore how the observed variables are inter-related. Firstly, you would want to check whether Factor Analysis is an appropriate technique for this data set by performing some suitability tests:

```python
>>> from factor_analyzer import calculate_bartlett_sphericity, calculate_kmo

>>> chi_sq, p = calculate_bartlett_sphericity(pivoted_df)
>>> kmo_all, kmo_model = calculate_kmo(pivoted_df)

>>> print("Bartlett Test of Sphericity results:")
>>> print(f"Chi-squared: {chi_sq}, p-value: {p}")
>>> print("Kaiser-Meyer-Olkin (KMO) results:")
>>> print(f"KMO score per item: {kmo_all}, Overall KMO score: {kmo_model}")
Bartlett Test of Sphericity results:
Chi-squared: 33.351, p-value: 0.0000003
Kaiser-Meyer-Olkin (KMO) results:
KMO score per item: [0.498 0.497  0.496], Overall KMO score: 0.497
```

Once you have reviewed the results of the suitability tests, you can perform the Factor Analysis:

```python
>>> from factor_analyzer import FactorAnalyzer

>>> fa = FactorAnalyzer(n_factors=3, rotation=None)
>>> fa.fit(pivoted_df)
>>> ev, v = fa.get_eigenvalues()
>>> ev
array([1.77598209, 0.86422349, 0.35979442])

>>> fig = px.line(x=range(1, pivoted_df.shape[1]+1), y=ev)
>>> fig.show()
```

![Eigenvalue plot](../../images/eigenvalues.png)

```python
>>> loadings = fa.loadings_
>>> loadings
array([[ 0.89912209,  0.02503715,  0.        ],
       [-0.60131768,  0.39154271,  0.        ],
       [ 0.5034576 ,  0.42293552,  0.        ]])
```

## Another example: Generalised Linear Model

This is another example of how information can be retrieved from a CSVW with the help of the Inspect API. The purpose of this example is to highlight how Inspector objects and the information they give access to can streamline exploration of data and avoid the requirement of any thorough knowledge of the data set or its details in order to retrieve information to use in analysis.

Here, we will be using the Inspect API to acquire all the information we need to then create a basic GLM (Generalised Linear Model) using the statsmodels library.

Say we want to make a model on a data set where we want the response variable to be modelled on the observation values from our input data set, and we want it to depend on the values contained within a time period column, i.e. dimension column.

```python
>>> gross_pay_inspector = Inspector('gross-median-weekly-pay.csv-metadata.json')
>>> gross_pay_table = gross_pay_inspector.tables[0]
>>> gross_pay_columns = gross_pay_table.columns
```

After loading the Inspector object, we can get the information we need from it. Refer to the previous example [Exploring data](./example3.md/#exploring-the-data) for accessing information using an Inspector, e.g. the data set's primary table and then the columns. It will work the same way, all we need to do is provide a valid input file.

Then we can get the dimensions columns from the data set. Note for an analysis like this, we assume there is only one observations column in the data set with an associated dimension. Otherwise, you would obviously need to know which set of observations you want to analyse and specify it.

The previous example's [Formatting data](./example3.md/#formatting-the-data) section shows how to acquire columns of a specific type using the Inspector object. We can do the same here to get the observation and dimension column titles.

```python
>>> dimension_col_title = [title for title, column in gross_pay_columns.items() if isinstance(column, DimensionColumn)]
>>> value_col_title = [title for title, column in gross_pay_columns.items() if isinstance(column, ObservationColumn)]
```

We have acquired the titles of the observations column and the dimensions column from our data set. Now, we can input this information into the GLM creation functions. The rest of the code is just the creation of a basic GLM.

```python
>>> glm_formula = f"{value_col_title} ~ {dimension_col_title}"
```

Without the functionality from the Inspect API, we would have to do something like figuring out the exact titles of the data set's columns, and hard coded them into
a script that would only ever work for this data set, which would look something like this:

```python
>>> glm_formula = "Value ~ Period"
```

The rest of the GLM creation code:
```python
>>> distribution_family = sm.families.Gaussian()

>>> glm_model = glm(
>>>     formula=glm_formula, data=my_dataframe, family=distribution_family
>>> ).fit()

>>> summary = glm_model.summary()
```
