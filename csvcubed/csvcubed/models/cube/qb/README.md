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
        QbColumn("A Dimension", NewQbDimension.from_data(data["A Dimension"])),
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

todo: Need to discuss the use of the `QbColumn` class including use of the `csv_column_template_uri` property.

todo: Mention using the `SuppressedCsvColumn` type.

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

todo: Describe the difference between literal values and URI values in RDF.

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

todo: Discuss where and how to use the `from_data` helper methods.

## Validations

todo: Discuss what we typically validate in these structural definitions.

todo: Discuss how to initiate the relevant validations against a cube.
