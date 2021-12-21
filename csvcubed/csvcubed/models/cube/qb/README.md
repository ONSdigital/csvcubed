# Defining a QbCube

* TODO: Do a flow diagram to help users figure out which kind of component they need for each individual column?

```text
QbStructuralDefinition              - A class which holds part of a qb:DataStructureDefinition (DSD).
├── QbColumnStructuralDefinition        - A DSD Part which can define what a column in the data CSV represents.
└── SecondaryQbStructuralDefinition     - All other parts of the DSD.
```

## Column Structrual Definitions

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
├── QbMultiMeasureDimension             - Each value describes which population characteristic was observed and is recorded in the row.
├── QbMultiUnits                        - The column values describe the unit that the row's measure was recorded in.
└── QbObservationValue                  - The column values represent observed values of some population characteristic.
    ├── QbSingleMeasureObservationValue     - All rows measure the same population characteristic in the same unit.
    └── QbMultiMeasureObservationValue      - Each row declares what its measure is (and also possibly what its unit is).
```

## Secondary Structural Definitions

```text
SecondaryQbStructuralDefinition
├── QbAttributeValue
│   └── NewQbAttributeValue
├── QbCodeList
│   ├── CompositeQbCodeList
│   ├── ExistingQbCodeList
│   ├── NewQbCodeList
│   └── NewQbCodeListInCsvW
├── QbConcept
│   ├── DuplicatedQbConcept
│   ├── ExistingQbConcept
│   └── NewQbConcept
├── QbMeasure
│   ├── ExistingQbMeasure
│   └── NewQbMeasure
└── QbUnit
    ├── ExistingQbUnit
    └── NewQbUnit
```
