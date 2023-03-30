# Configuring code lists

By default, csvcubed generates code lists with the unique values of each [dimension](../../../glossary/index.md#dimension)
in a data set. This makes it as quick as possible to get from data to CSV-W cube, but it doesn't always leave you with
the best representation of your code list's metadata, structure, hierarchy, or values. In order to provide more accurate
 representations of code lists, csvcubed allows users to explicitly configure code lists using JSON.

This guide details how to explicitly define a code list using csvcubed.

!!! Tip
    **Experience of writing basic JSON documents is assumed throughout this document.**
    See this [tutorial from DigitalOcean](https://www.digitalocean.com/community/tutorials/an-introduction-to-json) for
    an introduction to writing JSON.

## Defining a code list configuration file

This approach allows defining a code list in a *code list configuration file*. The following example demonstrates the
structure of a *code list configuration file*:

```json
{
  "$schema": "https://purl.org/csv-cubed/code-list-config/v1",
  "title": "Biscuit Varieties",
  "summary": "Common biscuit varieties.",
  "description": "A code list of common generic biscuit varieties available in supermarkets across the UK.",
  "creator": "http://statistics.data.gov.uk",
  "publisher": "http://statistics.data.gov.uk",
  "dataset_issued": "3000-01-01T00:00:00Z",
  "dataset_modified": "3000-01-01T00:00:00Z",
  "license": "https://creativecommons.org/licenses/by/4.0/",
  "themes": [
    "http://example.com/themes/biscuits"
  ],
  "keywords": [
    "Biscuits",
    "Tasty"
  ],
  "sort": {
    "by": "label",
    "method": "ascending"
  },
  "concepts": [
    {
      "label": "Bourbon",
      "description": "The common chocolate bourbon biscuit.",
      "notation": "BB"
    },
    {
      "label": "Custard Cream",
      "description": "The custard flavoured sandwich biscuit.",
      "notation": "CC"
    },
    {
      "label": "Digestive",
      "description": "The ever trusty digestive biscuit.",
      "notation": "DG",
      "sort_order": 0,
      "children": [
        {
          "label": "Milk Chocolate Digestive",
          "description": "The milk chocolate digestive biscuit. An improvement on the basic digestive.",
          "notation": "DG-M"
        },
        {
          "label": "Dark Chocolate Digestive",
          "description": "The dark chocolate digestive biscuit.",
          "notation": "DG-D"
        }
      ]
    }
  ]
}
```

File name: biscuit-varieties.json

This code list configuration would generate a code list with the following structure:

```text
root
├── Bourbon
├── Custard Cream
└── Digestive
    ├── Dark Chocolate Digestive
    └── Milk Chocolate Digestive
```

As can be seen in the code list configuration example, the *code list configuration file* has two sections:

1. **Metadata**
   This section is used to describe the code list's catalog information to aid discovery, provide provenance and publication information, and optionally define the scope of the code list.

2. **Concepts**
   This section is used to define and describe the concepts in a code list.

### Metadata

The following metadata can be defined in the metadata section of the *code list configuration file*:

| **field name**     | **description**                                                                                                                     | **default value**                  |
|--------------------|-------------------------------------------------------------------------------------------------------------------------------------|------------------------------------|
| `title`            | Title of the code list                                                                                                              | *none*                             |
| `description`      | Description of the contents in code list; this field supports the [markdown](https://www.markdownguide.org/getting-started/) format | *none*                             |
| `summary`          | Summary of the contents in code list                                                                                                | *none*                             |
| `creator`          | Link to the creator of the code list                                                                                                | *none*                             |
| `publisher`        | Link to the publisher of the code list                                                                                              | *none*                             |
| `dataset_issued`   | Code list issued date/time                                                                                                          | *none*                             |
| `dataset_modified` | Code list modified date/time                                                                                                        | *none*                             |
| `license`          | Link to the license of the code list                                                                                                | *none*                             |
| `themes`           | List or a single link of the theme(s) covered by the code list                                                                      | *none*                             |
| `keywords`         | List or a single string of the keywords(s) covered by the Code list                                                                 | *none*                             |
| `sort`             | Sort by (`label` or `notation`) and sort method (`ascending` or `descending`) of the code list                                      | by (`label`), method (`ascending`) |

#### Using `sort`

The `sort` field allows defining the sort `by` and sort `method` fields of the code list. The sort `by` allows defining the field used by the sorting mechanism for sorting the concepts in a code list. This field can be the concept's `label` or the `notation`. The sort `method` allows defining whether the sorting needs to be done in `ascending` or `descending` order.

*If the `sort` field is defined, the concepts without the `sort_order` (see below) will be sorted according to the sort  `by` and sort `method`. The remaining concepts which has the `sort_order` field defined will be sorted according to the `sort_order` field within each concept.*

### Concepts

The following fields can be defined for each of the concept defined in the concepts section:

| **field name** | **description**                                        | **default value** |
|----------------|--------------------------------------------------------|-------------------|
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

### Referencing a code list configuration file

This new code list can be referenced in a [qube-config.json](./index.md) file using the `code_list` field in [dimension configuration](./index.md#dimension-configuration), e.g.

```json
{
  "$schema": "https://purl.org/csv-cubed/qube-config/v1",
  "columns": {
    "Biscuit Variety": {
      "type": "dimension",
      "code_list": "./biscuit-varieties.json"
    }
  }
}
```

## Defining an in-line code list

It is also possible to define a code list configuration inside a [qube-config.json](./index.md) file.

This approach is recommended for defining simple code lists (e.g. code lists with a small number of concepts or simple hierarchy).

```json
{
  "$schema": "https://purl.org/csv-cubed/qube-config/v1",
  "title": "Biscuit Weightings",
  "summary": "The average weights of different kinds of biscuits.",
  "description": "A data set containing the average weights of a series of different kinds of biscuits. Recorded in the year 3000.",
  "license": "https://creativecommons.org/licenses/by/4.0/",
  "creator": "http://statistics.data.gov.uk",
  "publisher": "http://statistics.data.gov.uk",
  "dataset_issued": "3000-01-01T00:00:00Z",
  "keywords": [
    "Biscuits",
    "Tasty"
  ],
  "columns": {
    "Biscuit Variety": {
      "type": "dimension",
      "code_list": {
        "title": "Biscuit Varieties",
        "summary": "Common biscuit varieties.",
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "concepts": [
          {
            "label": "Bourbon",
            "description": "The common chocolate bourbon biscuit.",
            "notation": "BB"
          },
          {
            "label": "Custard Cream",
            "description": "The custard flavoured sandwich biscuit.",
            "notation": "CC"
          },
          {
            "label": "Digestive",
            "description": "The ever trusty digestive biscuit.",
            "notation": "DG",
            "sort_order": 0,
            "children": [
              {
                "label": "Milk Chocolate Digestive",
                "description": "The milk chocolate digestive biscuit. An improvement on the basic digestive.",
                "notation": "DG-M"
              },
              {
                "label": "Dark Chocolate Digestive",
                "description": "The dark chocolate digestive biscuit.",
                "notation": "DG-D"
              }
            ]
          }
        ]
      }
    }
  }
}
```

As shown in the above example, an in-line code list is defined within the `qube-config.json` using the same fields discussed above. Moreover, one can choose to define a separate code list configuration file for one dimension and define an in-line code list for another dimension.

## Code-list build command

It is possible to generate a code list CSV-W without providing a tidy-data.csv file using the `code-list build` command. Please refer to the [code-list build command documentation](../../command-line/code-list-build-command.md) page for a usage guide.
