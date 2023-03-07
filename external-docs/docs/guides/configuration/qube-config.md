# Writing a qube-config.json

This page discusses how to configure your cube with the greatest control and flexibility by writing a `qube-config.json` file. If you are new to using csvcubed, you may wish to begin with the [quick start](../../quick-start/index.md) approach.

> **Experience of writing basic JSON documents is assumed throughout this document.**
> See this [tutorial from DigitalOcean](https://www.digitalocean.com/community/tutorials/an-introduction-to-json) for an introduction to writing JSON.

The `qube-config.json` file has two sections:

1. **Metadata**
   This section is used to describe the data set's catalog information to aid discovery, provide provenance and publication information, and optionally define the scope of the data set.
2. **Column Definitions**
   This section is used to describe each column in the `.csv` file, classifying the column and defining how the column data is both represented and how it links semantically to other data.

## Metadata

A CSV-W file contains metadata which improves discoverability of data publications. In csvcubed, we use a selection of metadata entries from established namespaces to enable users to contribute to the web of data faster. The metadata fields available, their description and default values are as follows.

| **field name**             | **description**                                                                                            | **default value**                           |
|----------------------------|------------------------------------------------------------------------------------------------------------|---------------------------------------------|
| `title`                    | The title of the cube                                                                                      | A capital case version of the csv file name |
| `description`              | A description of the contents of the cube                                                                  | *none*                                      |
| `summary`                  | A summary of the data set                                                                                  | *none*                                      |
| `publisher`                | A link to the publisher of the cube                                                                        | *none*                                      |
| `creator`                  | A link to the creator of the cube                                                                          | *none*                                      |
| `themes`                   | A list of themes that describe the focus of the data                                                       | *none*                                      |
| `keywords`                 | A list or a single string of the keywords(s) covered by the data (i.e. `["trade", "energy", "imports"]`)   | *none*                                      |
| `dataset_issued`           | Date that the data set was initially published in ISO 8601 format, e.g. 2022-03-31 or 2022-03-31T12:54:30Z | *none*                                      |
| `dataset_modified`         | Date that the data set was last modified in ISO 8601 format, e.g. 2022-03-31 or 2022-03-31T12:54:30Z       | *none*                                      |
| `license`                  | URI representing the copyright [license](../linked-data/licenses.md) that applies to this cube             | *none*                                      |
| `public_contact_point_uri` | URI providing a public contact point for discussion of the data set, e.g. mailto:contact.point@example.com | *none*                                      |

See the [describing your CSV](../../quick-start/describing-csv.md) quick start for a practical guide on configuring metadata.

## Column definitions

A CSV-W file provides detailed information about the columns beyond their values. In csvcubed, we are targeting a level of detail which results in a data cube which can be be expressed using W3C's [RDF Cube Vocabulary](https://www.w3.org/TR/vocab-data-cube/). In order to be valid, a data cube must have at least one dimension, at least one observation column, along with at least one defined unit and measure. A cube may also have one or more attribute columns which provide clarification to observational data. Units and measures may be attached to the observation column (single measure cube), or appear in a column of their own (multi-measure cube).

To define a column in a `qube-config.json` file, provide the column header as a dictionary key, and create a new dictionary as the value to contain configuration properties.

A column is assumed to be a dimension unless otherwise configured using the `type` key or the column being named one of the [reserved names](../configuration/convention.md#conventional-column-names). A dimension can still have a `"type": "dimension"` key/value pair.

```json
{ ...
 "columns": {
  "Example column": {
    "type": "dimension"
  }
 }
}
```

**If a column mapping is not defined in the `qube-config.json` file for a given CSV column, the column is [configured by convention](./convention.md).**  To ignore a column and not configure it by convention, set the column's definition to `false`. This will ensure the column will not be present in the CSV-W when built by csvcubed.

```json
{ ...
 "columns": {
  "Suppressed column": false
 }
}
```

### Dimensions
<!-- Removed blockquote formatting -->
The *dimension* columns serve to identify observations in the data set. A combined set of values for all dimension components should uniquely identify a single observation value. Examples of dimensions include the time period to which the observation applies, or the geographic region which the observation covers.

Think of the principle of [MECE](https://en.wikipedia.org/wiki/MECE_principle).

See the [Dimension Configuration](#dimension-configuration) page for more information.

### Measures

> The *measure* [column] represents the phenomenon being observed.

The measure column is effectively another form of dimension.

### Attributes

> The *attribute* [column] allows us to qualify and interpret the observed value(s). This enables specification of the units of measure, any scaling factors and metadata such as the status of the observation (e.g. *estimated*, *provisional*).

The attribute column can link to [resources](../../glossary/index.md#uri) or [literals](../../glossary/index.md#literal).

### Units

The *unit* column is a type of attribute column which provides the units of the observation.

### Observations

The *observation* column contains the numeric values of the observations recorded in the data set.

### Using templates

To use or extend an existing template, provide a `"from_template": "month"` key-value pair referencing one of the [available templates](templates.md). csvcubed loads the reference template's key-value pairs making creating linked data much faster. The values for a column with a `from_template` set in `qube-config.json` override the values for the template. In the example below, the CSV contains a column called Marker, the `qube-config.json` file references the template [`observation-status`](https://purl.org/csv-cubed/qube-config/templates/observation-status.json) but csvcubed will override the template's label with the value provided.

```json
   "columns" {
      "Marker": {
         "from_template": "observation-status",
         "label": "Data Marker"
      }
   }
```

### Using existing columns

To reuse or extend existing dimensions, attributes, units, or measures, provide a `"from_existing": "uri"` key-value pair linking to the RDF subject for the component specification. csvcubed determines whether the column reuses an existing component (e.g. dimension) or requires the extension of an existing component through further configuration of the column.

```json
   "columns": {
      "reused column": {
         "type": "dimension",
         "from_existing": "https://example.org/dimension/years"
      },
      "reused and renamed column": {
         "type": "dimension",
         "from_existing": "https://example.org/dimension/flavours",
         "label": "ice cream flavours"
      }
   }
```

In the example above there are two reused dimensions. For the first existing dimension, "reused column" takes the existing dimension "years" and reuses it without any changes. The second dimension is an example of the creation of a new dimension but showing that ice-cream flavours is a child dimension of flavours.

Unless the component being reused is a literal attribute and you're providing a `"data_type"` key-value pair, any other key-value pairs provided will change the column to a new component which will extend the linked parent component.

## Shared column configuration options

There are several configuration options available across column types except observations.

| **field name**   | **description**                                                                                                           | **default value**                                                                |
|------------------|---------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| `type`           | The type of the column (Required)                                                                                         | *dimension*                                                                      |
| `label`          | The title of the column (Optional)                                                                                        | The capital case of the header in the csv file with spaces replacing underscores |
| `description`    | A description of the contents of the column (Optional)                                                                    | *none*                                                                           |
| `from_existing`  | The uri of the resource for reuse/extension (Optional)                                                                    | *none*                                                                           |
| `definition_uri` | A uri of a resource to show how the column is created/managed (i.e. a uri of a PDF explaining a list of units) (Optional) | *none*                                                                           |

The `from_existing` value when set provides the basis of linked data; it allows csvcubed to generate additional RDF-hints to allow users to discover how the `tidy_data.csv` links to other data semantically.

## Dimension Configuration

The following fields can be configured for each dimension in your data set. csvcubed will assume that a column represents a dimension if the `type` field is left blank, or explicitly specified as `dimension`.

| **field name**      | **description**                                                                                                                                                                                                                                                                                       | **default value**                                                                               |
|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| `type`              | The type of the column (Required)                                                                                                                                                                                                                                                                     | *dimension*                                                                                     |
| `from_template`     | Use a [column template](templates.md) (Optional)                                                                                                                                                                                                                                                      | *none*                                                                                          |
| `label`             | The title of the column (Optional)                                                                                                                                                                                                                                                                    | The capital case version of the column header in the csv file with spaces replacing underscores |
| `description`       | A description of the contents of the column (Optional)                                                                                                                                                                                                                                                | *none*                                                                                          |
| `from_existing`     | The uri of the resource for reuse/extension (Optional)                                                                                                                                                                                                                                                | *none*                                                                                          |
| `definition_uri`    | A uri of a resource to show how the column is created/managed (i.e. a uri of a PDF explaining a list of units) (Optional)                                                                                                                                                                             | *none*                                                                                          |
| `cell_uri_template` | **(Advanced)** Override the uri generated for values within the uri (Optional)                                                                                                                                                                                                                        | *none*                                                                                          |
| `code_list`         | Generate a code-list (true), suppress a code-list (false), file path to a [code-list-config.json](code-list-config.md#defining-a-code-list-configuration-file) (uri), [in-line code list](code-list-config.md#defining-an-in-line-code-list) (json), or link to an externally-defined code list (uri) | true                                                                                            |
<!-- TODO: uri_override not in schema -->
<!-- | `uri_override`      | Override the uri created automatically for the column (Optional) (Advanced)                                                                                                                                          | `tidy_data.csv#uri_safe_column_header_from_csv`                                  | -->

### Examples of dimension configuration

The Sweden at Eurovision data set consists of four dimensions - `Year`, `Entrant`, `Song` and `Language`. Examples of how these dimensions could be configured are as follows.

```json
"columns": {
   "Year": {
      "from_template": "year",
      "label": "Competition year",
      "code_list": "true"
   },
   "Entrant": {
      "type": "dimension",
      "description": "The act representing Sweden at Eurovision for the given year",
      "code_list": "my_eurovision_code_list_config.json"
   },
   "Song": {
      "from_existing": "http://example.org/dimension/eurovision-songs",
      "cell_uri_template": "http://example.org/code-lists/eurovision-songs/{+song}"
   },
   "Language": {
      "code_list": "false",
      "cell_uri_template": "http://example.org/code-lists/eurovision-languages/{+language}"
   }
}
```

Taking each of these dimensions one-by-one:

```json
"columns": {
   "Year": {
      "from_template": "year",
      "label": "Competition year",
      "code_list": "true"
   }
}
```

The `Year` column uses a [column template](templates.md#datetime-period-template) - doing so means that the `type`, `from_existing`, `label` and `cell_uri_template` fields will be automatically populated based on the [calendar-year.json](https://purl.org/csv-cubed/qube-config/templates/calendar-year.json) template. However, these fields can also be over-ridden, as is the case here, since the `label` has been defined as "Competition year".

A code list will be automatically generated by csvcubed for the `Year` column, since the `code_list` field has been set to `true`.


```json
"columns": {
   "Entrant": {
      "type": "dimension",
      "description": "The act representing Sweden at Eurovision for the given year",
      "code_list": "entrant_code_list_config.json"
   }
}
```

The `Entrant` column has been explicitly configured with a `type` of dimension, although strictly speaking this is unnecessary, as a column will be designated as a dimension by default if `type` is not defined.

The `description` field allows additional information to be associated with a column.

A code list will be generated by csvcubed for the `Entrant` column, based on the `entrant_code_list_config.json` file provided. See the [code list configuration](code-list-config.md#defining-a-code-list-configuration-file) page for further instructions. Alternatively, code lists can be [defined in-line](code-list-config.md#defining-an-in-line-code-list) within the `qube-config.json` itself.


```json
"columns": {
   "Song": {
      "from_existing": "http://example.org/dimension/eurovision-songs",
      "cell_uri_template": "http://example.org/code-lists/eurovision-songs/{+song}"
   },
   "Language": {
      "code_list": "false",
      "cell_uri_template": "http://example.org/eurovision-languages/{+language}"
   }
}
```

The `Song` and `Language` columns have both been configured with a `cell_uri_template` property. It is important to note that this property should only be used where the concept scheme is defined externally at an existing URI, or there is no concept scheme, but you want to point to an existing resource.

If `cell_uri_template` is specified:

**Either**:

- `from_existing` must also be defined, in which case `cell_uri_template` should refer to the concepts in the existing dimension's code list;

**Or**:

- `code_list` must be set as `false`, in which case `cell_uri_template` should refer to URIs which are existing RDF resources.

**This is considered an advanced configuration option, and therefore care must be taken to ensure that the values generated are valid.**

The format of the `cell_uri_template` value **must** follow [RFC6570](https://www.rfc-editor.org/rfc/rfc6570) guidance for URI Templates. In the case of any doubt, follow the pattern in the examples shown above (i.e. `http://example.org/some-uri/{+column_name}`), as this will ensure csvcubed safely [transforms the column header](../uris.md#csv-column-name-safe-transformation) to the CSV-W format.

<!-- TODO: Add examples of `definition_uri`, `code_list` uri -->

## Attributes Configuration

| **field name**           | **description**                                                                                                                                                                                                                                                                                                                                                                | **default value**                                                                |
|--------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| `type`                   | The type of the column; to configure an attribute column use the value `attribute` (Required)                                                                                                                                                                                                                                                                                  | *dimension*                                                                      |
| `from_template`          | Use a [column template](templates.md)                                                                                                                                                                                                                                                                                                                                          | *none*                                                                           |
| `label`                  | The title of the column (Optional)                                                                                                                                                                                                                                                                                                                                             | The capital case of the header in the csv file with spaces replacing underscores |
| `description`            | A description of the contents of the column (Optional)                                                                                                                                                                                                                                                                                                                         | *none*                                                                           |
| `from_existing`          | The uri of the resource for reuse/extension (Optional)                                                                                                                                                                                                                                                                                                                         | *none*                                                                           |
| `definition_uri`         | A uri of a resource to show how the column is created/managed (i.e. a uri of a PDF explaining a list of units) (Optional)                                                                                                                                                                                                                                                      | *none*                                                                           |
| `describes_observations` | Associates this attribute with the relevant observation values. This is only necessary for [pivoted shape data sets](../shape-data/pivoted-shape.md) with multiple observation value columns.                                                                                                                                                                                  | *none*                                                                           |
| `required`               | If this boolean value is true csvcubed will flag to the user if there are blank values in this column                                                                                                                                                                                                                                                                          | *none*                                                                           |
| `data_type`              | (Attribute Literals only) The [xml data type](https://www.w3.org/TR/xmlschema-2/#built-in-datatypes) of the contents of the column, if this is provided it becomes a Literal Attribute column (Optional)                                                                                                                                                                       | *none*                                                                           |
| `values`                 | (New Resource Attributes only) If automatically-generated attributes are desired, a boolean value of `true` is used to signify to csvcubed to create attribute resources from values in this column; otherwise this should be a dictionary defining the attributes used in the column. See [Attribute values configuration](#attribute-values-configuration) for more details. | *none*                                                                           |
| `cell_uri_template`      | (Existing Resource Attributes only) Used to define a template to map the cell values in this column to URIs                                                                                                                                                                                                                                                                    | *none*                                                                           |

## Observations Configuration

Observations are the most important component of a CSV-W data set. Observation columns can have measures and units defined against them to obviate the need for separate unit and measure columns in a single unit/measure data set.

| **field name** | **description**                                                                                                                                                                                                                                                                          | **default value** |
|----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------|
| `type`         | The type of the column; to configure an observation column use the value `observations`. **NOTE** This value is required if the observation column isn't [conventionally named](./convention.md) or required if either measure or unit columns are not part of the observation csv file. | *dimension*       |
| `data_type`    | The data type of the observations. This should generally be a decimal or integer. (Optional)                                                                                                                                                                                             | *decimal*         |
| `unit`         | The unit for this observation column; this can a uri to an existing unit, or a dictionary containing a new or extended existing unit. If there is a unit column this value must not be provided. (Optional)                                                                              | *none*            |
| `measure`      | The measure for this observation column; this can be a uri to an existing dimension, or a dictionary containing a new or extended existing measure. If there is a measure column this key must not be provided. (Optional)                                                               | *none*            |

## Measure and Unit Columns Configuration

Measure and unit columns are treated slightly differently to dimension, attribute, and observation columns. Measure and unit columns contain references to discrete units and measures. In both cases by defining `"type": "measures"` or `"type": "units"` provides the same behaviour. Do not put measures in unit columns or units in measure columns.

| **field name**           | **description**                                                                                                                                                                                                                                                                                                  | **default value** |
|--------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------|
| `type`                   | The type of the column, provide `"measures"` for the measure column type or `"units"` for the unit column (Required)                                                                                                                                                                                             | *dimension*       |
| `values`                 | (New Measures/Units only) If basic units/measures are desired, a boolean value of `true` is used to signify to csvcubed to create units/measures from values in this column; otherwise values is a dictionary which defines the units/measures using the notation from [Measures and Units](#measures-and-units) | `true`            |
| `from_template`          | (Existing Units only) Use a [column template](templates.md)                                                                                                                                                                                                                                                      | *none*            |
| `cell_uri_template`      | (Existing Measures/Units only) Used to define a template to map the cell values in this column to URIs                                                                                                                                                                                                           | *none*            |
| `describes_observations` | (Unit column only) Associates the unit column with the relevant observation values. This is only necessary for [pivoted shape data sets](../shape-data/pivoted-shape.md) with multiple observation value columns.                                                                                                | *none*            |

## Measures and Units

Measures can either be attached to a Measure Column if there are a mixture of measures in your data set, or to an Observation column if all observations in the cube have the same measure.
Units can either be attached to a Unit Column if there are a mixture of units in your data set, or to an Observation column if all observations in the cube have the same unit.

### Measures Configuration

Measures have no unique configuration options.

| **field name**   | **description**                                                                                                             | **default value** |
|------------------|-----------------------------------------------------------------------------------------------------------------------------|-------------------|
| `label`          | The title of the measure (Required; Optional if `from_existing` defined)                                                    | *none*            |
| `description`    | A description of the contents of the measure (Optional)                                                                     | *none*            |
| `from_existing`  | The uri of the resource for reuse/extension (Optional)                                                                      | *none*            |
| `definition_uri` | A uri of a resource to show how the measure is created/managed (i.e. a uri of a PDF explaining the measure type) (Optional) | *none*            |

### Units Configuration

Units are effectively attributes with additional options.

| **field name**      | **description**                                                                                                                                                                                         | **default value** |
|---------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------|
| `label`             | The title of the unit (Required; Optional if `from_existing` defined)                                                                                                                                   | *none*            |
| `description`       | A description of the contents of the unit (Optional)                                                                                                                                                    | *none*            |
| `from_existing`     | The uri of the resource for reuse/extension (Optional)                                                                                                                                                  | *none*            |
| `definition_uri`    | A uri of a resource to show how the unit is created/managed (i.e. a uri of a image which shows the formula on how the unit is derived) (Optional)                                                       | *none*            |
| `scaling_factor`    | The scaling factor (expressed in base 10) is used to define a new unit from an existing base (i.e. "GBP millions" would have a form_existing unit of GBP, and a `"scaling_factor": 1000000`) (Optional) | *none*            |
| `si_scaling_factor` | The si_scaling_factor helps relate common scaled units to source SI units, for example kilograms are 1000 grams. Most of these units are already defined. (Optional) (Advanced)                         | *none*            |
| `quantity_kind`     | The [QUDT quantity kind](http://www.qudt.org/doc/DOC_VOCAB-QUANTITY-KINDS.html#Instances) helps group units                                                                                             | *none*            |

For a more practical approach to defining units, see [configuring units](./units.md).

## Attribute Values Configuration

| **field name**   | **description**                                                             | **default value** |
|------------------|-----------------------------------------------------------------------------|-------------------|
| `label`          | The title of the attribute (Required; Optional if `from_existing` defined)  | *none*            |
| `description`    | A description of the contents of the attribute (Optional)                   | *none*            |
| `from_existing`  | The uri of the resource for reuse/extension (Optional)                      | *none*            |
| `definition_uri` | A uri of a resource to show how the attribute is created/managed (Optional) | *none*            |
