# Error - missing uri template name

## When it occurs

You are referencing a column name in a uri template but that column does not exist.

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

is **valid** because `dim_1` is just a correctly formatted variable expressing a column name (i.e `Dim-1` is a column that exists).

Whereas this:

```json
"columns": {
      "Dim-1": {
        "type": "dimension",
        "code_list": true,
        "cell_uri_template": "http://example.com/dimensions/{+i_dont_exist}"
      },
```

is **not** valid, as we're referencing a non existent column.

Alternatively, you can also include [built-in supported special csvw variables](https://www.w3.org/TR/2015/REC-tabular-metadata-20151217/#h-uri-template-properties) in place of a column name variable.

<!-- TODO: Link to somewhere which helps the user define multi-measure dimensions. -->