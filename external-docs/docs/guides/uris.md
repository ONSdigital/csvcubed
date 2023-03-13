# Working with URIs

## URI safe transformation

The URI safe transformation is a process which converts human-friendly text into an identifier which can be used as part of a URI. It is used to generate URIs to identify code list concepts, new units, new measures and new attribute values.

### The process

| Step                                                                                | Example                                                   |
|:------------------------------------------------------------------------------------|:----------------------------------------------------------|
| The entire label is converted to lower case                                         | `Picard, Jean-Luc!` is transformed to `picard, jean-luc!` |
| Characters which are not letters, numbers, `_` or `/` are replaced with a dash, `-` | `picard, jean-luc!` is transformed to `picard--jean-luc-` |
| Multiple dashes are replaced with single dashes                                     | `picard--jean-luc-` is transformed to `picard-jean-luc-`  |
| A trailing dash is removed if present                                               | `picard-jean-luc-` is transformed to `picard-jean-luc`    |

Once this process is complete, the value is appended on to a URI base to make a full URI, for example `picard-jean-luc` may be appended to `http://example.com/definitions/code-lists/enterprise-captains/` to identify Jean-Luc Picard within the code list defining Enterprise captains.

> `http://example.com/definitions/code-lists/enterprise-captains/picard-jean-luc`.


## CSV column name safe transformation

The CSV column name safe transformation converts a human-readable column name into an identifier that is safe to use as the `name` property in a CSV-W column.

### The process

| Step                                                                                             | Example                                                                     |
|:-------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------|
| The entire column name is converted to lower case                                                | `USS Enterprise-D personnel` is transformed to `uss enterprise-d personnel` |
| Any characters which are not letters, numbers or `_` (underscore) are replaced with a single `_` | `uss enterprise-d personnel` is transformed to `uss_enterprise_d_personnel` |

The transformed [column name](https://www.w3.org/TR/2015/REC-tabular-metadata-20151217/#column-name) can then be safely used by csvcubed in the generation of CSV-W metadata, such as column definitions:

```json
{
    "@context": "http://www.w3.org/ns/csvw",
    "@id": "starfleet.csv#dataset",
    "tables": [
        {
            "url": "starfleet.csv",
            "tableSchema":{
                "columns": [
                    {
                        "titles": "USS Enterprise-D personnel",
                        "name": "uss_enterprise_d_personnel",
                        ...
                    }
                ]
            }
        }
    ]
}

```
