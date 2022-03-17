# Working with URIs

## URI safe transformation

The URI safe transformation is a process which converts human-friendly text into an identifier which can be used as part of a URI. It is used to generate URIs to identify code list concepts, new units, new measures and new attribute values.

### The process

| Step                                                                                | Example                                             |
|:------------------------------------------------------------------------------------|:----------------------------------------------------|
| The entire label is converted to lower case                                         | `Potter, Harry!` is transformed to `potter, harry!` |
| Characters which are not letters, numbers, `_` or `/` are replaced with a dash, `-` | `potter, harry!` is transformed to `potter--harry-` |
| Multiple dashes are replaced with single dashes                                     | `potter--harry-` is transformed to `potter-harry-`  |
| A trailing dash is removed if present                                               | `potter-harry-` is transformed to `potter-harry`    |

Once this process is complete, the value is appended on to a URI base to make a full URI, for example `potter-harry` may be appended to `http://example.com/definitions/code-lists/hogwarts-students/` to identify Harry Potter within the list of code list defining Hogwarts students.

> `http://example.com/definitions/code-lists/hogwarts-students/potter-harry`.
