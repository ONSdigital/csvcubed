# Dimension columns

This page discusses what a dimension column is, when one should be used, and how one can be defined.

> For a detailed look at a dimension column's configuration options, see the [Reference table](#reference) at the bottom of this page.

## What is a dimension column?

A dimension column serves to identify the observations in a data set. In order to be valid, a data cube must include at least one dimension column; however, in practice, it is likely that your data set will contain more than one dimension. A combined set of dimension values (including measures) should uniquely identify each observation in the data set. Examples of dimensions include the time period to which the observation applies, or the geographic region which the observation covers.

## When to use one

Dimensions are the fundamental building blocks of your data set, and as such your data set must always include at least one dimension. Given that the goal of the csvcubed project is to simplify the process of creating [5-star linked data](https://5stardata.info/en/) from CSV files, proper configuration of the dimensions in your data set is a good way to start publishing linked data.

## Basic configuration

By default, csvcubed will designate a column as a dimension if the `type` field is left blank. It is also possible to explicitly designate the column as a dimension by setting the column's `type` field as "dimension". The following examples are therefore equivalent:

```json
{ ...
   "columns": {
      "Column title" {
         "type": "dimension",
         "label": "The title of the column",
         "description": "A description of the contents of the column"
      }
   }
}
```

```json
{ ...
   "columns": {
      "Column title" {
         "label": "The title of the column",
         "description": "A description of the contents of the column"
      }
   }
}
```

## Code list configuration

One of the key principles of linked data is the ability to connect data sets via references to common concepts. These concepts can be formalised through the use of code lists. By default, csvcubed will generate code lists for each of the dimensions in your data set. However, there are several configuration options for refining how your code lists are generated and expressed. Full details can be found on the [Code list configuration](../code-list-config.md) page.

<!-- Some examples are provided below.

### Code list configuration file

```json
{ ...
   "columns": {
      "Entrant": {
         "type": "dimension",
         "description": "The act representing Sweden at Eurovision for the given year",
         "code_list": "entrant_code_list_config.json"
      }
   }
}
```

### In-line code list

```json
{ ...
   "columns": {
      "Entrant": {
         "type": "dimension",
         "description": "The act representing Sweden at Eurovision for the given year",
         "code_list": {
            "title": "title",
            "concepts": [
               {
                  "label": "label",
                  "description": "description",
                  "notation": "notation"
               },
               {
                  "label": "label",
                  "description": "description",
                  "notation": "notation"
               },
               {
                  "label": "label",
                  "description": "description",
                  "notation": "notation"
               }
            ]
         }
      }
   }
}
```

### Code list URI

```json
{ ...
   "columns": {
      "Entrant": {
         "type": "dimension",
         "description": "The act representing Sweden at Eurovision for the given year",
         "code_list": "http://example.org/code-lists/eurovision-acts"
      }
   }
}
``` -->

## Dimension column templates

```json
{ ...
   "columns": {
      "Year": {
         "from_template": "year",
         "label": "Competition year"
      }
   }
}
```

The `Year` column defined above uses a [column template](../templates.md) - doing so means that the `type`, `from_existing`, `label` and `cell_uri_template` fields will be automatically populated based on the [calendar-year.json](https://purl.org/csv-cubed/qube-config/templates/calendar-year.json) template. However, these fields can also be overridden, as is the case here, since the `label` has been defined as "Competition year".

## Advanced configuration
### Cell URI templates

**The use of the `cell_uri_template` field is considered an advanced configuration option, and therefore care must be taken to ensure that the values generated are valid.**

```json
{ ...
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
}
```

The `Song` and `Language` columns have both been configured with a `cell_uri_template` field. It is important to note that this field should only be used where the concept scheme is defined externally at an existing URI, or there is no concept scheme, but you want to point to an existing resource to provide additional context about the dimension's value.

If `cell_uri_template` is specified:

**Either**:

- `from_existing` must also be defined, in which case `cell_uri_template` should refer to the concepts in the existing dimension's code list;

**Or**:

- `code_list` must be set as `false`, in which case `cell_uri_template` should refer to URIs which are existing RDF resources.

The format of the `cell_uri_template` value **must** follow [RFC6570](https://www.rfc-editor.org/rfc/rfc6570) guidance for URI Templates. In the case of any doubt, follow the pattern in the examples shown above (e.g. `http://example.org/some-uri/{+column_name}`), as this will ensure csvcubed safely [transforms the column header](../../uris.md#csv-column-name-safe-transformation) to the CSV-W format.

<!-- The [Sweden at Eurovision data set](../../../quick-start/designing-csv.md#adding-your-data) consists of four dimensions - `Year`, `Entrant`, `Song` and `Language`. Examples of how these dimensions could be configured are as follows.

```json
{ ...
   "columns": {
      "Year": {
         "from_template": "year",
         "label": "Competition year"
      },
      "Entrant": {
         "type": "dimension",
         "description": "The act representing Sweden at Eurovision for the given year",
         "definition_uri": "http://example.org/swedish-eurovision-acts",
         "code_list": "my_eurovision_code_list_config.json"
      },
      "Song": {
         "from_existing": "http://example.org/dimension/eurovision-songs",
         "cell_uri_template": "http://example.org/code-lists/eurovision-songs/{+song}"
      },
      "Language": {
         "code_list": "false",
         "cell_uri_template": "http://example.org/eurovision-languages/{+language}"
      }
   }
}
``` -->


<!-- ## Code list options

```json
{ ...
   "columns": {
      "Entrant": {
         "type": "dimension",
         "description": "The act representing Sweden at Eurovision for the given year",
         "definition_uri": "http://example.org/swedish-eurovision-acts",
         "code_list": "entrant_code_list_config.json"
      }
   }
}
```

The `definition_uri` allows you to point to a human-readable resource that further defines the dimension values, such as a PDF document.

A code list will be generated by csvcubed for the `Entrant` column, based on the `entrant_code_list_config.json` file provided. See the [code list configuration](../code-list-config.md#defining-a-code-list-configuration-file) page for further instructions. Alternatively, code lists can be [defined in-line](../code-list-config.md#defining-an-in-line-code-list) within the `qube-config.json` itself, or can point to a uri by setting `"code_list": "uri"`. -->

## Reference

This table shows a list of the possible fields that can be entered when configuring a dimension.

| **field name**      | **description**                                                                                                                                                                                                                                                                                       | **default value**                                                                               |
|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| `type`              | The type of the column. This can be left blank to configure a column as a dimension by default.                                                                                                                                                                                                       | *dimension*                                                                                     |
| `label`             | The title of the column (Optional)                                                                                                                                                                                                                                                                    | The capital case version of the column header in the csv file with spaces replacing underscores |
| `description`       | A description of the contents of the column (Optional)                                                                                                                                                                                                                                                | *none*                                                                                          |
| `from_template`     | Use a [column template](../templates.md) (Optional)                                                                                                                                                                                                                                                   | *none*                                                                                          |
| `from_existing`     | The uri of the resource for reuse/extension (Optional)                                                                                                                                                                                                                                                | *none*                                                                                          |
| `code_list`         | Generate a code-list (true), suppress a code-list (false), file path to a [code-list-config.json](../code-list-config.md#defining-a-code-list-configuration-file), [in-line code list](../code-list-config.md#defining-an-in-line-code-list) (json), or link to an externally-defined code list (uri) | true                                                                                            |
| `definition_uri`    | A uri of a resource to show how the column is created/managed (e.g. a uri of a PDF explaining a list of units) (Optional)                                                                                                                                                                             | *none*                                                                                          |
| `cell_uri_template` | **(Advanced)** Override the uri generated for values within the uri (Optional)                                                                                                                                                                                                                        | *none*                                                                                          |
<!-- TODO: uri_override not in schema -->
<!-- | `uri_override`      | Override the uri created automatically for the column (Optional) (Advanced)                                                                                                                                          | `tidy_data.csv#uri_safe_column_header_from_csv`                                  | -->
