# Defining a QbCube

This file serves as an introduction to how the `Qb` components in csvcubed should be used. It will give you a rough breakdown of what the purpose of each component is as well as where it should be used.

Note that it is generally supposed that the `Qb` cube classes are (and should always be) the back-end way we represent and validate data cubes before they are serialised to CSV-Ws. Hence, all classes are designed and structured to be clearly named, specific in their purpose and readily composable; they are generally **unsuitable for direct use by an end-user**. These classes are designed to be used by a **specialised user interface which is targetted to the needs and capabilities of a specific type of user**, e.g. a declarative JSON document for experts who need full control or a wizard-style GUI for people who just need to publish something simple.

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

**The catalog metadata** - holds the catalog metadata which should describe what the cube contains, who published it, when it was published and how the data is licensed. See [here](https://github.com/GSS-Cogs/dataengineer-walkthrough/blob/master/csvcubed-usage/Generating%20Catalog%20Metadata.md#how-to-generate-catalog-metadata) for a discussion on ways of configuring the catalog metadata.

**The data** - holds the actual data associated with the cube (as a pandas DataFrame). This is technically optional, however your life is generally easier if you can provide it since we can perform additional validations on your cube.

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

N.B. You must list the columns **in the order** in which they are present in the `data` dataframe. You must also provide mappings for *every* column defined in your dataframe.

When mapping a column to a pre-existing code-list or set of attribute values, or mapping the column to a list of pre-existing measures or units, you must set the column's `csv_column_uri_template`. This property specifies how the cell values are mapped to the URIs representing the existing code-list concepts, attribute values, measures or units that you are attempting to re-use.

### URI Templates

The URI templates used by the `csv_column_uri_template` property follow the [RFC 6570](https://datatracker.ietf.org/doc/html/rfc6570) standard. The variable names available within the template URI are the CSV-W column's `name` - this can be deduced by applying the [csvw_column_name_safe](https://github.com/GSS-Cogs/csvcubed/blob/96f37301f7eb056e6048014e4ebfcf5ded37e853/csvcubed/csvcubed/utils/uri.py#L28) transformation to the column's title.

The [csvw_column_name_safe](https://github.com/GSS-Cogs/csvcubed/blob/96f37301f7eb056e6048014e4ebfcf5ded37e853/csvcubed/csvcubed/utils/uri.py#L28) transformation essentialy says to:

* convert the column's title to lower case
* replace any non-alphanumeric characters with `_`
* de-duplicate any character strings containing more than one underscore (i.e. `hello___world` -> `hello_world`)

e.g. a column with the title `Average Income (£ Sterling)` is transformed to `average_income_sterling_`.

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
* `SecondaryQbStructuralDefinition` - Parts of the DSD which are secondary to a parent QbColumnStructuralDefinition.

**N.B. Only columnar structural definitions can be set on a `QbColumn` mapping.**

### Columnar Structrual Definitions

A rough structure of the available columnar structural definitions is shown below. The hierarchical/tree representation has been chosen to help you decide which kind of column to use in your column definitions when defining a cube.

```text
QbColumnStructuralDefinition
├── QbAttribute                         - A column where the values describe an attribute of the observed value.
│   ├── ExistingQbAttribute                 - We can reuse an attribute someone else has defined.
│   ├── NewQbAttribute                      - We want/need to define a new attribute property.
│   └── QbAttributeLiteral                  - The attribute values should be represented by a literal value instead of a URI.
│       ├── ExistingQbAttributeLiteral          - We can reuse a literal attribute someone else has defined.
│       └── NewQbAttributeLiteral               - We want/need to define a new literal attribute property.
├── QbDimension                         - The column values describe a dimension which partitions the statistical population.
│   ├── ExistingQbDimension                 - We can reuse a dimension someone else has defined.
│   └── NewQbDimension                      - We want/need to define a new dimension property.
├── QbMultiMeasureDimension             - The values describe which population characteristic was observed and is recorded in the row.
├── QbMultiUnits                        - The column values describe the unit that the row's measured/observed value was recorded in.
└── QbObservationValue                  - The column values represent observed values of some population characteristic.
    ├── QbSingleMeasureObservationValue     - All rows measure the same population characteristic in the same unit.
    └── QbMultiMeasureObservationValue      - Each row declares what its measure is (and also possibly what its unit is).
```

**Note that**:

* The above diagram **does not represent the true class hierarchy** and should be used as a guide to help the lay-user decide which  `QbColumnStructuralDefinition` should be selected to describe their data-cube's structure.
* When choosing which structural definition to use, you must pick the most specific one. If the type you want to use has descendents then you must select one of its children. (i.e. you must pick a leaf node)

#### Literal vs URI

URIs represent resources which can have relationships to other resources or values. [Literals](https://www.w3.org/TR/rdf11-concepts/#section-Graph-Literal) are just plain values like a number `3.5` or a string `'elephants and other pachyderms'`.

### Secondary Structural Definitions

Secondary structural definitions are parts of the data structure definition which cannot fully describe a column in the data-cube. They are *secondary to* the column's structural definition. You only need to use these secondary definitions where they are required by the column's structural definiton.

A rough structure of `SecondaryQbStructuralDefinition`s is shown below. It can be used to help you decide which secondary structural definitions you should use when describing your data-cube.

```text
SecondaryQbStructuralDefinition
├── QbAttributeValue        - Stored against the QbAttribute. Represents a (URI) value that an attribute can have.        
│   └── NewQbAttributeValue     - We want/need to define a new URI value which an attribute can hold.
├── QbCodeList              - Stored against the QbDimension. Holds a `skos:ConceptScheme` which lists the values the dimension can have.
│   ├── ExistingQbCodeList      - We want to reuse a code-list defined elsewhere.
│   ├── NewQbCodeList           - We want/need to define a new code-list   
│   ├── CompositeQbCodeList     - We want/need to define a new code-list which is a composite of `skos:Concept`s defined in other code-lists.
│   └── NewQbCodeListInCsvW     - We want/need to define a new code-list which we have already generated and stored in a CSV-W.
├── QbConcept               - Stored against the QbCodeList. It holds a concept contained in a `skos:ConceptScheme`.
│   ├── NewQbConcept            - We want/need to define a new concept
│   └── DuplicatedQbConcept     - We want to reuse a concept defined elsewhere. We can alter its label/notation/structure.
├── QbMeasure               - Stored against the QbObservation OR QbMultiMeasureDimension. Represents an observation's measure.
│   ├── ExistingQbMeasure       - We want to reuse a measure defined elsewhere.
│   └── NewQbMeasure            - We want/need to define a new measure.
└── QbUnit                  - Stored against the QbObservation OR QbMultiUnits. Represents an observation's unit.
    ├── ExistingQbUnit          - We want to reuse a unit defined elsewhere.
    └── NewQbUnit               - We want/need to define a new unit.
```

**Note that**:

* The above diagram **does not represent the true class hierarchy** and should be interpreted as a guide to help the lay-user decide which `SecondaryQbStructuralDefinition` best describes their data-cube's structure.
* When choosing which structural definition to use, you must pick the most specific one. If the type you want to use has descendents then you must select one of its children. (i.e. you must pick a leaf node)

## The `from_data` Helpers

There are a number of `from_data` helper methods on columnar structrual definition classes:

* `NewQbDimension.from_data`
* `NewQbAttribute.from_data`
* `QbMultiMeasureDimension.new_measures_from_data`
* `QbMultiMeasureDimension.existing_measures_from_data`
* `QbMultiUnits.new_units_from_data`
* `QbMultiUnits.existing_units_from_data`

And there is also a helper method on the `NewQbCodeList` secondary structural definition class:

* `NewQbCodeList.from_data`

These methods accept data straight from a pandas DataFrame's column and are designed to speed up the user by automatically generating resources, or references to resources. Use them where the user has not provided detailed configuration to help support the [convention over configuration](https://en.wikipedia.org/wiki/Convention_over_configuration) approach to CSV-W generation; this is an attempt to lower the cognative load on new users.

## Validations

Each of the classes discussed above extends from the [csvcubed.models.PydanticModel](https://github.com/GSS-Cogs/csvcubed/blob/main/csvcubed/csvcubed/models/pydanticmodel.py) class. This adds [pydantic](https://pydantic-docs.helpmanual.io/) validation to our models which ensures that all attributes have the correct type as decribed by their [static type annotations](https://docs.python.org/3/library/typing.html). Many of the models use the [pydantic custom validator](https://pydantic-docs.helpmanual.io/usage/validators/) functionality to add checks which are more specific than checking the overall type, e.g. `_attribute_uri_validator` inside the `ExistingQbAttribute` class in [csvcubed.models.cube.qb.components.attribute](https://github.com/GSS-Cogs/csvcubed/blob/main/csvcubed/csvcubed/models/cube/qb/components/attribute.py).

Pydantic validation can be performed on individual models by calling `pydantic_validation` (declared on [PydanticModel](https://github.com/GSS-Cogs/csvcubed/blob/main/csvcubed/csvcubed/models/pydanticmodel.py)).

### The Works

More thorough validations, including some checks on the cube's structure as a whole, as well as validation of models against the data present can be performed with the following:

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
