# Defining a QbCube

This file serves as an introduction to how the `Qb` components in csvcubed should be used. It is a rough description of the purpose of each component as well as where it should be used.

Note that it is generally supposed that the `Qb` cube classes are (and should always be) the back-end way csvcubed represents and validates data cubes before they are serialised to CSV-Ws. Hence, all classes are designed and structured to be clearly named, specific in their purpose and readily composable; they are generally **unsuitable for direct use**. These classes are designed to be used by a **specialised user interface which is targeted to the needs and capabilities of a specific type of user**, e.g. a declarative JSON document for experts who need full control, or a wizard-style GUI for an interactive publication process.

## The `Cube` Class

When defining a `Cube` there are three components which need to be provided: the catalog `metadata`, the `data` and the `columns`' metadata.

```python
from csvcubed.models.cube import *
import pandas as pd

data = pd.DataFrame({
    "A Dimension": ["a", "b", "c"],
    "An Observation": [1, 2, 3]
})

cube = Cube(
    metadata=CatalogMetadata("Some Dataset Name"),
    data=data,
    columns=[
        QbColumn("A Dimension", NewQbDimension.from_data("The Dimension's Name", data["A Dimension"])),
        QbColumn(
            "An Observation",
            QbSingleMeasureObservationValue(
                measure=NewQbMeasure("Some Measure"),
                unit=NewQbUnit("Some Unit")
            )
        )
    ]
)
```

