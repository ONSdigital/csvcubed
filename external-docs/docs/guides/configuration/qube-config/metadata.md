# Metadata

A CSV-W file contains metadata which improves discoverability of data publications. In csvcubed, we use a selection of metadata entries from established namespaces to enable users to contribute to the web of data faster. The metadata fields available, their description and default values are as shown in the [table](#metadata-fields) at the bottom of the page.

The following is an example of a metadata section from a `qube-config.json` about Eurovision performances by Sweden, that uses all of the possible fields.

```json
{
    "$schema": "https://purl.org/csv-cubed/qube-config/v1",
    "title": "Sweden at Eurovision",
    "summary": "List of Swedish entries to the Eurovision Song Contest since 1958.",
    "description": "Sweden has been competing in Eurovision since 1958, with an enviable track record of wins. This dataset covers all contests since 1958, their artists, the song names, language (if mono-lingual), and some observations covering points in final, rank in final, and number of artists on stage. Data originally sourced from https://en.wikipedia.org/w/index.php?title=Sweden_in_the_Eurovision_Song_Contest&oldid=1081060799 and https://sixonstage.com/",
    "license": "https://creativecommons.org/licenses/by/4.0/",
    "public_contact_point_uri": "mailto:swedensongscontact@example.com",
    "themes": ["http://example.com/themes/sweden-eurovision"],
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

Note how some field contents must be given in square brackets [] as a list, such as `keywords` or `themes`.

You do not have to provide all fields for the metadata to be valid, but you should provide a `$schema` so that csvcubed can recognise the file.

## Metadata fields

| **field name**             | **description**                                                                                                                      | **default value**                           |
|----------------------------|--------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------|
| `title`                    | The title of the cube                                                                                                                | A capital case version of the CSV file name |
| `description`              | A description of the contents of the cube; this field supports the [markdown](https://www.markdownguide.org/getting-started/) format | *none*                                      |
| `summary`                  | A summary of the data set                                                                                                            | *none*                                      |
| `publisher`                | A link to the publisher of the cube                                                                                                  | *none*                                      |
| `creator`                  | A link to the creator of the cube                                                                                                    | *none*                                      |
| `themes`                   | A list of themes that describe the focus of the data                                                                                 | *none*                                      |
| `keywords`                 | A list or a single string of the keywords(s) covered by the data (i.e. `["trade", "energy", "imports"]`)                             | *none*                                      |
| `dataset_issued`           | Date that the data set was initially published in ISO 8601 format, e.g. 2022-03-31 or 2022-03-31T12:54:30Z                           | *none*                                      |
| `dataset_modified`         | Date that the data set was last modified in ISO 8601 format, e.g. 2022-03-31 or 2022-03-31T12:54:30Z                                 | *none*                                      |
| `license`                  | URI representing the copyright [license](../../linked-data/licenses.md) that applies to this cube                                    | *none*                                      |
| `public_contact_point_uri` | URI providing a public contact point for discussion of the data set, e.g. mailto:contact.point@example.com                           | *none*                                      |

See the [describing your CSV](../../../quick-start/describing-csv.md) quick start for a practical guide on configuring metadata.
