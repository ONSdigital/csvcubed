# Dimension columns

This page discusses what a dimension column is, when one should be used, and how one can be defined.

> For a detailed look at a dimension column's configuration options, see the [Reference table](#reference) at the bottom
 of this page.

## What is a dimension column?

A dimension column identifies the observations in a data set. In order to be valid, a data cube must include at least
one dimension column; however, in practice, it is likely that your data set will contain more than one dimension.

A combined set of dimension values (including the measure) uniquely identifies each observation in the data set. More
specifically, the combined dimension values identify the sub-set of the population to which the observed value applies.

Examples of dimensions include the time period to which the observation applies, or the geographic region which the
observation covers, as demonstrated in the table below:

| **Year** | **Region** | **Value** |
|:---------|:-----------|:---------:|
| 2020     | England    |   10.6    |
| 2021     | Scotland   |   13.8    |
| 2022     | Wales      |   9.43    |

## When to use one

Dimensions are the fundamental building blocks of your data set, so your data set must always include at least one
dimension.

**If a column groups or identifies a sub-set of the population that your cube describes, then it is a dimension.** Care
should be taken when deciding whether a column represents a dimension or an attribute. Attributes describe the observed
value and **should not** identify a sub-set of your cube's population.

Referring to the table above, `Year` and `Region` are the dimensions that partition the population into sub-sets. That
is, `Year` and `Region` respectively identify the time period and geographic area to which the observed `Value` relates.

## Basic configuration

