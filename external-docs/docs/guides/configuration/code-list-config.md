# Writing a code-list-config.json

In addition to the [configuration by convention approach](convention.md), csvcubed allows users to define a code list using a `code-list-config.json` file, and define an in-line code list within the `qube-config.json` file. This page discusses how to configure code lists using these two approaches.

> **Experience of writing basic JSON documents is assumed throughout this document.**
> See this [tutorial from DigitalOcean](https://www.digitalocean.com/community/tutorials/an-introduction-to-json) for an introduction to writing JSON.

## Defining a code list using `code-list-config.json`

This approach allows defining a code list in a `code-list-config,json` that conforms to the rules defined in the [csvcubed code list configuration json schema](https://purl.org/csv-cubed/code-list-config/v1).

The `code-list-config.json` file has two sections:

1. **Metadata**
   This section is used to describe the code list's catalog information to aide discovery, provide provinance and publication information, and optionally define the scope of the code list.

2. **Concepts**
   This section is used to define and descripts the concepts of a code list.

### Metadata

The following metadata can be defined in the metadata section of the `code-list-config.json`:

| **field name**     | **description**                                                                                              | **default value**                  |
|--------------------|--------------------------------------------------------------------------------------------------------------|------------------------------------|
| `title`            | Title of the code list                                                                                       | *none*                             |
| `description`      | Description of the contents in code list                                                                     | *none*                             |
| `summary`          | Summary of the contents in code list                                                                         | *none*                             |
| `creator`          | a link to the creator of the cube                                                                            | *none*                             |
| `publisher`        | a link to the publisher of the cube                                                                          | *none*                             |
| `dataset_issued`   | the data set issued date/time                                                                                | *none*                             |
| `dataset_modified` | the data set modified date/time                                                                              | *none*                             |
| `license`          | a link to the license of the cube                                                                            | *none*                             |
| `themes`           | a list or a single link of the theme(s) covered by the data                                                  | *none*                             |
| `keywords`         | a list or a single string of the keywords(s) covered by the data                                             | *none*                             |
| `sort`             | the sort by (i.e. `label` or `notation`) and sort method (i.e. `ascending` or `descending`) of the code list | by (`label`), method (`ascending`) |

#### Using `sort`

The `sort` field allows defining the sort `by` and sort `method` fields of the code list. The sort `by` allows defining the field used by the sort mechanism for sorting. This field can be the concept's `label` or the `notation`. The sort `method` allows defining whether the sorting needs to be done as `ascending` or `descending`.

*If the `sort` field is defined, the concepts without the `sort_order` (see below) will be sorted according to the sort  `by` and sort `method`.*

### Concepts

The following fields can be defined for each of the concept defined in the concepts section:

| **field name** | **description**                                        | **default value** |
|----------------|--------------------------------------------------------|-------------------|
| `label`        | Label of the concept                                   | *none*            |
| `description`  | Description of the concept                             | *none*            |
| `notation`     | Notation of the concept                                | *none*            |
| `sort_order`   | A numeric value defining the sort order of the concept | *none*            |
| `same_as`      | A link to a concept defined elsewhere                  | *none*            |

#### Using `sort_order`

The `sort_order` field allows users sort code list on per concept basis. For example, one can define `sort_order` of 0 and 1 to the last two concepts to make these concepts appear at the top of the code list.

*If the aforementioned `sort` field and the concept's `sort_order` defined, csvcubed first sort the concepts with `sort_order` and then applies the sorting to the rest of the concepts. In other words, the concept's `sort_order` has priority over the code list's `sort` field.*

#### Using `same_as`

The `same_as` field allows using a concept defined elsewhere in the internet.

### Example

## Defining an in-line code list

This approach is recommended to use for defining simple code lists (e.g. non-hierachical code lists).