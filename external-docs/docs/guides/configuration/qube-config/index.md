# Explicit cube configuration

This page discusses how to configure your cube with the greatest control and flexibility by writing a `qube-config.json` file.

If you are new to using csvcubed, you may wish to begin with the [quick start](../../../quick-start/index.md) approach.

This page will introduce the main components that make up a `qube-config.json` file, then provide you with links to
explore more advanced configuration.

!!! Tip
    **Experience of writing basic JSON documents is assumed throughout this document.**
    See this [tutorial from DigitalOcean](https://www.digitalocean.com/community/tutorials/an-introduction-to-json) for
    an introduction to writing JSON.

A `qube-config.json` file has two primary sections:

1. [**Metadata**](#metadata)
   This section is used to describe the data set's catalog information to aid discovery and to provide provenance and
   publication information.
2. [**Column Definitions**](#column-definitions)
   This section is used to describe each column in the CSV file; each column is classified, and optionally linked to
   existing data definitions.

## Metadata

All csvcubed outputs contain metadata which makes it easier to discover data publications. We use definitions from
established vocabularies to enable you to contribute faster to the web of data.

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
    ]
}
```

Remember that you don't have to set everything; many of the fields are optional, but you should **always include the
`$schema` property** so that csvcubed can recognise the file.

More information on how to configure metadata can be found on the [Metadata](./metadata.md) page

## Column definitions

> For a more detailed introduction on how to configure column definitions, see the
> [Column definitions](./columns/index.md) page.

After the configuration file's metadata section, the column definitions section should describe some or all of the
columns defined in your CSV file. This helps csvcubed understand what type of columns you're using and whether there's
anything missing.

Configuring the types of each of your columns is relatively straightforward. The following data set can be correctly
configured with the JSON below it.

| Location  | Year | Average Badger Weight / kg |
|:----------|:-----|---------------------------:|
| Sheffield | 1996 | 9.6                        |
| Carlisle  | 1994 | 10.5                       |

```json
{
    "$schema": "https://purl.org/csv-cubed/qube-config/v1",
    "title": "Badger weight watch",
    "columns": {
      "Location": {
         "type": "dimension"
      },
      "Year": {
         "type": "dimension"
      },
      "Average Badger Weight / kg": {
         "type": "observations",
         "measure": {
            "label": "Average Badger Weight"
         },
         "unit": {
            "label": "kg"
         }
      }
    }
}
```

More information on how to configure columns can be found on the [Column definitions](./columns/index.md) page.
