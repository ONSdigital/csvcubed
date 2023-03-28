# Overview

This page discusses how to configure your cube with the greatest control and flexibility by writing a `qube-config.json` file.

If you are new to using csvcubed, you may wish to begin with the [quick start](../../quick-start/index.md) approach.

This page will introduce the sections and components that make up a `qube-config.json` file, detailing the overall structure expected in the configuration file. This page will not go into extensive detail on the metadata, individual columns, and fields contained within that are required in a configuration file. Instead, each section will link to a dedicated page for the full details on the respective subject.

> **Experience of writing basic JSON documents is assumed throughout this document.**
> See this [tutorial from DigitalOcean](https://www.digitalocean.com/community/tutorials/an-introduction-to-json) for an introduction to writing JSON.

The `qube-config.json` file has two sections:

1. [**Metadata**](./metadata.md)
   This section is used to describe the data set's catalog information to aid discovery, provide provenance and publication information, and optionally define the scope of the data set.
2. [**Column Definitions**](./column-definitions.md)
   This section is used to describe each column in the `.csv` file, classifying the column and defining how the column data is both represented and how it links semantically to other data.

## Metadata

A CSV-W file contains metadata which improves discoverability of data publications. In csvcubed, we use a selection of metadata entries from established namespaces to enable users to contribute to the web of data faster.

For a detailed look at what fields can be configured when creating metadata for a `qube-config.json`, see the
[metadata](../configuration/metadata.md) page.

The metadata of the `qube-config.json` should be defined at the top of the file. Provide the metadata fields that you wish to describe your data with, and populate them by entering the field contents in quotation marks. Keep in mind that your metadata can contain any combination or variety of the possible fields, you do not have to provide all of them.

The JSON below shows a basic example of what a metadata section of a `qube-config.json` file can look like with some of its fields filled in.

```json
{
    "$schema": "https://purl.org/csv-cubed/qube-config/v1",
    "title": "Sweden at Eurovision",
    "summary": "List of Swedish entries to the Eurovision Song Contest since 1958.",
    "description": "Sweden has been competing in Eurovision since 1958, with an enviable track record of wins. This dataset covers all contests since 1958, their artists, the song names, language (if mono-lingual), and some observations covering points in final, rank in final, and number of artists on stage. Data originally sourced from https://en.wikipedia.org/w/index.php?title=Sweden_in_the_Eurovision_Song_Contest&oldid=1081060799 and https://sixonstage.com/",
    "license": "https://creativecommons.org/licenses/by/4.0/",
    "publisher": "https://www.gov.uk/government/organisations/office-for-national-statistics",
    "creator": "https://www.gov.uk/government/organisations/office-for-national-statistics",
    "dataset_issued": "2022-04-08T00:00:00Z",
    "dataset_modified": "2022-04-08T00:00:00Z",
    "keywords": [
        "Eurovision",
        "Song Contest",
        "Sweden",
        "European Broadcasting Union"
    ],
...
}
```

## Column definitions

After the configuration file's metadata section, the column definitions section should describe each column contained in the `.csv` file, identifying what type of column it is and how the column content is represented in the data set.

Each of the allowed column types can have differing combinations of properties provided to describe them, allowing basic configurations with automatically generated values, minimal simple configurations, or detailed configurations with several optional properties.

The column types that can be configured in a `qube-config.json` file are:

1. Dimensions

   See the [Dimensions Columns](./columns/dimensions.md) page for more information on configuring dimensions columns.

2. Observations

   See the [Observation Columns](./columns/observations.md) page for more information on configuring observation columns.

3. Measures

   See the [Measures Columns](./columns/measures.md) page for more information on configuring measures columns.
   See the [Measure Configuration](./measure-configuration.md) page for more information on configuring measures themselves.

4. Units

   See the [Units Columns](./columns/units.md) page for more information on configuring units columns.
   See the [Unit Configuration](./unit-configuration.md) page for more information on configuring units themselves.

5. Attributes

   Attributes can either be [resources](../../glossary/index.md#resource) or [literals](../../glossary/index.md#literal).

   See the [Resources Attribute](./columns/attribute-literals.md) page for more information on configuring Resources attribute columns.
   See the [Literals Attribute](./columns/attribute-literals.md) page for more information on configuring Literals attribute columns.
   For more information on defining these columns in a `qube-config.json` file, see the [Column definitions](./column-definitions.md) page.

### Creating a new column

Begin the columns section of the `qube-config.json` file by creating a `"columns"` object. From here, you can define columns as JSON objects where the column name is the object key, containing the column's properties. A basic example of two columns being created showing the structure of column definitions is shown below:

```json
{ ...
   "columns": {
      "Year": {
         "type": "dimension"
      },
      "Region": {
         "type": "dimension",
         "label": "Geographic region"
      }
   }
}
```

The first column in the configuration is called "Year" and the second column is called "Region". The first field that is provided when defining the column should be the `type`, to indicate what this column will represent. Following this, the other properties of the column that are accepted by this column type can be given, separated by commas. For example, the "Region" column specifies that the column represents a dimension, and it is then given the label "Geographic region".

Note this is a very basic example, viewing the [Column definitions](./column-definitions.md) page or the individual column type pages is recommended for more detail.

### Using existing columns

You may also re-use existing column definitions for the available column types if you do not wish to create your own. To reuse or extend existing dimensions, attributes, units, or measures, provide a `"from_existing": "uri"` key-value pair linking to the RDF subject for the component specification. csvcubed determines whether the column reuses an existing component (e.g. a dimension) or requires the extension of an existing component through further configuration of the column.

```json
{ ...
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
}
```

In the example above there are two reused dimensions. For the first existing dimension, "reused column" takes the existing dimension "years" and reuses it without any changes. The second dimension is an example of the creation of a new dimension but showing that ice-cream flavours is a child dimension of flavours.

Unless the component being reused is a literal attribute and you're providing a `"data_type"` key-value pair, any other key-value pairs provided will change the column to a new component which will extend the linked parent component.
