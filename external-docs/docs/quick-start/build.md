# Building a CSV-W

This page is designed to help you build a CSV-W from a properly structured CSV file. It assumes that you have already [installed csvcubed](./installation.md) and have [designed your CSV input](./designing-csv.md).

To build a cube from the structured CSV we built in [Designing a CSV](designing-csv.md), we run the [csvcubed build](../guides/command-line/build-command.md) command:

```bash
csvcubed build sweden_at_eurovision_no_missing.csv
```

All being well we get the following output:

> `Build Complete`

This indicates that a cube was created and was written to the [output directory](../guides/command-line/build-command.md#output-directory) (default: `./out`).

## The Files

For our Eurovision example dataset we have the following files:

```bash
out
├── entrant.csv
├── entrant.csv-metadata.json
├── entrant.table.json
├── language.csv
├── language.csv-metadata.json
├── language.table.json
├── song.csv
├── song.csv-metadata.json
├── song.table.json
├── sweden_at_eurovision_no_missing.csv
├── sweden_at_eurovision_no_missing.csv-metadata.json
├── year.csv
├── year.csv-metadata.json
└── year.table.json
```

The key files are:

* `sweden_at_eurovision_no_missing.csv` - contains all of the observations.
* `sweden_at_eurovision_no_missing.csv-metadata.json` - contains metadata describing the structure of your CSV-W cube.
* For each dimension you will have:
    * `<dimension_name>.csv` - a code list containing the unique values of that dimension.
    * `<dimension_name>.table.json` - schema describing the code list CSV.
    * `<dimension_name>.csv-metadata.json` - catalogue metadata describing the code list.

## Passing configuration

So far in the quick start we have not touched on providing explicit configuring telling csvcubed how to convert your data into a CSV-W, but this is coming next. If you do wish to provide a configuration JSON file, you must set the [`--config` / `-c`](../guides/command-line/build-command.md#config---c) option to tell csvcubed where the config file is.

```bash
csvcubed build your-data.csv --config your-configuration.json
```

## Errors

There are a number of errors which can occur when building a CSV-W; most of them are designed to help ensure you get correct and valid outputs.

Please see our documentation explaining a [number of common errors](../guides/errors/index.md) to see what you can do to diagnose and correct any errors which occur.

## Next

The next step is to [describe your CSV](./describing-csv.md).