If you do not provide a column configuration in your `qube-config.json` file for a column, then
[Inferred configuration](../convention.md#inferred-configuration) applies. This means that your column will be
treated as a dimension by default unless it has a [reserved name](../convention.md#conventional-column-names).

If you provide a column mapping for your column, but you do not specify the `type` field, then csvcubed will
automatically assume that your column is a dimension. It is also possible to explicitly set the column as a dimension
by setting the column's `type` field to `dimension`. The following examples are therefore equivalent:

```json
{
   "title": "The title of the cube",
   "description": "A description of the contents of the cube",
   "summary": "A summary of the data set",
   "columns": {
      "Year" {
         "type": "dimension"
      }
}
```

```json
{
   "title": "The title of the cube",
   "description": "A description of the contents of the cube",
   "summary": "A summary of the data set",
   "columns": {
      "Year" {
         "type": "dimension"
      },
      "Region": {
         "type": "dimension"
      }
   }
}
```

This minimal definition results in:

* the `label` field defaulting to the column titles (`Year` and `Region` in this example);
* a `code_list` being automatically generated for each column, containing the column's unique values.

## Label, description and definition

Additional details can be associated with the dimensions in your data set through the `label`, `description` and
`definition_uri` fields.

As mentioned above, the `label` field will default to the column title unless explicitly configured in the
`qube-config.json` file. In the example below, the `Region` label is amended to `Geographic region`:

```json
{ ...
   "columns": {
      "Year" {
         "type": "dimension",
      },
      "Region": {
         "type": "dimension",
         "label": "Geographic region"
      }
   }
}
```

The `description` field can be used to provide a longer description of your dimension. If you want to provide
information about your methodology, the `description` field is the preferred place for this. It also supports the
markdown format.

```json
{ ...
   "columns": {
      "Year" {
         "type": "dimension",
      },
      "Region": {
         "type": "dimension",
         "description": "The geographic region to which the observation relates; uses standard ONS Geography codes"
      }
   }
}
```

The `definition_uri` fields allows you to refer to external resources that further define a dimension's values:

```json
{ ...
   "columns": {
      "Year" {
         "type": "dimension",
      },
      "Region": {
         "type": "dimension",
         "definition_uri": "https://en.wikipedia.org/wiki/ONS_coding_system"
      }
   }
}
```

## Code list configuration

One of the key principles of linked data is the ability to connect data sets via references to common concepts. These
concepts can be formalised through the use of code lists. By default, csvcubed will generate code lists for each of the
dimensions in your data set. However, there are several configuration options for refining how your code lists are
generated and expressed. These are briefly described below - full details can be found on the
[Code list configuration](../code-list-config.md) page.

* Link to an externally-defined code list (URI):
<!-- TODO: Find an actual code list URI -->
   ```json
   { ...
      "columns": {
         "Year" {
            "type": "dimension",
         },
         "Region": {
            "type": "dimension",
            "code_list": "http://statistics.data.gov.uk/data/statistical-geography/code-lists"
         }
      }
   }
   ```

* Use a locally-defined [code-list-config.json](../code-list-config.md#defining-a-code-list-configuration-file):

   ```json
   { ...
      "columns": {
         "Year" {
            "type": "dimension",
         },
         "Region": {
            "type": "dimension",
            "code_list": "regions-code-list-config.json"
         }
      }
   }
   ```

* Define an [in-line code list](../code-list-config.md#defining-an-in-line-code-list):

   ```json
   { ...
      "columns": {
         "Year" {
            "type": "dimension",
         },
         "Region": {
            "type": "dimension",
            "code_list": {
               "title": "Geographic regions",
               "concepts": [
                  {
                     "label": "E92000001",
                     "description": "England"
                  },
                  {
                     "label": "S92000003",
                     "description": "Scotland"
                  },
                  {
                     "label": "W92000004",
                     "description": "Wales"
                  }
               ]
            }
         }
      }
   }
   ```

* Suppress a codelist:

   ```json
   { ...
      "columns": {
         "Year" {
            "type": "dimension",
         },
         "Region": {
            "type": "dimension",
            "code_list": false
         }
      }
   }
   ```
## Dimension column templates

The `Region` column could also be configured by using a [column template](../templates.md) - doing so means that the
`type`, `from_existing`, `label` and `cell_uri_template` fields will be automatically populated based on the
[statistical-geography.json](https://purl.org/csv-cubed/qube-config/templates/statistical-geography.json) template.

```json
{ ...
   "columns": {
      "Year": {
         "type": "dimension"
      }
   },
   "Region": {
      "from_template": "statistical-geography"
   }
}
```

## Inheritance

To reuse or extend an existing dimension, the `from_existing` field can be configured to link to a URI where the
dimension to be reused or extended is defined.

To reuse a parent dimension without making any changes to it, set the `from_existing` field to the URI defining the
dimension to be reused:

```json
{ ...
   "columns": {
      "Year": {
         "type": "dimension",
         "from_existing": "http://purl.org/linked-data/sdmx/2009/dimension#refPeriod"
      }
   }
}
```

To extend a parent dimension and create a new dimension from it, set the `from_existing` field to the URI defining the
dimension to be reused, and set the `label` field to indicate that this is a new child dimension of
`http://purl.org/linked-data/sdmx/2009/dimension#refArea`:

```json
{ ...
   "columns": {
      "Region": {
         "from_existing": "http://purl.org/linked-data/sdmx/2009/dimension#refArea",
         "label": "Geographic region"
      }
   }
}
```

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

The `Song` and `Language` columns have both been configured with a `cell_uri_template` field. It is important to note
that this field should only be used where the concept scheme is defined externally at an existing URI, or there is no
concept scheme, but you want to point to an existing resource to provide additional context about the dimension's value.

If `cell_uri_template` is specified:

**Either**:

- `from_existing` must also be defined, in which case `cell_uri_template` should refer to the concepts in the existing
dimension's code list;

**Or**:

- `code_list` must be set as `false`, in which case `cell_uri_template` should refer to URIs which are existing RDF
resources.

The format of the `cell_uri_template` value **must** follow [RFC6570](https://www.rfc-editor.org/rfc/rfc6570) guidance
for URI Templates. In the case of any doubt, follow the pattern in the examples shown above (e.g. `http://example.org/some-uri/{+column_name}`),
as this will ensure csvcubed safely [transforms the column header](../../uris.md#csv-column-name-safe-transformation)
to the CSV-W format.

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
