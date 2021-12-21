# Defining a QbCube

* TODO: Do a flow diagram to help users figure out which kind of component they need for each individual column?

```text
QbStructuralDefinition
├── QbColumnStructuralDefinition
└── SecondaryQbStructuralDefinition
```

## Column Structrual Definitions

```text
QbColumnStructuralDefinition
├── QbAttribute
│   ├── ExistingQbAttribute
│   ├── NewQbAttribute
│   └── QbAttributeLiteral
│       ├── ExistingQbAttributeLiteral
│       └── NewQbAttributeLiteral
├── QbDimension
│   ├── ExistingQbDimension
│   └── NewQbDimension
├── QbMultiMeasureDimension
├── QbMultiUnits
└── QbObservationValue
    ├── QbMultiMeasureObservationValue
    └── QbSingleMeasureObservationValue
```

## Secondary Structural Definitions

```text
SecondaryQbStructuralDefinition
├── QbAttributeValue
│   └── NewQbAttributeValue
├── QbCodeList
│   ├── CompositeQbCodeList
│   ├── ExistingQbCodeList
│   ├── NewQbCodeList
│   └── NewQbCodeListInCsvW
├── QbConcept
│   ├── DuplicatedQbConcept
│   ├── ExistingQbConcept
│   └── NewQbConcept
├── QbMeasure
│   ├── ExistingQbMeasure
│   └── NewQbMeasure
└── QbUnit
    ├── ExistingQbUnit
    └── NewQbUnit
```