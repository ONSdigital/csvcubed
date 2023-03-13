# Catalog Metadata

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
