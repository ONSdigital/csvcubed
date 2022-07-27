# Writing a code-list-config.json

By default, csvcubed generates code lists with the unique values of each [dimension](../../glossary/index.md#dimension) in a data set. This makes it as quick as possible to get from data to CSV-W cube, but it doesn't always leave you with the best representation of your code list's metadata, structure, hierarchy, or values. In order to provide more accurate representations of code lists, csvcubed allows users to explicitly configure code lists using JSON. 

This guide details how to explicitly define a code list using csvcubed.

> **Experience of writing basic JSON documents is assumed throughout this document.**
> See this [tutorial from DigitalOcean](https://www.digitalocean.com/community/tutorials/an-introduction-to-json) for an introduction to writing JSON.

## Defining a code list using code-list-config.json

This approach allows defining a code list in a `code-list-config.json` file.

```json
{
  "$schema": "https://purl.org/csv-cubed/code-list-config/v1.0",
  "title": "Example code list",
  "description": "This is an example code list demonstrating how to define a code list in a json file",
  "summary": "This is an example code list",
  "creator": "http://purl.org/dc/aboutdcmi#DCMI",
  "publisher": "http://purl.org/dc/aboutdcmi#DCMI",
  "dataset_issued": "2022-03-31T12:54:30Z",
  "dataset_modified": "2022-04-01T12:54:30Z",
  "license": "https://creativecommons.org/licenses/by/4.0/",
  "themes": [
    "http://example.com/themes/theme"
  ],
  "keywords": [
    "keyword1"
  ],
  "sort": {
    "by": "label",
    "method": "ascending"
  },
  "concepts": [
    {
      "label": "A",
      "description": "A data record",
      "notation": "a",
      "same_as": "http://example.com/concepts/some-existing-concept",
      "sort_order": 2,
    },
    {
      "label": "C",
      "description": "C data record",
      "notation": "c",
      "sort_order": 1,
    },
    {
      "label": "B",
      "description": "B data record",
      "notation": "b",
      "sort_order": 0,
      "children": [
        {
          "label": "D",
          "description": "D data record",
          "notation": "d"
        }
      ]
    }
  ]
}
```

As shown in the example above, the `code-list-config.json` file has two sections:

1. **Metadata**
   This section is used to describe the code list's catalog information to aid discovery, provide provenance and publication information, and optionally define the scope of the code list.

2. **Concepts**
   This section is used to define and describe the concepts in a code list.

### Metadata

The following metadata can be defined in the metadata section of the `code-list-config.json`:

| **field name**     | **description**                                                                                | **default value**                  |
| ------------------ | ---------------------------------------------------------------------------------------------- | ---------------------------------- |
| `title`            | Title of the code list                                                                         | *none*                             |
| `description`      | Description of the contents in code list                                                       | *none*                             |
| `summary`          | Summary of the contents in code list                                                           | *none*                             |
| `creator`          | Link to the creator of the code list                                                           | *none*                             |
| `publisher`        | Link to the publisher of the code list                                                         | *none*                             |
| `dataset_issued`   | Code list issued date/time                                                                     | *none*                             |
| `dataset_modified` | Code list modified date/time                                                                   | *none*                             |
| `license`          | Link to the license of the code list                                                           | *none*                             |
| `themes`           | List or a single link of the theme(s) covered by the code list                                 | *none*                             |
| `keywords`         | List or a single string of the keywords(s) covered by the Code list                            | *none*                             |
| `sort`             | Sort by (`label` or `notation`) and sort method (`ascending` or `descending`) of the code list | by (`label`), method (`ascending`) |

#### Using `sort`

The `sort` field allows defining the sort `by` and sort `method` fields of the code list. The sort `by` allows defining the field used by the sorting mechanism for sorting the concepts in a code list. This field can be the concept's `label` or the `notation`. The sort `method` allows defining whether the sorting needs to be done in `ascending` or `descending` order.

*If the `sort` field is defined, the concepts without the `sort_order` (see below) will be sorted according to the sort  `by` and sort `method`. The remaining concepts which has the `sort_order` field defined will be sorted according to the `sort_order` field within each concept.*

### Concepts

The following fields can be defined for each of the concept defined in the concepts section:

| **field name** | **description**                                        | **default value** |
| -------------- | ------------------------------------------------------ | ----------------- |
| `label`        | Label of the concept                                   | *none*            |
| `description`  | Description of the concept                             | *none*            |
| `notation`     | Notation of the concept                                | *none*            |
| `sort_order`   | A numeric value defining the sort order of the concept | *none*            |
| `same_as`      | A link to a concept defined elsewhere                  | *none*            |
| `children`     | List of child concepts                                 | *none*            |

#### Using `sort_order`

The `sort_order` field allows sorting a code list on per concept basis.

*If both the aforementioned `sort` field and the concept's `sort_order` are defined, csvcubed first sorts the concepts with `sort_order`, and then sorts the rest of the concepts according to the `sort` field. In other words, the concept's `sort_order` field has priority over the code list's `sort` field.*

#### Using `same_as`

The `same_as` field allows using a concept defined elsewhere in the internet (e.g. [E92 concept in Geography Linked Data](http://statistics.data.gov.uk/id/statistical-geography/E92000001)).

### Linking the code-list-config.json in qube-config.json

Once the `code-list-config.json` is defined, it can be linked in the `qube-config.json` using the `code_list` field in [dimension configuration](./qube-config.md#dimension-configuration). More specifically, the path to the `code-list-config.json` needs to be given in the `code_list` field in `qube-config.json`.
## Defining an in-line code list

This approach is recommended for defining simple code lists (e.g. code lists with a small number of concepts or simple hierarchy).


```json
{
    "$schema": "https://purl.org/csv-cubed/qube-config/v1.1",
    "title": "Example cube config with an inline code list",
    "summary": "Cube config with an inline code list",
    "description": "This is an example cube config demonstrating how to define an inline code list",
    "license": "https://creativecommons.org/licenses/by/4.0/",
    "creator": "http://statistics.data.gov.uk",
    "publisher": "http://statistics.data.gov.uk",
    "dataset_issued": "2022-04-08T00:00:00Z",
    "keywords": [
        "Keyword1"
    ],
    "columns": {
        "DimensionInline": {
            "type": "dimension",
            "code_list": {
                "title": "Example of an inline code list",
                "description": "This is an inline code list defined inside a cube config",
                "summary": "This is an inline code list",
                "creator": "http://purl.org/dc/aboutdcmi#DCMI",
                "publisher": "http://purl.org/dc/aboutdcmi#DCMI",
                "dataset_issued": "2022-03-31T12:54:30Z",
                "dataset_modified": "2022-04-01T12:54:30Z",
                "license": "https://creativecommons.org/licenses/by/4.0/",
                "themes": [
                    "http://example.com/themes/theme"
                ],
                "keywords": [
                    "keyword1"
                ],
                "sort": {
                    "by": "label",
                    "method": "ascending"
                },
                "concepts": [
                    {
                        "label": "A",
                        "description": "A data record",
                        "notation": "a",
                        "sort_order": 2,
                    },
                    {
                        "label": "C",
                        "description": "C data record",
                        "notation": "c",
                        "sort_order": 1,
                    },
                    {
                        "label": "B",
                        "description": "B data record",
                        "notation": "b",
                        "sort_order": 0,
                        "children": [
                            {
                                "label": "D",
                                "description": "D data record",
                                "notation": "d"
                            }
                        ]
                    }
                ]
            },
            "DimensionJsonFile": {
                "type": "dimension",
                "code_list": "./code-list-config.json"
            },
        },
        "Value": {
            "type": "observations"
        },
        "Measure": {
            "type": "measures"
        },
        "Unit": {
            "type": "units"
        }
    }
}
```

As shown in the above example, an in-line code list is defined within the `qube-config.json` using the same fields discussed above. Moreover, as shown in the example, one can choose to define a `code-list-config.json` for a one dimension and define an in-line code list for another dimension.