**The catalog metadata** - holds the catalog metadata which should describe the cube (i.e. a description of its contents), as well as details about the publication (e.g. the publisher, its publication date, contact information, and usage restrictions/license). Further information on configuring catalog metadata is [available](https://github.com/GSS-Cogs/dataengineer-walkthrough/blob/master/csvcubed-usage/Generating%20Catalog%20Metadata.md#how-to-generate-catalog-metadata).

**The data** - holds the observational data associated with the cube (as a pandas DataFrame). Although optional, providing this data allows additional validations on your cube.

**The column mappings/metadata** - holds a list of `QbColumn`s providing the metadata which describes what each column in `data` contains.

## Defining Column Mappings

Column Mappings are defined using the `QbColumn` class:

```python
[
    QbColumn("The CSV Column's Title", <A Columnar Structural Definition (QbColumnStructuralDefinition)>),
    # e.g.
    QbColumn(
        "Product Name", 
        ExistingQbDimension("http://gss-data.org.uk/def/trade/property/dimension/product"),
        csv_column_uri_template="http://gss-data.org.uk/def/trade/concept-scheme/sitc-sections/{+product_name}"
    )
]
```

N.B. **All columns** contained in `data` must be defined here, and the columns must be listed in the **same order** from left to right as they appear. Columns can be supressed, see [Ignoring Columns](#ignoring-columns).

When mapping a column to a pre-existing code-list or set of attribute values, or mapping the column to a list of pre-existing measures or units, you must set the column's `csv_column_uri_template`. This property specifies how the cell values are mapped to the URIs representing the existing code-list concepts, attribute values, measures or units that you are attempting to re-use.

### URI Templates

The URI templates used by the `csv_column_uri_template` property follow the [RFC 6570](https://datatracker.ietf.org/doc/html/rfc6570) standard. The only variable name available within the template URI is the CSV-W column's `name` - this can be deduced by applying the [csvw_column_name_safe](https://github.com/GSS-Cogs/csvcubed/blob/96f37301f7eb056e6048014e4ebfcf5ded37e853/csvcubed/csvcubed/utils/uri.py#L28) transformation to the column's title.

The [csvw_column_name_safe](https://github.com/GSS-Cogs/csvcubed/blob/96f37301f7eb056e6048014e4ebfcf5ded37e853/csvcubed/csvcubed/utils/uri.py#L28) transformation essentialy says to:

* convert the column's title to lower case
* replace any non-alphanumeric characters with `_`
* de-duplicate any character strings containing more than one underscore (e.g. `hello___world` -> `hello_world`)

For example, a column with the title `Average Income (£ Sterling)` is transformed to `average_income_sterling_`.

### Ignoring Columns

It is sometimes the case that a column appears in the source CSV/dataframe that you do not wish to be serialised with the RDF cube. In this case, you can use the `SuppressedCsvColumn` class to represent this column. It will be included in the CSV-W, but will not not make it into any resulting RDF.

```python
[
    QbColumn("Useful Data", NewQbDimension.from_data("Useful Data", data["Useful Data"])),
    SuppressedCsvColumn("Irrelevant Notes Column")
]
```

## Data Structure Definitions

There are two types of structural definitions which we use in `csvcubed`: columnar structure definitions (`QbColumnStructuralDefinition`) and secondary structural definitions (`SecondaryQbStructuralDefinition`).

* `QbColumnStructuralDefinition` - A DSD Part which can define what a column in the data CSV represents.
* `SecondaryQbStructuralDefinition` - Parts of the DSD which are secondary to a parent `QbColumnStructuralDefinition`.

**N.B. Only columnar structural definitions can be set on a `QbColumn` mapping.**

### Columnar Structural Definitions

A rough structure of the available columnar structural definitions is shown below. The hierarchical/tree representation assists in selecting the which kind of column to use in the cube's column definitions.

```text
QbColumnStructuralDefinition
├── QbAttribute                         - A column where the values describe an attribute of the observed value.
│   ├── ExistingQbAttribute                 - Reuse an attribute defined elsewhere.
│   ├── NewQbAttribute                      - Define a new attribute property.
│   └── QbAttributeLiteral                  - The attribute values should be represented by a literal value instead of a URI.
│       ├── ExistingQbAttributeLiteral          - Reuse a literal attribute defined elsewhere.
│       └── NewQbAttributeLiteral               - Define a new literal attribute property.
├── QbDimension                         - The column values describe a dimension which partitions the statistical population.
│   ├── ExistingQbDimension                 - Reuse a dimension defined elsewhere.
│   └── NewQbDimension                      - Define a new dimension property.
├── QbMultiMeasureDimension             - The values describe which population characteristic was observed and is recorded in the row.
├── QbMultiUnits                        - The column values describe the unit that the row's measured/observed value was recorded in.
└── QbObservationValue                  - The column values represent observed values of some population characteristic.
    ├── QbSingleMeasureObservationValue     - All rows measure the same population characteristic in the same unit.
    └── QbMultiMeasureObservationValue      - Each row declares what its measure is (and also possibly what its unit is).
```

**Note that**:

* The above diagram **does not represent the true class hierarchy** and should be used as a guide to help decide which  `QbColumnStructuralDefinition` should be selected to describe their data-cube's structure.
* Choose the most specific structural definition in every case. If the structural definition has children, it cannot be used directly and its children must be used. (i.e. use leaf nodes only)

#### Literal vs URI

URIs represent resources which can have relationships to other resources or values. [Literals](https://www.w3.org/TR/rdf11-concepts/#section-Graph-Literal) are just plain values like a number `3.5` or a string `'elephants and other pachyderms'`.

### Secondary Structural Definitions

Secondary structural definitions are parts of the data structure definition which cannot fully describe a column in the data-cube. They are *secondary to* the column's structural definition. You only need to use these secondary definitions where they are required by the column's structural definition.

A rough structure of `SecondaryQbStructuralDefinition`s is shown below. It can be used to help you decide which secondary structural definitions you should use when describing your data-cube.

```text
SecondaryQbStructuralDefinition
├── QbAttributeValue        - Stored against the QbAttribute. Represents a (URI) value that an attribute can have.        
│   └── NewQbAttributeValue     - Define a new URI value which an attribute can hold.
├── QbCodeList              - Stored against the QbDimension. Holds a `skos:ConceptScheme` which lists the values the dimension can have.
│   ├── ExistingQbCodeList      - Reuse a code-list defined elsewhere.
│   ├── NewQbCodeList           - Define a new code-list. 
│   ├── CompositeQbCodeList     - Define a new code-list which is a composite of `skos:Concept`s defined in other code-lists.
│   └── NewQbCodeListInCsvW     - Use a code-list which is already generated and stored in a CSV-W.
├── QbConcept               - Stored against the QbCodeList. It holds a concept contained in a `skos:ConceptScheme`.
│   ├── NewQbConcept            - Define a new concept
│   └── DuplicatedQbConcept     - Reuse a concept defined elsewhere. This permits altering its label/notation/structure.
├── QbMeasure               - Stored against the QbObservation OR QbMultiMeasureDimension. Represents an observation's measure.
│   ├── ExistingQbMeasure       - Reuse a measure defined elsewhere.
│   └── NewQbMeasure            - Define a new measure.
└── QbUnit                  - Stored against the QbObservation OR QbMultiUnits. Represents an observation's unit.
    ├── ExistingQbUnit          - Reuse a unit defined elsewhere.
    └── NewQbUnit               - Define a new unit.
```

**Note that**:

* The above diagram **does not represent the true class hierarchy** and should only be used as a guide to aid in deciding which `SecondaryQbStructuralDefinition` best describes a data-cube's structure.
* Choose the most specific structural definition in every case. If the structural definition has children, it cannot be used directly and its children must be used. (i.e. use leaf nodes only)

## The `from_data` Helpers

There are a number of `from_data` helper methods on columnar structural definition classes:

* `NewQbDimension.from_data`
* `NewQbAttribute.from_data`
* `QbMultiMeasureDimension.new_measures_from_data`
* `QbMultiMeasureDimension.existing_measures_from_data`
* `QbMultiUnits.new_units_from_data`
* `QbMultiUnits.existing_units_from_data`

And there is also a helper method on the `NewQbCodeList` secondary structural definition class:

* `NewQbCodeList.from_data`

These methods accept data straight from a pandas DataFrame's column and are designed to automatically generate resources, or references to resources from the DataFrame's data. Use them where the user has not provided detailed configuration to help support the [convention over configuration](https://en.wikipedia.org/wiki/Convention_over_configuration) approach to CSV-W generation; this aims to speed the adoption of the standards for new users by reducing cognitive load.

## Validations

Each of the classes discussed above extends from the [csvcubed.models.PydanticModel](https://github.com/GSS-Cogs/csvcubed/blob/main/csvcubed/csvcubed/models/pydanticmodel.py) class. This adds [pydantic](https://pydantic-docs.helpmanual.io/) validation to csvcubed's models which ensures that all attributes have the correct type as described by their [static type annotations](https://docs.python.org/3/library/typing.html). Many of the models define [custom pydantic validators](https://pydantic-docs.helpmanual.io/usage/validators/) to add checks which are more specific than checking the overall type, e.g. `_attribute_uri_validator` inside the `ExistingQbAttribute` class in [csvcubed.models.cube.qb.components.attribute](https://github.com/GSS-Cogs/csvcubed/blob/main/csvcubed/csvcubed/models/cube/qb/components/attribute.py).

Pydantic validation can be performed on individual models by calling `pydantic_validation` (declared on [PydanticModel](https://github.com/GSS-Cogs/csvcubed/blob/main/csvcubed/csvcubed/models/pydanticmodel.py)).

### The Works

More thorough validations, including some checks on the cube's structure as a whole, as well as the validation of models against the data present can be performed with the following:

```python
from csvcubed.models.cube import *
from csvcubed.utils.qb.validation.cube import validate_qb_component_constraints
import pandas as pd

data = pd.DataFrame({
    "A Dimension": ["a", "b", "c"],
    "An Observation": [1, 2, 3]
})

cube = Cube(
    metadata=CatalogMetadata("Some Dataset Name"),
    data=data,
    columns=[
        QbColumn("A Dimension", NewQbDimension.from_data("The Dimension's Name", data["A Dimension"])),
        QbColumn(
            "An Observation",
            QbSingleMeasureObservationValue(
                measure=NewQbMeasure("Some Measure"),
                unit=NewQbUnit("Some Unit")
            )
        )
    ]
)

errors = cube.validate()
errors += validate_qb_component_constraints(cube)

if len(errors) > 0:
    print([e.message for e in errors])
    raise Exception("The cube is invalid!")
else:
    print("The cube is valid")
```
