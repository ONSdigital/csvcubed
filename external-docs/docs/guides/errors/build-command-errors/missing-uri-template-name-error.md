# Error - missing uri template name

## When it occurs

You are referencing a column name in the uri template but that column does not exist.

## How to fix

The columns names in your config directly inform what you can validly reference in your uri templates.

For example, this:

```json
"columns": {
      "Dim-1": {
        "type": "dimension",
        "code_list": true,
        "cell_uri_template": "http://example.com/dimensions/{+dim_1}"
      },
```

is **valid** because `dim_1` is just a correctly formatted variable expressing the column `Dim-1`, i.e it exists.

Whereas this:

```json
"columns": {
      "Dim-1": {
        "type": "dimension",
        "code_list": true,
        "cell_uri_template": "http://example.com/dimensions/{+i-dont-exist}"
      },
```

is **not** valid, as we're referencing a non existent column.


-----

Please note, it is valid to reuse a defined column name variable between columns, so:

```json
"columns": {
      "Dim-1": {
        "type": "dimension",
        "code_list": true,
      },
      "Dim-2": {
        "type": "dimension",
        "code_list": true,
        "cell_uri_template": "http://example.com/dimensions/{+dim_1}"
      },
```

Is a valid configuration.

Upon encountering this error, the message itself will tell you what currently defined column variable names you have in your configuration.


<!-- TODO: Link to somewhere which helps the user define multi-measure dimensions. -->